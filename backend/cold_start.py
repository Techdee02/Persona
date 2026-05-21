from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .cultural_signals import CulturalSignals
from .profile import PsychologicalProfile
from .signal_extraction import RatingStats, StylometryStats
from .trajectory import TrajectoryStats

# Fixed elicitation questions presented to new users.
COLD_START_QUESTIONS: List[Dict[str, object]] = [
    {
        "id": "rating_tendency",
        "question": (
            "When you enjoy something, do you typically give top marks (5 stars), "
            "or do you reserve those for truly exceptional experiences?"
        ),
        "options": ["top_marks", "reserve_top"],
    },
    {
        "id": "value_priority",
        "question": "When reviewing a place or product, what matters most to you?",
        "options": ["food_quality", "service", "price_value", "atmosphere"],
    },
    {
        "id": "review_style",
        "question": "How would you describe your review writing style?",
        "options": ["brief_and_direct", "detailed_and_thorough"],
    },
    {
        "id": "cultural_register",
        "question": "Do you sometimes use Nigerian or local expressions in your reviews?",
        "options": ["yes_often", "sometimes", "rarely"],
    },
]

# question_id → answer → signal overrides applied to the bootstrapped profile.
_SIGNAL_MAP: Dict[str, Dict[str, Dict[str, object]]] = {
    "rating_tendency": {
        "top_marks":    {"mean": 4.5, "std_dev": 0.5},
        "reserve_top":  {"mean": 3.5, "std_dev": 0.8},
    },
    "value_priority": {
        "food_quality": {"food": 3, "service": 0, "price": 0, "atmosphere": 0},
        "service":      {"food": 0, "service": 3, "price": 0, "atmosphere": 0},
        "price_value":  {"food": 0, "service": 0, "price": 3, "atmosphere": 0},
        "atmosphere":   {"food": 0, "service": 0, "price": 0, "atmosphere": 3},
    },
    "review_style": {
        "brief_and_direct":     {"avg_review_length": 80.0,  "avg_word_count": 16.0},
        "detailed_and_thorough": {"avg_review_length": 300.0, "avg_word_count": 60.0},
    },
    "cultural_register": {
        "yes_often":  {"nigerian_english_index": 0.06, "code_switching_detected": True, "pidgin_term_hits": 5},
        "sometimes":  {"nigerian_english_index": 0.02, "code_switching_detected": True, "pidgin_term_hits": 1},
        "rarely":     {"nigerian_english_index": 0.0,  "code_switching_detected": False, "pidgin_term_hits": 0},
    },
}


@dataclass(frozen=True)
class ColdStartAnswer:
    question_id: str
    answer: str


def bootstrap_profile(user_id: str, answers: List[ColdStartAnswer]) -> PsychologicalProfile:
    """Build a thin PsychologicalProfile from cold-start elicitation answers."""
    rating_overrides: Dict[str, float] = {}
    value_keywords: Dict[str, int] = {"food": 0, "service": 0, "price": 0, "atmosphere": 0}
    stylometry_overrides: Dict[str, float] = {}
    cultural_overrides: Dict[str, object] = {}

    for ans in answers:
        signals = _SIGNAL_MAP.get(ans.question_id, {}).get(ans.answer, {})

        if ans.question_id == "rating_tendency":
            rating_overrides.update(signals)
        elif ans.question_id == "value_priority":
            for k, v in signals.items():
                value_keywords[k] = int(v)
        elif ans.question_id == "review_style":
            stylometry_overrides.update(signals)
        elif ans.question_id == "cultural_register":
            cultural_overrides.update(signals)

    mean_rating = float(rating_overrides.get("mean", 3.5))
    std_dev = float(rating_overrides.get("std_dev", 0.8))

    return PsychologicalProfile(
        user_id=user_id,
        rating_stats=RatingStats(
            count=0,
            mean=mean_rating,
            std_dev=std_dev,
            min_rating=max(1.0, mean_rating - std_dev),
            max_rating=min(5.0, mean_rating + std_dev),
        ),
        stylometry=StylometryStats(
            avg_review_length=float(stylometry_overrides.get("avg_review_length", 150.0)),
            avg_word_count=float(stylometry_overrides.get("avg_word_count", 30.0)),
            vocab_richness=0.5,
            avg_sentence_length=float(stylometry_overrides.get("avg_word_count", 30.0)) / 3.0,
        ),
        value_keywords=value_keywords,
        trajectory=TrajectoryStats(
            early_mean_rating=0.0,
            recent_mean_rating=0.0,
            delta_rating=0.0,
            early_avg_review_length=0.0,
            recent_avg_review_length=0.0,
            delta_review_length=0.0,
        ),
        cultural_signals=CulturalSignals(
            nigerian_english_index=float(cultural_overrides.get("nigerian_english_index", 0.0)),
            code_switching_detected=bool(cultural_overrides.get("code_switching_detected", False)),
            pidgin_term_hits=int(cultural_overrides.get("pidgin_term_hits", 0)),
        ),
    )
