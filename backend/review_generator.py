from __future__ import annotations

import random
from typing import Dict, List, Optional

from .profile import PsychologicalProfile

# Sentiment buckets keyed by rounded mean rating.
_OPENERS: Dict[str, List[str]] = {
    "positive": [
        "Really enjoyed this experience.",
        "Definitely worth it.",
        "Came in with high hopes and they were met.",
        "Can't complain at all.",
    ],
    "neutral": [
        "Decent overall.",
        "Nothing spectacular but nothing terrible either.",
        "It was okay.",
        "Does what it says on the tin.",
    ],
    "negative": [
        "Honestly a bit disappointed.",
        "Expected better.",
        "Not sure I'd rush back.",
        "Left feeling underwhelmed.",
    ],
}

_VALUE_PHRASES: Dict[str, Dict[str, List[str]]] = {
    "food": {
        "positive": ["The food was the highlight.", "Really tasty and well-prepared.", "Flavours were on point."],
        "neutral":  ["The food was alright.", "Nothing wrong with the menu.", "Food was serviceable."],
        "negative": ["Food was average at best.", "The kitchen has room to improve."],
    },
    "service": {
        "positive": ["Staff were attentive and warm.", "Service was prompt and friendly."],
        "neutral":  ["Service was fine, nothing to write home about.", "Staff were okay."],
        "negative": ["Service left a lot to be desired.", "Staff could be more attentive."],
    },
    "price": {
        "positive": ["Great value for money.", "Pricing is fair and reasonable."],
        "neutral":  ["Prices are about right for what you get.", "Neither cheap nor expensive."],
        "negative": ["Felt a bit overpriced for what was delivered.", "Not worth the price tag."],
    },
    "atmosphere": {
        "positive": ["The vibe was excellent.", "Great atmosphere — would come back just for that."],
        "neutral":  ["Atmosphere was okay.", "Nothing special about the setting."],
        "negative": ["The atmosphere was a bit off.", "Setting could use some work."],
    },
}

_PIDGIN_CLOSERS = [
    "Abeg, try am yourself and see.",
    "Na so e be sha.",
    "Omo, e get as e be.",
]

_STANDARD_CLOSERS = [
    "Would recommend.",
    "Might return if in the area.",
    "Wouldn't go out of my way to revisit.",
]


def _sentiment(mean: float) -> str:
    if mean >= 4.0:
        return "positive"
    if mean >= 2.5:
        return "neutral"
    return "negative"


def generate_review(
    profile: PsychologicalProfile,
    target_item: Dict[str, object],
    seed: Optional[int] = None,
) -> str:
    rng = random.Random(seed)
    sentiment = _sentiment(profile.rating_stats.mean)

    parts: List[str] = [rng.choice(_OPENERS[sentiment])]

    # Add a sentence for each value category the user cares about, highest first.
    top_values = sorted(
        ((k, v) for k, v in profile.value_keywords.items() if v > 0),
        key=lambda kv: kv[1],
        reverse=True,
    )
    for category, _ in top_values[:2]:
        phrases = _VALUE_PHRASES.get(category, {}).get(sentiment, [])
        if phrases:
            parts.append(rng.choice(phrases))

    # Item-specific mention when name is available.
    item_name = str(target_item.get("name", target_item.get("title", ""))).strip()
    if item_name:
        if sentiment == "positive":
            parts.append(f"{item_name} delivered what I was looking for.")
        elif sentiment == "negative":
            parts.append(f"{item_name} did not quite meet expectations.")

    # Cultural closing.
    if profile.cultural_signals.code_switching_detected:
        parts.append(rng.choice(_PIDGIN_CLOSERS))
    else:
        parts.append(rng.choice(_STANDARD_CLOSERS))

    # Trim or pad to match the user's average review length.
    review = " ".join(parts)
    target_len = int(profile.stylometry.avg_review_length)
    if target_len > 0 and len(review) > target_len * 1.5:
        review = review[: int(target_len * 1.5)].rsplit(" ", 1)[0] + "."

    return review
