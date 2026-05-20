from backend.data.schema import InteractionRecord
from backend.rating_calibration import build_rating_calibration


def _record(rating: float) -> InteractionRecord:
    return InteractionRecord(
        user_id="u1",
        item_id="i1",
        rating=rating,
        review_text="",
        timestamp="2021-01-01",
        source="yelp",
    )


def test_calibration_no_std_returns_rating():
    calibration = build_rating_calibration([_record(4.0)], [_record(3.0), _record(5.0)])
    assert calibration.calibrate(4.0) == 4.0


def test_calibration_adjusts_rating():
    user_records = [_record(1.0), _record(5.0)]
    population_records = [_record(3.0), _record(4.0), _record(5.0)]
    calibration = build_rating_calibration(user_records, population_records)

    calibrated = calibration.calibrate(5.0)
    assert 1.0 <= calibrated <= 5.0
