from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import time
from typing import Generic, Hashable, Optional, TypeVar


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


@dataclass
class CacheEntry(Generic[V]):
    value: V
    expires_at: float


class TTLCache(Generic[K, V]):
    def __init__(self, max_size: int, ttl_seconds: int) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._max_size = max_size
        self._ttl_seconds = ttl_seconds
        self._store: OrderedDict[K, CacheEntry[V]] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        now = time.time()
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at < now:
            self._store.pop(key, None)
            return None

        self._store.move_to_end(key)
        return entry.value

    def set(self, key: K, value: V) -> None:
        now = time.time()
        expires_at = now + self._ttl_seconds
        self._store[key] = CacheEntry(value=value, expires_at=expires_at)
        self._store.move_to_end(key)

        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def size(self) -> int:
        self._purge_expired()
        return len(self._store)

    def _purge_expired(self) -> None:
        now = time.time()
        expired_keys = [key for key, entry in self._store.items() if entry.expires_at < now]
        for key in expired_keys:
            self._store.pop(key, None)
