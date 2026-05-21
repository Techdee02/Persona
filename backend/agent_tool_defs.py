from __future__ import annotations

from typing import Dict, List

import numpy as np

from .agent_tools import ToolRegistry
from .data.schema import InteractionRecord
from .deliberative_scoring import deliberative_score
from .preference_axes import PreferenceAxis, extract_preference_axes
from .retrieval import RetrievalItem, multi_angle_retrieve
from .services.profile_service import ProfileService


def build_tool_registry(profile_service: ProfileService) -> ToolRegistry:
    registry = ToolRegistry()

    registry.register("build_profile", lambda args: _build_profile(profile_service, args))
    registry.register("extract_axes", _extract_axes)
    registry.register("retrieve_candidates", _retrieve_candidates)
    registry.register("score_candidates", _score_candidates)

    return registry


def _build_profile(profile_service: ProfileService, args: Dict[str, object]) -> Dict[str, object]:
    user_id = str(args.get("user_id", "")).strip()
    records = _parse_records(args.get("records", []), user_id)
    profile = profile_service.build_profile_cached(user_id, records)
    return profile.to_dict()


def _extract_axes(args: Dict[str, object]) -> Dict[str, object]:
    profile = args["profile"]
    axes = extract_preference_axes(profile)
    return {"axes": [axis.__dict__ for axis in axes]}


def _retrieve_candidates(args: Dict[str, object]) -> Dict[str, object]:
    items = [
        RetrievalItem(
            item_id=str(item.get("item_id", "")).strip(),
            vector=np.array(item.get("vector", []), dtype=float),
            metadata=item.get("metadata", {}),
        )
        for item in args.get("candidates", [])
    ]
    query_vectors = [np.array(vec, dtype=float) for vec in args.get("query_vectors", [])]
    top_k = int(args.get("top_k", 10))
    weights = args.get("weights", None)

    retrieved = multi_angle_retrieve(items, query_vectors=query_vectors, top_k=top_k, weights=weights)
    return {"retrieved": [result.__dict__ for result in retrieved]}


def _score_candidates(args: Dict[str, object]) -> Dict[str, object]:
    # axes may arrive as a plain list or wrapped in the extract_axes output dict.
    axes_raw = args.get("axes", [])
    if isinstance(axes_raw, dict):
        axes_raw = axes_raw.get("axes", [])
    axes = [PreferenceAxis(**ax) if isinstance(ax, dict) else ax for ax in axes_raw]

    penalties = args.get("penalties", None)
    candidates = args.get("candidates", [])

    scored = deliberative_score(candidates, axes, penalties=penalties)
    return {"scored": [item.__dict__ for item in scored]}


def _parse_records(raw_records: List[Dict[str, object]], user_id: str) -> List[InteractionRecord]:
    parsed = []
    for record in raw_records:
        parsed.append(
            InteractionRecord(
                user_id=user_id,
                item_id=str(record.get("item_id", "")).strip(),
                rating=float(record.get("rating", 0.0)),
                review_text=str(record.get("review_text", "")).strip(),
                timestamp=str(record.get("timestamp", "")).strip() or None,
                source=str(record.get("source", "")).strip() or "unknown",
            )
        )
    return parsed
