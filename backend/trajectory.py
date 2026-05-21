from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from .data.schema import InteractionRecord
from .data.split import timestamp_key


@dataclass(frozen=True)
class TrajectoryStats:
    early_mean_rating: float
    recent_mean_rating: float
    delta_rating: float
    early_avg_review_length: float
    recent_avg_review_length: float
    delta_review_length: float


def extract_trajectory(records: Iterable[InteractionRecord]) -> TrajectoryStats:
    ordered = sorted(records, key=timestamp_key)
    if len(ordered) < 4:
        return TrajectoryStats(
            early_mean_rating=0.0,
            recent_mean_rating=0.0,
            delta_rating=0.0,
            early_avg_review_length=0.0,
            recent_avg_review_length=0.0,
            delta_review_length=0.0,
        )

    mid = len(ordered) // 2
    early = ordered[:mid]
    recent = ordered[mid:]

    early_mean = mean([record.rating for record in early])
    recent_mean = mean([record.rating for record in recent])

    early_lengths = [_review_length(record) for record in early]
    recent_lengths = [_review_length(record) for record in recent]

    early_len = mean(early_lengths) if early_lengths else 0.0
    recent_len = mean(recent_lengths) if recent_lengths else 0.0

    return TrajectoryStats(
        early_mean_rating=early_mean,
        recent_mean_rating=recent_mean,
        delta_rating=recent_mean - early_mean,
        early_avg_review_length=early_len,
        recent_avg_review_length=recent_len,
        delta_review_length=recent_len - early_len,
    )


def _review_length(record: InteractionRecord) -> int:
    return len(record.review_text) if record.review_text else 0
