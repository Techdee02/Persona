"""
Ablation study runner.

Zeroes out one profile layer at a time and re-runs Task A and Task B
evaluation to measure the contribution of each layer.

Usage:
    python -m backend.evaluation.ablation \
        --records  data/records.jsonl \
        --store    data/vector_store.json \
        --split    0.8 \
        --k        10

Output: JSON object with per-layer RMSE, ROUGE-L, NDCG@k and delta vs full model.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

from ..cultural_signals import CulturalSignals
from ..data.schema import InteractionRecord
from ..data.split import temporal_split
from ..profile import PsychologicalProfile, build_profile
from ..rating_calibration import build_rating_calibration
from ..review_generator import generate_review
from ..signal_extraction import RatingStats, StylometryStats
from ..trajectory import TrajectoryStats
from .metrics import mean_rating_baseline, rmse, rouge_l_corpus
from .task_b_eval import evaluate as task_b_evaluate

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("persona.eval.ablation")


# ── Layer zeroing helpers ─────────────────────────────────────────────────────

_ZERO_RATING_STATS = RatingStats(count=0, mean=3.0, std_dev=0.0,
                                 min_rating=3.0, max_rating=3.0)
_ZERO_STYLOMETRY = StylometryStats(avg_review_length=0.0, avg_word_count=0.0,
                                   vocab_richness=0.0, avg_sentence_length=0.0)
_ZERO_TRAJECTORY = TrajectoryStats(early_mean_rating=0.0, recent_mean_rating=0.0,
                                   delta_rating=0.0, early_avg_review_length=0.0,
                                   recent_avg_review_length=0.0, delta_review_length=0.0)
_ZERO_CULTURAL = CulturalSignals(nigerian_english_index=0.0,
                                 code_switching_detected=False,
                                 pidgin_term_hits=0)
_ZERO_VALUE_KW: Dict[str, int] = {"food": 0, "service": 0, "price": 0, "atmosphere": 0}

_ABLATION_LAYERS = {
    "rating_stats":      lambda p: _replace(p, rating_stats=_ZERO_RATING_STATS),
    "stylometry":        lambda p: _replace(p, stylometry=_ZERO_STYLOMETRY),
    "value_keywords":    lambda p: _replace(p, value_keywords=_ZERO_VALUE_KW),
    "trajectory":        lambda p: _replace(p, trajectory=_ZERO_TRAJECTORY),
    "cultural_signals":  lambda p: _replace(p, cultural_signals=_ZERO_CULTURAL),
}


def _replace(profile: PsychologicalProfile, **overrides) -> PsychologicalProfile:
    return PsychologicalProfile(
        user_id=profile.user_id,
        rating_stats=overrides.get("rating_stats", profile.rating_stats),
        stylometry=overrides.get("stylometry", profile.stylometry),
        value_keywords=overrides.get("value_keywords", profile.value_keywords),
        trajectory=overrides.get("trajectory", profile.trajectory),
        cultural_signals=overrides.get("cultural_signals", profile.cultural_signals),
    )


# ── Task A ablation ───────────────────────────────────────────────────────────

def _task_a_metrics(
    train: List[InteractionRecord],
    test: List[InteractionRecord],
    ablate_layer: str | None = None,
) -> Dict[str, float]:
    train_by_user: Dict[str, List[InteractionRecord]] = {}
    for rec in train:
        train_by_user.setdefault(rec.user_id, []).append(rec)

    all_ratings = [r.rating for r in train]
    global_mean = mean_rating_baseline(all_ratings)

    predicted, ground_truth, generated, references = [], [], [], []

    for rec in test:
        user_records = train_by_user.get(rec.user_id, [])
        ground_truth.append(rec.rating)

        if user_records:
            profile = build_profile(rec.user_id, user_records)
            if ablate_layer:
                profile = _ABLATION_LAYERS[ablate_layer](profile)
            calibration = build_rating_calibration(user_records, train)
            pred = calibration.calibrate(profile.rating_stats.mean)
            generated.append(generate_review(profile, {"name": rec.item_id}, seed=0))
        else:
            pred = global_mean
            generated.append("")

        predicted.append(pred)
        if rec.review_text:
            references.append(rec.review_text)

    pairs = [(g, r) for g, r in zip(generated, references) if g and r]
    avg_rouge = rouge_l_corpus([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else 0.0

    return {
        "rmse": round(rmse(predicted, ground_truth), 4),
        "rouge_l": round(avg_rouge, 4),
    }


# ── Main ablation loop ────────────────────────────────────────────────────────

def run_ablation(
    records: List[InteractionRecord],
    store_path: str,
    k: int = 10,
    train_ratio: float = 0.8,
) -> Dict[str, object]:
    train, test = temporal_split(records, train_ratio=train_ratio)
    if not test:
        raise ValueError("Test split is empty")

    # Full model baseline.
    full_a = _task_a_metrics(train, test)
    full_b = task_b_evaluate(records, store_path=store_path, k=k, train_ratio=train_ratio)

    results: Dict[str, object] = {
        "full_model": {
            "task_a": full_a,
            "task_b": {
                "ndcg": full_b["persona_ndcg"],
                "hit_rate": full_b["persona_hit_rate"],
            },
        },
        "ablations": {},
    }

    for layer_name in _ABLATION_LAYERS:
        logger.info("Ablating layer: %s", layer_name)

        ablated_a = _task_a_metrics(train, test, ablate_layer=layer_name)
        ablated_b = task_b_evaluate(
            records, store_path=store_path, k=k,
            train_ratio=train_ratio, ablate_layer=layer_name,
        )

        results["ablations"][layer_name] = {
            "task_a": ablated_a,
            "task_a_delta": {
                "rmse_delta":   round(ablated_a["rmse"]   - full_a["rmse"],   4),
                "rouge_l_delta":round(ablated_a["rouge_l"] - full_a["rouge_l"], 4),
            },
            "task_b": {
                "ndcg":     ablated_b["persona_ndcg"],
                "hit_rate": ablated_b["persona_hit_rate"],
            },
            "task_b_delta": {
                "ndcg_delta":     round(ablated_b["persona_ndcg"]      - full_b["persona_ndcg"],      4),
                "hit_rate_delta": round(ablated_b["persona_hit_rate"]  - full_b["persona_hit_rate"],  4),
            },
        }

    return results


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
    parser = argparse.ArgumentParser(description="Persona ablation study")
    parser.add_argument("--records", required=True)
    parser.add_argument("--store",   required=True)
    parser.add_argument("--k",       type=int,   default=10)
    parser.add_argument("--split",   type=float, default=0.8)
    args = parser.parse_args()

    records = _load_jsonl(args.records)
    logger.info("Loaded %d records", len(records))

    results = run_ablation(records, store_path=args.store, k=args.k, train_ratio=args.split)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
