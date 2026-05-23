#!/usr/bin/env python3
"""
Persona — Yelp multi-checkpoint vector store ingestion.

Single pass through the Yelp review JSONL:
  - Embeds reviews in batches (sentence-transformers all-MiniLM-L6-v2)
  - Saves checkpoint JSONL stores at 50k, 100k, 150k, 200k to:
      /tmp/persona_checkpoints/yelp_50k.jsonl  (etc.)
  - Streams live progress to stdout and a clean log file
  - Ctrl+C saves a partial store before exit

Usage (from repo root):
    python ingest_checkpoints.py 2>&1 | tee /tmp/persona_checkpoints/ingest.log

Monitor in another terminal:
    tail -f /tmp/persona_checkpoints/ingest.log
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import sys
import time
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = Path(__file__).parent
DATASET_PATH = REPO_ROOT / "backend/data/yelp_raw/yelp_academic_dataset_review.json"
OUTPUT_DIR   = Path("/tmp/persona_checkpoints")
LOG_PATH     = OUTPUT_DIR / "ingest.log"

CHECKPOINTS  = [50_000, 100_000, 150_000, 200_000]
TOTAL_TARGET = CHECKPOINTS[-1]
BATCH_SIZE   = 512
MODEL_NAME   = "all-MiniLM-L6-v2"

TEXT_FIELD      = "text"
ID_FIELD        = "business_id"
METADATA_FIELDS = ["name", "categories", "stars"]

MILESTONE_EVERY = 10_000   # write a full timestamped line to log every N records

# ── Helpers ────────────────────────────────────────────────────────────────────

def fmt_bytes(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def fmt_time(s: float) -> str:
    m, s = divmod(int(s), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def fmt_eta(elapsed: float, done: int, total: int) -> str:
    if done == 0 or elapsed < 1:
        return "--:--"
    remaining = max(0, total - done) / (done / elapsed)
    return fmt_time(remaining)

def fmt_rate(elapsed: float, done: int) -> str:
    if elapsed < 0.5 or done == 0:
        return "  --/s"
    return f"{done/elapsed:>5.0f}/s"

def disk_free_str() -> str:
    return fmt_bytes(shutil.disk_usage("/tmp").free)

def pbar(done: int, total: int, w: int = 38) -> str:
    filled = int(min(done / total, 1.0) * w)
    return "█" * filled + "░" * (w - filled)

# ── Output (stdout + log file) ─────────────────────────────────────────────────

_log_fh = None

def _open_log():
    global _log_fh
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _log_fh = open(LOG_PATH, "a", encoding="utf-8", buffering=1)

def out(msg: str):
    """Write a line to stdout and to the log file."""
    print(msg, flush=True)
    if _log_fh:
        _log_fh.write(msg + "\n")
        _log_fh.flush()

def progress(msg: str):
    """Overwrite the current terminal line; write nothing to log (log uses milestones instead)."""
    print(f"\r{msg}", end="", flush=True)

def milestone(msg: str):
    """Write a timestamped milestone line to stdout (with newline) and to log."""
    ts = time.strftime("%H:%M:%S")
    full = f"[{ts}] {msg}"
    print(f"\n{full}", flush=True)
    if _log_fh:
        _log_fh.write(full + "\n")
        _log_fh.flush()

# ── Ingestion ──────────────────────────────────────────────────────────────────

def embed_batch(model, embed_fn, store, batch: list[dict]) -> int:
    """Embed a batch and add items to store. Returns count of items added."""
    texts   = [r.get(TEXT_FIELD, "") for r in batch]
    vectors = embed_fn(model, texts)
    added = 0
    for record, vec in zip(batch, vectors):
        item_id = str(record.get(ID_FIELD, "")).strip()
        if not item_id:
            continue
        store.add(item_id=item_id, vector=vec,
                  metadata={f: record.get(f) for f in METADATA_FIELDS})
        added += 1
    return added


def save_checkpoint(store, path: Path, count: int) -> int:
    """Stream-write the store to disk. Returns file size in bytes."""
    from backend.vector_store_persist import save_vector_store
    t = time.time()
    save_vector_store(store, str(path))
    dur = time.time() - t
    size = path.stat().st_size
    out(f"  │  File     : {path}")
    out(f"  │  Items    : {count:,}")
    out(f"  │  Size     : {fmt_bytes(size)}")
    out(f"  │  Save time: {dur:.1f}s")
    out(f"  │  /tmp free: {disk_free_str()}")
    return size


def run():
    _open_log()

    out("=" * 68)
    out("  Persona — Yelp Multi-Checkpoint Ingestion")
    out("=" * 68)
    out(f"  Dataset  : {DATASET_PATH}")
    out(f"  Output   : {OUTPUT_DIR}/")
    out(f"  Targets  : {', '.join(f'{c//1000}k' for c in CHECKPOINTS)}")
    out(f"  Batch    : {BATCH_SIZE}  |  Model: {MODEL_NAME}")
    out(f"  Log file : {LOG_PATH}")
    out(f"  /tmp free: {disk_free_str()}")
    out("=" * 68)
    out("")

    # ── Import backend modules ─────────────────────────────────────────────────
    sys.path.insert(0, str(REPO_ROOT))
    from backend.embeddings import embed_texts, load_embedding_model
    from backend.vector_store import InMemoryVectorStore

    out("Loading embedding model (may download on first run) …")
    t0 = time.time()
    model = load_embedding_model(MODEL_NAME)
    out(f"Model ready in {time.time() - t0:.1f}s\n")

    store = InMemoryVectorStore(items=[])
    checkpoints_saved: list[tuple[str, int, int]] = []  # (path, count, bytes)
    cp_idx      = 0
    total       = 0
    skipped     = 0
    batch: list[dict] = []
    start       = time.time()
    last_ms     = 0   # last milestone boundary logged

    # ── Ctrl+C handler ─────────────────────────────────────────────────────────
    interrupted = False
    def on_interrupt(sig, frame):
        nonlocal interrupted
        interrupted = True
        print()   # newline after \r progress line
        out(f"\n[INTERRUPTED] Saving partial store ({total:,} records) …")
        if total > 0:
            from backend.vector_store_persist import save_vector_store
            partial = OUTPUT_DIR / f"yelp_{total}rec_partial.jsonl"
            save_vector_store(store, str(partial))
            size = partial.stat().st_size
            out(f"  Saved: {partial} ({fmt_bytes(size)})")
        out("Exiting.")
        sys.exit(0)

    signal.signal(signal.SIGINT, on_interrupt)

    # ── Main streaming loop ────────────────────────────────────────────────────
    out("Streaming and embedding …\n")

    with open(DATASET_PATH, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            if total >= TOTAL_TARGET:
                break

            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                batch.append(json.loads(raw_line))
            except json.JSONDecodeError:
                skipped += 1
                continue

            if len(batch) < BATCH_SIZE:
                continue

            # Embed this batch
            total += embed_batch(model, embed_texts, store, batch)
            batch = []
            elapsed = time.time() - start

            # ── Live progress bar (terminal only) ──────────────────────────────
            bar = pbar(total, TOTAL_TARGET)
            pct = (total / TOTAL_TARGET) * 100
            progress(
                f"  [{bar}] {pct:5.1f}%  "
                f"{total:>7,}/{TOTAL_TARGET:,}  "
                f"{fmt_rate(elapsed, total)}  "
                f"ETA {fmt_eta(elapsed, total, TOTAL_TARGET)}  "
                f"[{fmt_time(elapsed)}]"
            )

            # ── Milestone log line (every 10k, goes to log file too) ───────────
            ms_boundary = (total // MILESTONE_EVERY) * MILESTONE_EVERY
            if ms_boundary > last_ms and ms_boundary >= MILESTONE_EVERY:
                last_ms = ms_boundary
                milestone(
                    f"{total:>7,} / {TOTAL_TARGET:,} records  "
                    f"{fmt_rate(elapsed, total)}  "
                    f"ETA {fmt_eta(elapsed, total, TOTAL_TARGET)}  "
                    f"/tmp free {disk_free_str()}"
                )

            # ── Checkpoint ─────────────────────────────────────────────────────
            if cp_idx < len(CHECKPOINTS) and total >= CHECKPOINTS[cp_idx]:
                label = CHECKPOINTS[cp_idx] // 1000
                ts = time.strftime("%H:%M:%S")
                out(f"\n  ┌─ CHECKPOINT {label}k  [{ts}]  {'─'*38}")
                size = save_checkpoint(
                    store, OUTPUT_DIR / f"yelp_{label}k.jsonl", total
                )
                out(f"  └{'─'*60}\n")
                checkpoints_saved.append((f"yelp_{label}k.jsonl", total, size))
                cp_idx += 1
                if total < TOTAL_TARGET:
                    out("Continuing …\n")

    # ── Flush any partial final batch ──────────────────────────────────────────
    if batch:
        total += embed_batch(model, embed_texts, store, batch)
        batch = []
        print()

    # Final checkpoint in case last batch pushed us over the boundary
    if cp_idx < len(CHECKPOINTS) and total >= CHECKPOINTS[cp_idx]:
        label = CHECKPOINTS[cp_idx] // 1000
        out(f"\n  ┌─ CHECKPOINT {label}k  ['─'*38]")
        size = save_checkpoint(store, OUTPUT_DIR / f"yelp_{label}k.jsonl", total)
        out(f"  └{'─'*60}\n")
        checkpoints_saved.append((f"yelp_{label}k.jsonl", total, size))

    # ── Summary ────────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    out("\n" + "=" * 68)
    out(f"  COMPLETE")
    out(f"  Records   : {total:,}  (skipped {skipped:,} bad lines)")
    out(f"  Total time: {fmt_time(elapsed)}")
    out(f"  Avg rate  : {fmt_rate(elapsed, total)}")
    out("=" * 68)
    out("  Checkpoint files (all in /tmp/persona_checkpoints/):")
    for fname, count, size in checkpoints_saved:
        out(f"    {fname:<22}  {count:>7,} items  {fmt_bytes(size)}")
    out("")
    out("  Copy to your data directory:")
    out("    cp /tmp/persona_checkpoints/yelp_200k.jsonl \\")
    out("       /workspaces/Persona/backend/data/yelp_vector_store_200k.jsonl")
    out("")
    out("  Then set in .env:")
    out("    VECTOR_STORE_PATH=/workspaces/Persona/backend/data/yelp_vector_store_200k.jsonl")
    out("=" * 68 + "\n")


if __name__ == "__main__":
    run()
