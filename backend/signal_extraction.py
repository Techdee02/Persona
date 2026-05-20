from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from statistics import mean, pstdev
import re
from typing import Dict, Iterable, List

from .data.schema import InteractionRecord


_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_RE = re.compile(r"[.!?]+")


@dataclass(frozen=True)
class RatingStats:
    count: int
    mean: float
    std_dev: float
    min_rating: float
    max_rating: float


@dataclass(frozen=True)
class StylometryStats:
    avg_review_length: float
    avg_word_count: float
    vocab_richness: float
    avg_sentence_length: float


def extract_rating_stats(records: Iterable[InteractionRecord]) -> RatingStats:
    ratings = [record.rating for record in records]
    if not ratings:
        return RatingStats(count=0, mean=0.0, std_dev=0.0, min_rating=0.0, max_rating=0.0)

    return RatingStats(
        count=len(ratings),
        mean=mean(ratings),
        std_dev=pstdev(ratings) if len(ratings) > 1 else 0.0,
        min_rating=min(ratings),
        max_rating=max(ratings),
    )


def extract_stylometry(records: Iterable[InteractionRecord]) -> StylometryStats:
    texts = [record.review_text for record in records if record.review_text]
    if not texts:
        return StylometryStats(
            avg_review_length=0.0,
            avg_word_count=0.0,
            vocab_richness=0.0,
            avg_sentence_length=0.0,
        )

    word_counts: List[int] = []
    sentence_lengths: List[float] = []
    vocab_counter: Counter[str] = Counter()
    total_words = 0

    for text in texts:
        words = _WORD_RE.findall(text)
        word_counts.append(len(words))
        total_words += len(words)
        vocab_counter.update([w.lower() for w in words])

        sentence_count = max(1, len(_SENTENCE_RE.findall(text)))
        sentence_lengths.append(len(words) / sentence_count if words else 0.0)

    vocab_richness = (len(vocab_counter) / total_words) if total_words else 0.0

    return StylometryStats(
        avg_review_length=mean([len(text) for text in texts]),
        avg_word_count=mean(word_counts),
        vocab_richness=vocab_richness,
        avg_sentence_length=mean(sentence_lengths),
    )


def extract_value_keywords(records: Iterable[InteractionRecord]) -> Dict[str, int]:
    keywords = {
        "food": {"food", "taste", "flavor", "fresh", "spicy", "grill"},
        "service": {"service", "staff", "wait", "server", "attentive"},
        "price": {"price", "cheap", "expensive", "value", "cost"},
        "atmosphere": {"ambience", "atmosphere", "music", "decor", "vibe"},
    }

    counts = {category: 0 for category in keywords}
    for record in records:
        text = record.review_text.lower() if record.review_text else ""
        words = set(_WORD_RE.findall(text))
        for category, terms in keywords.items():
            if words.intersection(terms):
                counts[category] += 1

    return counts
