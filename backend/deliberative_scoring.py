from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .preference_axes import PreferenceAxis
from .retrieval import RetrievalResult


@dataclass(frozen=True)
class ScoredRecommendation:
    item_id: str
    score: float
    explanation: str
    metadata: Dict[str, object]


def deliberative_score(
    candidates: List[RetrievalResult],
    axes: List[PreferenceAxis],
    penalties: Dict[str, float] | None = None,
) -> List[ScoredRecommendation]:
    penalties = penalties or {}
    scored: List[ScoredRecommendation] = []

    for candidate in candidates:
        axis_score = sum(axis.weight for axis in axes)
        penalty_score = sum(penalties.values())
        final_score = candidate.score + axis_score - penalty_score

        explanation = _build_explanation(candidate, axes, penalties)
        scored.append(
            ScoredRecommendation(
                item_id=candidate.item_id,
                score=final_score,
                explanation=explanation,
                metadata=candidate.metadata,
            )
        )

    return sorted(scored, key=lambda item: item.score, reverse=True)


def _build_explanation(
    candidate: RetrievalResult,
    axes: List[PreferenceAxis],
    penalties: Dict[str, float],
) -> str:
    axis_notes = ", ".join([axis.name for axis in axes[:3]])
    penalty_notes = ", ".join(penalties.keys())

    parts = [f"Similarity score {candidate.score:.2f}"]
    if axis_notes:
        parts.append(f"Matched axes: {axis_notes}")
    if penalty_notes:
        parts.append(f"Conflicts: {penalty_notes}")

    return "; ".join(parts)
