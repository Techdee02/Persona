"""
Task B evaluation runner.

Usage:
    python -m backend.evaluation.task_b_eval \
        --records     data/user_records.jsonl \
        --store       data/vector_store.json \
        --k           10

For each test-split user the script queries the vector store using the
user's profile and measures NDCG@k and Hit Rate@k against their held-out
interactions as the ground-truth relevant set.

Includes per-user breakdown by history length and cultural signal presence.
"""
from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from ..cultural_signals import CulturalSignals
from ..data.schema import InteractionRecord
from ..data.split import temporal_split
from ..deliberative_scoring import deliberative_score
from ..embeddings import embed_texts, load_embedding_model
from ..preference_axes import extract_preference_axes
from ..profile import PsychologicalProfile, build_profile
from ..retrieval import RetrievalResult
from ..signal_extraction import RatingStats, StylometryStats
from ..trajectory import TrajectoryStats
from ..vector_store_persist import load_vector_store
from .metrics import hit_rate_at_k, ndcg_at_k, popularity_baseline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("persona.eval.task_b")

# History-length buckets for breakdown.
_HISTORY_BUCKETS = [("sparse", 1, 5), ("medium", 6, 20), ("dense", 21, int(1e9))]

# Ablation zeroing helpers (imported by ablation.py via this module's evaluate()).
_ZERO_RATING_STATS = RatingStats(count=0, mean=3.0, std_dev=0.0,
                                 min_rating=3.0, max_rating=3.0)
_ZERO_STYLOMETRY = StylometryStats(avg_review_length=0.0, avg_word_count=0.0,
                                   vocab_richness=0.0, avg_sentence_length=0.0)
