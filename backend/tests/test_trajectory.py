from backend.data.schema import InteractionRecord
from backend.trajectory import extract_trajectory


def _record(rating: float, text: str, timestamp: str) -> InteractionRecord:
    return InteractionRecord(
        user_id="u1",
        item_id="i1",
        rating=rating,
        review_text=text,
        timestamp=timestamp,
        source="yelp",
    )


def test_extract_trajectory_requires_min_records():
    stats = extract_trajectory([
        _record(4.0, "Nice", "2021-01-01"),
        _record(3.0, "Ok", "2021-01-02"),
    ])
    assert stats.early_mean_rating == 0.0


def test_extract_trajectory_splits_early_recent():
    records = [
        _record(2.0, "Short", "2021-01-01"),
        _record(3.0, "Short", "2021-01-02"),
        _record(5.0, "Long review text", "2021-01-03"),
        _record(5.0, "Long review text", "2021-01-04"),
    ]
    stats = extract_trajectory(records)
    assert stats.delta_rating > 0
    assert stats.delta_review_length > 0
