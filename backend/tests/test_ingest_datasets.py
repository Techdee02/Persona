import json

from backend.ingest_datasets import ingest_yelp_reviews


def test_ingest_yelp_reviews(tmp_path):
    data_path = tmp_path / "yelp.jsonl"
    with data_path.open("w", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "business_id": "b1",
                    "text": "Nice food",
                    "name": "Spot",
                    "categories": "Food",
                    "stars": 4.0,
                }
            )
        )
        handle.write("\n")

    store = ingest_yelp_reviews(str(data_path))
    results = store.query([1.0] * len(store.items[0].vector), top_k=1)
    assert results[0].item_id == "b1"
