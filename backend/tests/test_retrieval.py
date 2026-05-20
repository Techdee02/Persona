import numpy as np

from backend.retrieval import RetrievalItem, multi_angle_retrieve


def test_multi_angle_retrieve_returns_top_k():
    items = [
        RetrievalItem(item_id="a", vector=np.array([1.0, 0.0]), metadata={}),
        RetrievalItem(item_id="b", vector=np.array([0.0, 1.0]), metadata={}),
    ]

    results = multi_angle_retrieve(items, [np.array([1.0, 0.0])], top_k=1)
    assert len(results) == 1
    assert results[0].item_id == "a"


def test_multi_angle_retrieve_averages_scores():
    items = [
        RetrievalItem(item_id="a", vector=np.array([1.0, 0.0]), metadata={}),
        RetrievalItem(item_id="b", vector=np.array([0.0, 1.0]), metadata={}),
    ]

    results = multi_angle_retrieve(
        items,
        [np.array([1.0, 0.0]), np.array([0.0, 1.0])],
        top_k=2,
        weights=[1.0, 1.0],
    )
    assert results[0].score == results[1].score
