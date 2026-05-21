from __future__ import annotations

from typing import Dict, List, Optional

from .llm_prompts import build_task_a_prompt
from .preference_axes import extract_preference_axes
from .profile import PsychologicalProfile
from .rating_calibration import RatingCalibration, build_rating_calibration
from .review_generator import generate_review
from .services.profile_service import ProfileService
from .data.schema import InteractionRecord
from .llm_client import OpenAIClient


class TaskAService:
    def __init__(
        self,
        profile_service: Optional[ProfileService] = None,
        llm_client: Optional[OpenAIClient] = None,
    ) -> None:
        self._profile_service = profile_service or ProfileService()
        self._llm_client = llm_client

    def simulate_review(
        self,
        user_id: str,
        records: List[InteractionRecord],
        target_item: Dict[str, object],
        population_records: Optional[List[InteractionRecord]] = None,
        use_llm: bool = False,
    ) -> Dict[str, object]:
        profile = self._profile_service.build_profile_cached(user_id, records)

        if not population_records:
            population_records = records

        calibration = build_rating_calibration(records, population_records)
        base_rating = profile.rating_stats.mean if profile.rating_stats.count else 3.0
        calibrated = calibration.calibrate(base_rating)

        reasoning = _build_reasoning(profile, calibration, calibrated)

        if use_llm and self._llm_client:
            review_text = _generate_review_with_llm(self._llm_client, profile.to_dict(), target_item)
            reasoning += " Review generated via LLM using structured prompt."
        else:
            review_text = generate_review(profile, target_item)

        return {
            "user_id": user_id,
            "target_item": target_item,
            "predicted_rating": calibrated,
            "reasoning": reasoning,
            "review_text": review_text,
        }


def _build_reasoning(
    profile: PsychologicalProfile,
    calibration: RatingCalibration,
    calibrated_rating: float,
) -> str:
    parts: List[str] = []

    # Rating calibration explanation
    if profile.rating_stats.count:
        direction = "upward" if calibrated_rating > profile.rating_stats.mean else "downward"
        if abs(calibrated_rating - profile.rating_stats.mean) < 0.05:
            direction = "unchanged"
        parts.append(
            f"User mean rating is {profile.rating_stats.mean:.2f} "
            f"(σ={profile.rating_stats.std_dev:.2f}, n={profile.rating_stats.count}); "
            f"calibrated {direction} to {calibrated_rating:.2f} against population "
            f"mean {calibration.population_mean:.2f}."
        )
    else:
        parts.append(f"No rating history; defaulted to population mean {calibrated_rating:.2f}.")

    # Top value axes
    axes = extract_preference_axes(profile)
    value_axes = [a for a in axes if a.name not in ("rating_bias", "cultural_register")]
    if value_axes:
        top = value_axes[:2]
        axis_str = ", ".join(f"{a.name} (w={a.weight:.2f})" for a in top)
        parts.append(f"Top preference axes: {axis_str}.")

    # Trajectory drift
    traj = profile.trajectory
    if abs(traj.delta_rating) >= 0.3:
        direction = "improved" if traj.delta_rating > 0 else "declined"
        parts.append(
            f"Rating trajectory has {direction} by {abs(traj.delta_rating):.2f} "
            f"(early avg {traj.early_mean_rating:.2f} → recent {traj.recent_mean_rating:.2f})."
        )

    # Stylometry signal
    sty = profile.stylometry
    if sty.avg_word_count > 0:
        parts.append(
            f"Review style: ~{sty.avg_word_count:.0f} words, "
            f"vocab richness {sty.vocab_richness:.2f}."
        )

    # Cultural register
    cs = profile.cultural_signals
    if cs.code_switching_detected:
        parts.append(
            f"Nigerian English detected (index={cs.nigerian_english_index:.2f}, "
            f"pidgin hits={cs.pidgin_term_hits}); cultural register applied."
        )

    return " ".join(parts)


def _generate_review_with_llm(
    client: OpenAIClient,
    profile: Dict[str, object],
    target_item: Dict[str, object],
) -> str:
    messages = build_task_a_prompt(profile, target_item)
    response = client.chat_completion(messages, temperature=0.2)
    choices = response.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    return str(message.get("content", "")).strip()
