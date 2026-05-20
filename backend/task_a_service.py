from __future__ import annotations

from typing import Dict, List, Optional

from .rating_calibration import build_rating_calibration
from .services.profile_service import ProfileService
from .data.schema import InteractionRecord


class TaskAService:
    def __init__(self, profile_service: Optional[ProfileService] = None) -> None:
        self._profile_service = profile_service or ProfileService()

    def simulate_review(
        self,
        user_id: str,
        records: List[InteractionRecord],
        target_item: Dict[str, object],
        population_records: Optional[List[InteractionRecord]] = None,
    ) -> Dict[str, object]:
        profile = self._profile_service.build_profile_cached(user_id, records)

        if not population_records:
            population_records = records

        calibration = build_rating_calibration(records, population_records)
        base_rating = profile.rating_stats.mean if profile.rating_stats.count else 3.0
        calibrated = calibration.calibrate(base_rating)

        return {
            "user_id": user_id,
            "target_item": target_item,
            "predicted_rating": calibrated,
            "reasoning": "Rating derived from user mean with calibration.",
            "review_text": "(stub) Review generation will be added in Phase 4.",
        }
