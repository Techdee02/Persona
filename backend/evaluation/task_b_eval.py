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
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Set

from ..data.schema import InteractionRecord
from ..data.split import temporal_split
from ..profile import build_profile
from ..preference_axes import extract_preference_axes
from ..deliberative_scoring import deliberative_score
from ..retrieval import RetrievalResult
from ..vector_store_persist import load_vector_store
from ..embeddings import embed_texts, load_embedding_model
from .metrics import hit_rate_at_k, ndcg_at_k, popularity_baseline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("persona.eval.task_b")


def evaluate(
    records: List[InteractionRecord],
    store_path: str,
    k: int = 10,
    train_ratio: float = 0.8,
    model_name: str = "all-MiniLM-L6-v2",
) -> Dict[str, float]:
    train, test = temporal_split(records, train_ratio=train_ratio)
    if not test:
        raise ValueError("Test split is empty")

    store = load_vector_store(store_path)
    embedding_model = load_embedding_model(model_name)

    train_by_user: Dict[str, List[InteractionRecord]] = {}
    for rec in train:
        train_by_user.setdefault(rec.user_id, []).append(rec)

    # Ground-truth: items each user interacted with in the test set.
    test_items_by_user: Dict[str, Set[str]] = {}
    for rec in test:
        test_items_by_user.setdefault(rec.user_id, set()).add(rec.item_id)

    # Popularity baseline: item frequency in training set.
    item_counts: Dict[str, int] = {}
    for rec in train:
        item_counts[rec.item_id] = item_counts.get(rec.item_id, 0) + 1

    persona_ndcg: List[float] = []
    persona_hr: List[float] = []
    baseline_ndcg: List[float] = []
    baseline_hr: List[float] = []

    pop_baseline = popularity_baseline(item_counts, k=k)

    for user_id, relevant in test_items_by_user.items():
        user_records = train_by_user.get(user_id, [])
        if not user_records:
            continue

        profile = build_profile(user_id, user_records)
        axes = extract_preference_axes(profile)

        # Use the user's most recent review text as the query.
        query_text = user_records[-1].review_text or user_id
        query_vector = embed_texts(embedding_model, [query_text])[0]

        raw_results = store.query(query_vector, top_k=k)
        candidates = [
            RetrievalResult(item_id=r.item_id, score=r.score, metadata=r.metadata)
            for r in raw_results
        ]
        scored = deliberative_score(candidates, axes)
        ranked = [item.item_id for item in scored]

        persona_ndcg.append(ndcg_at_k(ranked, relevant, k=k))
        persona_hr.append(hit_rate_at_k(ranked, relevant, k=k))
        baseline_ndcg.append(ndcg_at_k(pop_baseline, relevant, k=k))
        baseline_hr.append(hit_rate_at_k(pop_baseline, relevant, k=k))

    def _mean(vals: List[float]) -> float:
        return round(sum(vals) / len(vals), 4) if vals else 0.0

    results = {
        "evaluated_users": len(persona_ndcg),
        "k": k,
        "persona_ndcg": _mean(persona_ndcg),
        "baseline_ndcg": _mean(baseline_ndcg),
        "ndcg_improvement": round(_mean(persona_ndcg) - _mean(baseline_ndcg), 4),
        "persona_hit_rate": _mean(persona_hr),
        "baseline_hit_rate": _mean(baseline_hr),
    }
    return results


def _load_jsonl(path: str) -> List[InteractionRecord]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        records.append(
            InteractionRecord(
                user_id=str(row.get("user_id", "")),
                item_id=str(row.get("item_id", "")),
                rating=float(row.get("rating", 0.0)),
                review_text=str(row.get("review_text", "")),
                timestamp=str(row.get("timestamp", "")) or None,
                source=str(row.get("source", "unknown")),
            )
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Task B evaluation")
    parser.add_argument("--records", required=True, help="JSONL file of interaction records")
    parser.add_argument("--store",   required=True, help="Path to persisted vector store JSON")
    parser.add_argument("--k",       type=int, default=10)
    parser.add_argument("--split",   type=float, default=0.8)
    args = parser.parse_args()

    records = _load_jsonl(args.records)
    logger.info("Loaded %d records", len(records))

    results = evaluate(records, store_path=args.store, k=args.k, train_ratio=args.split)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
