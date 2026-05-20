from backend.data.schema import InteractionRecord
from backend.signal_extraction import (
    extract_rating_stats,
    extract_stylometry,
    extract_value_keywords,
)


def _record(rating: float, text: str) -> InteractionRecord:
    return InteractionRecord(
        user_id="u1",
        item_id="i1",
        rating=rating,
        review_text=text,
        timestamp="2021-01-01",
        source="yelp",
    )


def test_extract_rating_stats():
    stats = extract_rating_stats([_record(4.0, ""), _record(2.0, "")])
    assert stats.count == 2
    assert stats.mean == 3.0
    assert stats.min_rating == 2.0
    assert stats.max_rating == 4.0


def test_extract_stylometry():
    stats = extract_stylometry([_record(5.0, "Great food. Nice vibe!")])
    assert stats.avg_word_count > 0
    assert stats.vocab_richness > 0
    assert stats.avg_sentence_length > 0


def test_extract_value_keywords():
    counts = extract_value_keywords([
        _record(5.0, "Great food and friendly staff"),
        _record(2.0, "Too expensive for the service"),
    ])
    assert counts["food"] == 1
    assert counts["service"] == 2
    assert counts["price"] == 1
