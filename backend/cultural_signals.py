from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .data.schema import InteractionRecord


_WORD_RE = re.compile(r"[A-Za-z']+")

_PIDGIN_TERMS = {
    "abeg",
    "abi",
    "dey",
    "na",
    "oga",
    "sef",
    "sha",
    "wahala",
    "jollof",
    "suya",
    "wah",
    "omo",
}


@dataclass(frozen=True)
class CulturalSignals:
    nigerian_english_index: float
    code_switching_detected: bool
    pidgin_term_hits: int


def extract_cultural_signals(records: Iterable[InteractionRecord]) -> CulturalSignals:
    words = []
    for record in records:
        if record.review_text:
            words.extend(_WORD_RE.findall(record.review_text.lower()))

    if not words:
        return CulturalSignals(
            nigerian_english_index=0.0,
            code_switching_detected=False,
            pidgin_term_hits=0,
        )

    pidgin_hits = sum(1 for word in words if word in _PIDGIN_TERMS)
    nigerian_index = pidgin_hits / max(1, len(words))

    return CulturalSignals(
        nigerian_english_index=nigerian_index,
        code_switching_detected=pidgin_hits > 0,
        pidgin_term_hits=pidgin_hits,
    )
