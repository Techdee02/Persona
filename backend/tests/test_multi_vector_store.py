"""Tests for MultiVectorStoreService cross-domain retrieval."""
from unittest.mock import MagicMock
import pytest

from backend.multi_vector_store import MultiVectorStoreService


def _mock_store(results):
    store = MagicMock()
    store.query.return_value = results
    return store


def test_query_merges_results_from_multiple_stores():
    yelp = _mock_store([
        {"item_id": "y1", "score": 0.9, "metadata": {}},
        {"item_id": "y2", "score": 0.5, "metadata": {}},
    ])
    amazon = _mock_store([
        {"item_id": "a1", "score": 0.8, "metadata": {}},
    ])
    svc = MultiVectorStoreService(stores={"yelp": yelp, "amazon": amazon})
    results = svc.query("great food", top_k=5)
    item_ids = [r["item_id"] for r in results]
    assert "y1" in item_ids
    assert "a1" in item_ids


def test_query_deduplicates_by_item_id():
    store_a = _mock_store([{"item_id": "shared", "score": 0.9, "metadata": {}}])
    store_b = _mock_store([{"item_id": "shared", "score": 0.7, "metadata": {}}])
    svc = MultiVectorStoreService(stores={"a": store_a, "b": store_b})
    results = svc.query("test", top_k=5)
    ids = [r["item_id"] for r in results]
    assert ids.count("shared") == 1


def test_query_respects_top_k():
    items = [{"item_id": f"i{n}", "score": n / 10, "metadata": {}} for n in range(10)]
    store = _mock_store(items)
    svc = MultiVectorStoreService(stores={"yelp": store})
    results = svc.query("x", top_k=3)
    assert len(results) <= 3


def test_domain_metadata_tagged():
    store = _mock_store([{"item_id": "z1", "score": 1.0, "metadata": {}}])
    svc = MultiVectorStoreService(stores={"yelp": store})
    results = svc.query("q", top_k=1)
    assert results[0]["domain"] == "yelp"


def test_requires_at_least_one_store():
    with pytest.raises(ValueError):
        MultiVectorStoreService(stores={})


def test_faulty_store_is_skipped():
    bad_store = MagicMock()
    bad_store.query.side_effect = RuntimeError("connection error")
    good_store = _mock_store([{"item_id": "ok", "score": 1.0, "metadata": {}}])
    svc = MultiVectorStoreService(stores={"bad": bad_store, "good": good_store})
    results = svc.query("test", top_k=5)
    assert any(r["item_id"] == "ok" for r in results)


def test_add_and_remove_store():
    store_a = _mock_store([{"item_id": "a", "score": 1.0, "metadata": {}}])
    store_b = _mock_store([{"item_id": "b", "score": 1.0, "metadata": {}}])
    svc = MultiVectorStoreService(stores={"a": store_a})
    svc.add_store("b", store_b)
    assert "b" in svc.domains
    svc.remove_store("b")
    assert "b" not in svc.domains
