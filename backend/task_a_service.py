from __future__ import annotations

from typing import Dict, List, Optional

from .rating_calibration import build_rating_calibration
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

        reasoning = "Rating derived from user mean with calibration."

        if use_llm and self._llm_client:
            review_text = _generate_review_with_llm(self._llm_client, profile.to_dict(), target_item)
            reasoning = "Rating derived from calibration; review generated via LLM."
        else:
            review_text = generate_review(profile, target_item)

        return {
            "user_id": user_id,
            "target_item": target_item,
            "predicted_rating": calibrated,
            "reasoning": reasoning,
            "review_text": review_text,
        }


def _generate_review_with_llm(
    client: OpenAIClient,
    profile: Dict[str, object],
    target_item: Dict[str, object],
) -> str:
    messages = [
        {
            "role": "system",
            "content": "Write a short review in the user's voice based on the profile.",
        },
        {
            "role": "user",
            "content": f"Profile: {profile}\nItem: {target_item}",
        },
    ]

    response = client.chat_completion(messages, temperature=0.2)
    choices = response.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    return str(message.get("content", "")).strip()
