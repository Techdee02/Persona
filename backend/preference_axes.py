from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .profile import PsychologicalProfile


@dataclass(frozen=True)
class PreferenceAxis:
    name: str
    rationale: str
    weight: float


def extract_preference_axes(profile: PsychologicalProfile) -> List[PreferenceAxis]:
    axes: List[PreferenceAxis] = []

    value_keywords = profile.value_keywords
    total_mentions = sum(value_keywords.values())
    if total_mentions > 0:
        for name, count in value_keywords.items():
            weight = count / total_mentions
            if weight == 0:
                continue
            axes.append(
                PreferenceAxis(
                    name=name,
                    rationale=f"Mentions {name} in {count} reviews",
                    weight=weight,
                )
            )

    rating_bias = profile.rating_stats.mean - 3.0
    if abs(rating_bias) >= 0.5:
        bias_label = "generous" if rating_bias > 0 else "harsh"
        axes.append(
            PreferenceAxis(
                name="rating_bias",
                rationale=f"Average rating {profile.rating_stats.mean:.2f} indicates a {bias_label} rater",
                weight=min(abs(rating_bias) / 2.0, 1.0),
            )
        )

    if profile.cultural_signals.code_switching_detected:
        axes.append(
            PreferenceAxis(
                name="cultural_register",
                rationale="Code-switching detected in reviews",
                weight=min(profile.cultural_signals.nigerian_english_index * 10, 1.0),
            )
        )

    return sorted(axes, key=lambda axis: axis.weight, reverse=True)
