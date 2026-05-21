"""
Task A evaluation runner.

Usage:
    python -m backend.evaluation.task_a_eval \
        --records  data/user_records.jsonl \
        --split    0.8

    # With BERTScore (requires bert-score package):
    python -m backend.evaluation.task_a_eval \
        --records  data/user_records.jsonl \
        --split    0.8 \
        --bertscore

Each JSONL line must have: user_id, item_id, rating, review_text, timestamp, source.
The script performs a per-user temporal split, predicts ratings + reviews for the
test set, and reports RMSE (vs mean-rating baseline) and ROUGE-L.

Includes per-user breakdown by history length and cultural signal presence.
"""
from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from ..data.schema import InteractionRecord
from ..data.split import temporal_split
from ..profile import build_profile
from ..rating_calibration import build_rating_calibration
from ..review_generator import generate_review
from .metrics import mean_rating_baseline, rmse, rouge_l_corpus

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("persona.eval.task_a")

_HISTORY_BUCKETS = [("sparse", 1, 5), ("medium", 6, 20), ("dense", 21, int(1e9))]


def _bucket(n: int) -> str:
    for label, lo, hi in _HISTORY_BUCKETS:
        if lo <= n <= hi:
            return label
    return "dense"


def _mean(vals: List[float]) -> float:
    return round(sum(vals) / len(vals), 4) if vals else 0.0


def _try_bertscore(hypotheses: List[str], references: List[str]) -> float:
    try:
        from bert_score import score as bert_score  # type: ignore
        _, _, f1 = bert_score(hypotheses, references, lang="en", verbose=False)
        return round(float(f1.mean().item()), 4)
    except ImportError:
        logger.warning("bert-score not installed; skipping BERTScore computation")
        return 0.0


def evaluate(
    records: List[InteractionRecord],
    train_ratio: float = 0.8,
    compute_bertscore: bool = False,
) -> Dict[str, object]:
    train, test = temporal_split(records, train_ratio=train_ratio)
    if not test:
        raise ValueError("Test split is empty — reduce train_ratio or add more records")

    train_by_user: Dict[str, List[InteractionRecord]] = {}
    for rec in train:
        train_by_user.setdefault(rec.user_id, []).append(rec)

    all_ratings = [r.rating for r in train]
    global_mean = mean_rating_baseline(all_ratings)

    predicted: List[float] = []
    baseline: List[float] = []
    ground_truth_ratings: List[float] = []
    generated_reviews: List[str] = []
    reference_reviews: List[str] = []

    # Per-bucket accumulators
    bucket_rmse_pred: Dict[str, List[float]] = defaultdict(list)
    bucket_rmse_gt:   Dict[str, List[float]] = defaultdict(list)
    cultural_pred:    List[float] = []
    cultural_gt:      List[float] = []
    noncultural_pred: List[float] = []
    noncultural_gt:   List[float] = []

    for rec in test:
        user_records = train_by_user.get(rec.user_id, [])
        ground_truth_ratings.append(rec.rating)
        baseline.append(global_mean)

        if user_records:
            profile = build_profile(rec.user_id, user_records)
            calibration = build_rating_calibration(user_records, train)
            pred = calibration.calibrate(profile.rating_stats.mean)
            generated_reviews.append(generate_review(profile, {"name": rec.item_id}))

            bkt = _bucket(len(user_records))
            bucket_rmse_pred[bkt].append(pred)
            bucket_rmse_gt[bkt].append(rec.rating)

            if profile.cultural_signals.code_switching_detected:
                cultural_pred.append(pred)
                cultural_gt.append(rec.rating)
            else:
                noncultural_pred.append(pred)
                noncultural_gt.append(rec.rating)
        else:
            pred = global_mean
            generated_reviews.append("")

        predicted.append(pred)
        if rec.review_text:
            reference_reviews.append(rec.review_text)

    persona_rmse = rmse(predicted, ground_truth_ratings)
    baseline_rmse = rmse(baseline, ground_truth_ratings)

    pairs = [(g, r) for g, r in zip(generated_reviews, reference_reviews) if g and r]
    avg_rouge = rouge_l_corpus([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else 0.0

    results: Dict[str, object] = {
        "test_size": len(test),
        "persona_rmse": round(persona_rmse, 4),
        "baseline_rmse": round(baseline_rmse, 4),
        "rmse_improvement": round(baseline_rmse - persona_rmse, 4),
        "rouge_l": round(avg_rouge, 4),
        "breakdown": {
            "by_history_length": {
                label: {
                    "rmse": round(rmse(bucket_rmse_pred[label], bucket_rmse_gt[label]), 4)
                            if bucket_rmse_pred[label] else None,
                    "users": len(bucket_rmse_pred[label]),
                }
                for label in ("sparse", "medium", "dense")
            },
            "by_cultural_signal": {
                "with_nigerian_english": {
                    "rmse": round(rmse(cultural_pred, cultural_gt), 4) if cultural_pred else None,
                    "users": len(cultural_pred),
                },
                "without_nigerian_english": {
                    "rmse": round(rmse(noncultural_pred, noncultural_gt), 4) if noncultural_pred else None,
                    "users": len(noncultural_pred),
                },
            },
        },
    }

    if compute_bertscore and pairs:
        results["bert_score_f1"] = _try_bertscore(
            [p[0] for p in pairs], [p[1] for p in pairs]
        )

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
    parser = argparse.ArgumentParser(description="Task A evaluation")
    parser.add_argument("--records", required=True, help="JSONL file of interaction records")
    parser.add_argument("--split", type=float, default=0.8, help="Train ratio (default 0.8)")
    parser.add_argument("--bertscore", action="store_true", help="Compute BERTScore F1 (requires bert-score)")
    args = parser.parse_args()

    records = _load_jsonl(args.records)
    logger.info("Loaded %d records", len(records))

    results = evaluate(records, train_ratio=args.split, compute_bertscore=args.bertscore)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
