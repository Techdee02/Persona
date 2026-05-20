from backend.data.schema import InteractionRecord
from backend.profile import build_profile


def test_build_profile():
    records = [
        InteractionRecord(
            user_id="u1",
            item_id="i1",
            rating=4.0,
            review_text="Great food and friendly staff",
            timestamp="2021-01-01",
            source="yelp",
        )
    ]

    profile = build_profile("u1", records)
    assert profile.user_id == "u1"
    assert profile.rating_stats.count == 1
    assert profile.stylometry.avg_word_count > 0
    assert profile.value_keywords["food"] == 1
    assert profile.cultural_signals.nigerian_english_index >= 0.0
