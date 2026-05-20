from __future__ import annotations

import hashlib
import json
from typing import Iterable, List, Optional

from ..cache import TTLCache
from ..config import app_config_from_env
from ..data.schema import InteractionRecord
from ..profile import PsychologicalProfile, build_profile


class ProfileService:
    def __init__(self, cache: Optional[TTLCache[str, PsychologicalProfile]] = None) -> None:
        config = app_config_from_env()
        self._cache = cache or TTLCache(
            max_size=config.profile_cache_max_size,
            ttl_seconds=config.profile_cache_ttl_seconds,
        )

    def build_profile_cached(
        self, user_id: str, records: List[InteractionRecord]
    ) -> PsychologicalProfile:
        cache_key = _hash_profile_input(user_id, records)
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        profile = build_profile(user_id, records)
        self._cache.set(cache_key, profile)
        return profile

    def cache_size(self) -> int:
        return self._cache.size()


def _hash_profile_input(user_id: str, records: Iterable[InteractionRecord]) -> str:
    payload = {
        "user_id": user_id,
        "records": [
            {
                "item_id": record.item_id,
                "rating": record.rating,
                "review_text": record.review_text,
                "timestamp": record.timestamp,
                "source": record.source,
            }
            for record in records
        ],
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return digest
