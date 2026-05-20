from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

from .data.schema import InteractionRecord
from .signal_extraction import (
    RatingStats,
    StylometryStats,
    extract_rating_stats,
    extract_stylometry,
    extract_value_keywords,
)


@dataclass(frozen=True)
class PsychologicalProfile:
    user_id: str
    rating_stats: RatingStats
    stylometry: StylometryStats
    value_keywords: Dict[str, int]

    def to_dict(self) -> Dict[str, object]:
        return {
            "user_id": self.user_id,
            "rating_stats": asdict(self.rating_stats),
            "stylometry": asdict(self.stylometry),
            "value_keywords": self.value_keywords,
        }


def build_profile(user_id: str, records: list[InteractionRecord]) -> PsychologicalProfile:
    rating_stats = extract_rating_stats(records)
    stylometry = extract_stylometry(records)
    value_keywords = extract_value_keywords(records)

    return PsychologicalProfile(
        user_id=user_id,
        rating_stats=rating_stats,
        stylometry=stylometry,
        value_keywords=value_keywords,
    )
