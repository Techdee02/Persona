#!/usr/bin/env python3
"""
Enrich the Yelp vector store with business metadata from raw review data.

For each business_id in the vector store, finds the matching reviews in the
raw Yelp review JSONL and adds:
  - metadata.name        : first 80 chars of the highest-rated review for that business
  - metadata.stars       : average star rating across all reviews for that business
  - metadata.review_count: number of reviews seen in the dataset

The embeddings are unchanged — only metadata is updated.

Usage (from repo root):
    python -m backend.enrich_vector_store
    # or
    python backend/enrich_vector_store.py
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
logger = logging.getLogger("enrich")

REPO_ROOT    = Path(__file__).parent.parent
REVIEW_PATH  = REPO_ROOT / "backend/data/yelp_raw/yelp_academic_dataset_review.json"
STORE_PATH   = REPO_ROOT / "backend/data/yelp_vector_store_200k.jsonl"
# Write to /tmp (has 97 GB free) to avoid filling /workspaces (only 3 GB free)
OUTPUT_PATH  = Path("/tmp/yelp_vector_store_200k_enriched.jsonl")

PREVIEW_LEN  = 80   # chars of review text used as the display label


def build_business_lookup() -> dict:
    """
    Stream the raw Yelp review JSONL once.

    For each business_id keep the text snippet of its highest-rated review
    (tie-break: first seen) plus a running average star rating.
    """
    logger.info("Reading raw reviews from %s …", REVIEW_PATH)
    lookup: dict[str, dict] = {}
    count = 0
    t0 = time.time()

    with REVIEW_PATH.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            biz_id = record.get("business_id", "").strip()
            stars  = float(record.get("stars", 0))
            text   = record.get("text", "").replace("\n", " ").strip()

            if biz_id not in lookup:
                preview = text[:PREVIEW_LEN] + ("…" if len(text) > PREVIEW_LEN else "")
                lookup[biz_id] = {
                    "preview": preview,
                    "best_stars": stars,
                    "stars_sum": stars,
                    "count": 1,
                }
            else:
                entry = lookup[biz_id]
                entry["stars_sum"] += stars
                entry["count"] += 1
                # Upgrade preview to the highest-rated review's text
                if stars > entry["best_stars"]:
                    entry["best_stars"] = stars
                    entry["preview"] = text[:PREVIEW_LEN] + ("…" if len(text) > PREVIEW_LEN else "")

            count += 1
            if count % 500_000 == 0:
                logger.info(
                    "  %d reviews processed, %d unique businesses  (%.0fs)",
                    count, len(lookup), time.time() - t0,
                )

    logger.info(
        "Lookup built: %d reviews → %d unique businesses  (%.0fs)",
        count, len(lookup), time.time() - t0,
    )
    return lookup


def enrich_store(lookup: dict) -> None:
    """
    Stream the vector store JSONL, enrich metadata, write to OUTPUT_PATH.
    Then atomically replace the original.
    """
    logger.info("Enriching %s …", STORE_PATH)
    t0 = time.time()
    total = 0
    enriched = 0

    with STORE_PATH.open("r", encoding="utf-8") as fin, \
         OUTPUT_PATH.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)

            biz_id = item.get("item_id", "")
            if biz_id in lookup:
                entry = lookup[biz_id]
                avg_stars = entry["stars_sum"] / entry["count"]
                item["metadata"]["name"]         = entry["preview"]
                item["metadata"]["stars"]        = round(avg_stars, 1)
                item["metadata"]["review_count"] = entry["count"]
                enriched += 1

            fout.write(json.dumps(item, separators=(",", ":")) + "\n")
            total += 1
            if total % 50_000 == 0:
                logger.info("  %d / 200k items  (%d enriched)  (%.0fs)", total, enriched, time.time() - t0)

    logger.info("Enrichment done: %d / %d items enriched  (%.0fs)", enriched, total, time.time() - t0)

    # Replace original: delete first (frees space on /workspaces), then move from /tmp
    logger.info("Replacing original: deleting %s …", STORE_PATH)
    STORE_PATH.unlink()
    logger.info("Moving enriched from /tmp → %s …", STORE_PATH)
    shutil.move(str(OUTPUT_PATH), str(STORE_PATH))
    logger.info("Done. Enriched store is now at %s", STORE_PATH)


if __name__ == "__main__":
    if not REVIEW_PATH.exists():
        logger.error("Raw review file not found: %s", REVIEW_PATH)
        raise SystemExit(1)
    if not STORE_PATH.exists():
        logger.error("Vector store not found: %s", STORE_PATH)
        raise SystemExit(1)

    lookup = build_business_lookup()
    enrich_store(lookup)
    logger.info("All done. Restart the API to pick up the enriched store.")
