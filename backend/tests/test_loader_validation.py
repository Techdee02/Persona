import json
import tempfile
from pathlib import Path

from backend.data.loaders import load_yelp_reviews


def _write_jsonl(rows: list, suffix=".jsonl") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    for row in rows:
        f.write(json.dumps(row) + "\n")
    f.flush()
    return f.name


def test_valid_rows_loaded():
    path = _write_jsonl([
        {"user_id": "u1", "business_id": "b1", "stars": 4.0, "text": "Great", "date": "2021-01-01"},
    ])
    records = load_yelp_reviews(path)
    assert len(records) == 1
    Path(path).unlink(missing_ok=True)


def test_missing_user_id_skipped():
    path = _write_jsonl([
        {"user_id": "",  "business_id": "b1", "stars": 4.0, "text": "Great", "date": "2021-01-01"},
        {"user_id": "u2","business_id": "b2", "stars": 3.0, "text": "Okay",  "date": "2021-01-02"},
    ])
    records = load_yelp_reviews(path)
    assert len(records) == 1
    assert records[0].user_id == "u2"
    Path(path).unlink(missing_ok=True)


def test_invalid_rating_skipped():
    path = _write_jsonl([
        {"user_id": "u1", "business_id": "b1", "stars": "not_a_number", "text": "Hi", "date": "2021-01-01"},
        {"user_id": "u2", "business_id": "b2", "stars": 5.0,            "text": "Hi", "date": "2021-01-02"},
    ])
    records = load_yelp_reviews(path)
    assert len(records) == 1
    assert records[0].user_id == "u2"
    Path(path).unlink(missing_ok=True)


def test_out_of_range_rating_skipped():
    path = _write_jsonl([
        {"user_id": "u1", "business_id": "b1", "stars": 99.0, "text": "Hi", "date": "2021-01-01"},
    ])
    records = load_yelp_reviews(path)
    assert len(records) == 0
    Path(path).unlink(missing_ok=True)
