import json

from backend.data.loaders import load_amazon_reviews, load_goodreads_reviews, load_yelp_reviews


def _write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row))
            handle.write("\n")


def test_load_yelp_reviews(tmp_path):
    data_path = tmp_path / "yelp.jsonl"
    _write_jsonl(
        data_path,
        [
            {
                "user_id": "u1",
                "business_id": "b1",
                "stars": 4.0,
                "text": "Nice place",
                "date": "2021-01-01",
            }
        ],
    )

    records = load_yelp_reviews(str(data_path))
    assert len(records) == 1
    assert records[0].user_id == "u1"
    assert records[0].item_id == "b1"


def test_load_amazon_reviews(tmp_path):
    data_path = tmp_path / "amazon.jsonl"
    _write_jsonl(
        data_path,
        [
            {
                "reviewerID": "u2",
                "asin": "p1",
                "overall": 5,
                "reviewText": "Great",
                "unixReviewTime": 1670000000,
            }
        ],
    )

    records = load_amazon_reviews(str(data_path))
    assert len(records) == 1
    assert records[0].user_id == "u2"
    assert records[0].item_id == "p1"


def test_load_goodreads_reviews(tmp_path):
    data_path = tmp_path / "goodreads.jsonl"
    _write_jsonl(
        data_path,
        [
            {
                "user_id": "u3",
                "book_id": "bk1",
                "rating": 3,
                "review_text": "Ok",
                "date": "2022-03-01",
            }
        ],
    )

    records = load_goodreads_reviews(str(data_path))
    assert len(records) == 1
    assert records[0].user_id == "u3"
    assert records[0].item_id == "bk1"
