from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from .deliberative_scoring import deliberative_score
from .preference_axes import extract_preference_axes
from .retrieval import RetrievalItem, RetrievalResult, multi_angle_retrieve
from .vector_store_service import VectorStoreService
from .services.profile_service import ProfileService
from .data.schema import InteractionRecord


class TaskBService:
    def __init__(
        self,
        profile_service: Optional[ProfileService] = None,
        vector_store_service: Optional[VectorStoreService] = None,
    ) -> None:
        self._profile_service = profile_service or ProfileService()
        self._vector_store_service = vector_store_service

    def recommend(
        self,
        user_id: str,
        records: List[InteractionRecord],
        query_vectors: List[np.ndarray],
        candidates: List[RetrievalItem],
        top_k: int = 10,
        weights: Optional[List[float]] = None,
        penalties: Optional[Dict[str, float]] = None,
        query_text: Optional[str] = None,
    ) -> Dict[str, object]:
        profile = self._profile_service.build_profile_cached(user_id, records)
        axes = extract_preference_axes(profile)

        if self._vector_store_service and query_text:
            # Vector store already returns items ranked by embedding similarity;
            # skip the vector-based multi_angle_retrieve and use results directly.
            retrieved_items = self._vector_store_service.query(query_text, top_k=top_k)
            retrieved = [
                RetrievalResult(
                    item_id=item["item_id"],
                    score=item["score"],
                    metadata=item.get("metadata", {}),
                )
                for item in retrieved_items
            ]
        else:
            retrieved = multi_angle_retrieve(
                candidates,
                query_vectors=query_vectors,
                top_k=top_k,
                weights=weights,
            )

        scored = deliberative_score(retrieved, axes, penalties=penalties)

        return {
            "user_id": user_id,
            "axes": [axis.__dict__ for axis in axes],
            "recommendations": [
                {
                    "item_id": item.item_id,
                    "score": item.score,
                    "explanation": item.explanation,
                    "metadata": item.metadata,
                }
                for item in scored
            ],
        }