_ZERO_TRAJECTORY = TrajectoryStats(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
_ZERO_CULTURAL = CulturalSignals(0.0, False, 0)
_ZERO_VALUE_KW: Dict[str, int] = {"food": 0, "service": 0, "price": 0, "atmosphere": 0}

_ABLATION_LAYERS: Dict[str, Callable[[PsychologicalProfile], PsychologicalProfile]] = {
    "rating_stats":    lambda p: _zero(p, rating_stats=_ZERO_RATING_STATS),
    "stylometry":      lambda p: _zero(p, stylometry=_ZERO_STYLOMETRY),
    "value_keywords":  lambda p: _zero(p, value_keywords=_ZERO_VALUE_KW),
    "trajectory":      lambda p: _zero(p, trajectory=_ZERO_TRAJECTORY),
    "cultural_signals":lambda p: _zero(p, cultural_signals=_ZERO_CULTURAL),
}


def _zero(p: PsychologicalProfile, **kw) -> PsychologicalProfile:
    return PsychologicalProfile(
        user_id=p.user_id,
        rating_stats=kw.get("rating_stats", p.rating_stats),
        stylometry=kw.get("stylometry", p.stylometry),
        value_keywords=kw.get("value_keywords", p.value_keywords),
        trajectory=kw.get("trajectory", p.trajectory),
        cultural_signals=kw.get("cultural_signals", p.cultural_signals),
    )


def _bucket(n: int) -> str:
    for label, lo, hi in _HISTORY_BUCKETS:
        if lo <= n <= hi:
            return label
    return "dense"


def _mean(vals: List[float]) -> float:
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def evaluate(
    records: List[InteractionRecord],
    store_path: str,
    k: int = 10,
    train_ratio: float = 0.8,
    model_name: str = "all-MiniLM-L6-v2",
    ablate_layer: Optional[str] = None,
) -> Dict[str, object]:
    train, test = temporal_split(records, train_ratio=train_ratio)
    if not test:
        raise ValueError("Test split is empty")

    store = load_vector_store(store_path)
    embedding_model = load_embedding_model(model_name)

    train_by_user: Dict[str, List[InteractionRecord]] = {}
    for rec in train:
        train_by_user.setdefault(rec.user_id, []).append(rec)

    test_items_by_user: Dict[str, Set[str]] = {}
    for rec in test:
        test_items_by_user.setdefault(rec.user_id, set()).add(rec.item_id)

    item_counts: Dict[str, int] = {}
    for rec in train:
        item_counts[rec.item_id] = item_counts.get(rec.item_id, 0) + 1

    pop_baseline = popularity_baseline(item_counts, k=k)

    persona_ndcg: List[float] = []
    persona_hr:   List[float] = []
    baseline_ndcg: List[float] = []
    baseline_hr:   List[float] = []

    # Per-bucket accumulators.
    bucket_ndcg: Dict[str, List[float]] = defaultdict(list)
    bucket_hr:   Dict[str, List[float]] = defaultdict(list)
    cultural_ndcg:     List[float] = []
    noncultural_ndcg:  List[float] = []

    for user_id, relevant in test_items_by_user.items():
        user_records = train_by_user.get(user_id, [])
        if not user_records:
            continue

        profile = build_profile(user_id, user_records)
        if ablate_layer and ablate_layer in _ABLATION_LAYERS:
            profile = _ABLATION_LAYERS[ablate_layer](profile)

        axes = extract_preference_axes(profile)
        query_text = user_records[-1].review_text or user_id
        query_vector = embed_texts(embedding_model, [query_text])[0]

        raw = store.query(query_vector, top_k=k)
        candidates = [RetrievalResult(item_id=r.item_id, score=r.score,
                                      metadata=r.metadata) for r in raw]
        scored = deliberative_score(candidates, axes)
        ranked = [item.item_id for item in scored]

        n = ndcg_at_k(ranked, relevant, k=k)
        h = hit_rate_at_k(ranked, relevant, k=k)
        bn = ndcg_at_k(pop_baseline, relevant, k=k)
        bh = hit_rate_at_k(pop_baseline, relevant, k=k)

        persona_ndcg.append(n);  persona_hr.append(h)
        baseline_ndcg.append(bn); baseline_hr.append(bh)

        bucket = _bucket(len(user_records))
        bucket_ndcg[bucket].append(n)
        bucket_hr[bucket].append(h)

        if profile.cultural_signals.code_switching_detected:
            cultural_ndcg.append(n)
        else:
            noncultural_ndcg.append(n)

    return {
        "evaluated_users": len(persona_ndcg),
        "k": k,
        "persona_ndcg":      _mean(persona_ndcg),
        "baseline_ndcg":     _mean(baseline_ndcg),
        "ndcg_improvement":  round(_mean(persona_ndcg) - _mean(baseline_ndcg), 4),
        "persona_hit_rate":  _mean(persona_hr),
        "baseline_hit_rate": _mean(baseline_hr),
        "breakdown": {
            "by_history_length": {
                label: {"ndcg": _mean(bucket_ndcg[label]),
                        "hit_rate": _mean(bucket_hr[label]),
                        "users": len(bucket_ndcg[label])}
                for label in ("sparse", "medium", "dense")
            },
            "by_cultural_signal": {
                "with_nigerian_english":    {"ndcg": _mean(cultural_ndcg),    "users": len(cultural_ndcg)},
                "without_nigerian_english": {"ndcg": _mean(noncultural_ndcg), "users": len(noncultural_ndcg)},
            },
        },
    }


def _load_jsonl(path: str) -> List[InteractionRecord]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        records.append(InteractionRecord(
            user_id=str(row.get("user_id", "")),
            item_id=str(row.get("item_id", "")),
            rating=float(row.get("rating", 0.0)),
            review_text=str(row.get("review_text", "")),
            timestamp=str(row.get("timestamp", "")) or None,
            source=str(row.get("source", "unknown")),
        ))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Task B evaluation")
    parser.add_argument("--records", required=True)
    parser.add_argument("--store",   required=True)
    parser.add_argument("--k",       type=int,   default=10)
    parser.add_argument("--split",   type=float, default=0.8)
    args = parser.parse_args()

    records = _load_jsonl(args.records)
    logger.info("Loaded %d records", len(records))
    results = evaluate(records, store_path=args.store, k=args.k, train_ratio=args.split)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
