from backend.data.schema import InteractionRecord
from backend.data.split import temporal_split


def test_temporal_split_orders_by_time():
    records = [
        InteractionRecord(
            user_id="u1",
            item_id="a",
            rating=4.0,
            review_text="",
            timestamp="2021-01-02",
            source="yelp",
        ),
        InteractionRecord(
            user_id="u1",
            item_id="b",
            rating=3.0,
            review_text="",
            timestamp="2021-01-01",
            source="yelp",
        ),
    ]

    train, test = temporal_split(records, train_ratio=0.5)
    assert len(train) == 1
    assert len(test) == 1
    assert train[0].item_id == "b"
    assert test[0].item_id == "a"
