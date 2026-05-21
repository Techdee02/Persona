"""
Session state for multi-turn Task B recommendations.

A session accumulates:
  - previously recommended item IDs (excluded from future results)
  - user-expressed constraints (e.g., "vegetarian", "budget")
  - turn count

Sessions are keyed by session_id and expire after TTL_SECONDS.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


TTL_SECONDS: int = 3600
_MAX_SESSIONS: int = 10_000


@dataclass
class SessionState:
    session_id: str
    user_id: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    excluded_ids: Set[str] = field(default_factory=set)
    constraints: Dict[str, object] = field(default_factory=dict)
    turn: int = 0

    def touch(self) -> None:
        self.last_accessed = time.time()

    def is_expired(self, ttl: int = TTL_SECONDS) -> bool:
        return (time.time() - self.last_accessed) > ttl

    def record_recommendations(self, item_ids: List[str]) -> None:
        self.excluded_ids.update(item_ids)
        self.turn += 1
        self.touch()

    def apply_constraints(self, new_constraints: Dict[str, object]) -> None:
        self.constraints.update(new_constraints)
        self.touch()

    def context_summary(self) -> str:
        parts = [f"Turn {self.turn}."]
        if self.excluded_ids:
            parts.append(
                f"Already recommended: {', '.join(sorted(self.excluded_ids)[:10])}"
                + (" (and more)" if len(self.excluded_ids) > 10 else "") + "."
            )
        if self.constraints:
            cstr = "; ".join(f"{k}={v}" for k, v in self.constraints.items())
            parts.append(f"Active constraints: {cstr}.")
        return " ".join(parts)


class SessionStore:
    """Thread-safe in-memory session store with LRU eviction."""

    def __init__(self, ttl: int = TTL_SECONDS, max_size: int = _MAX_SESSIONS) -> None:
        self._sessions: Dict[str, SessionState] = {}
        self._ttl = ttl
        self._max_size = max_size

    def create(self, user_id: str, session_id: Optional[str] = None) -> SessionState:
        self._evict()
        sid = session_id or str(uuid.uuid4())
        state = SessionState(session_id=sid, user_id=user_id)
        self._sessions[sid] = state
        return state

    def get(self, session_id: str) -> Optional[SessionState]:
        state = self._sessions.get(session_id)
        if state is None:
            return None
        if state.is_expired(self._ttl):
            del self._sessions[session_id]
            return None
        state.touch()
        return state

    def get_or_create(self, user_id: str, session_id: Optional[str]) -> SessionState:
        if session_id:
            existing = self.get(session_id)
            if existing:
                return existing
        return self.create(user_id, session_id=session_id)

    def delete(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def _evict(self) -> None:
        # Remove expired sessions first.
        expired = [sid for sid, s in self._sessions.items() if s.is_expired(self._ttl)]
        for sid in expired:
            del self._sessions[sid]
        # If still over capacity, evict oldest by last_accessed.
        if len(self._sessions) >= self._max_size:
            oldest = sorted(self._sessions.items(), key=lambda kv: kv[1].last_accessed)
            for sid, _ in oldest[: len(self._sessions) - self._max_size + 1]:
                del self._sessions[sid]

    @property
    def active_count(self) -> int:
        return sum(1 for s in self._sessions.values() if not s.is_expired(self._ttl))


# Module-level singleton used by app.py
session_store = SessionStore()
