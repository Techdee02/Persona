from backend.vector_store import InMemoryVectorStore


def test_vector_store_query():
    store = InMemoryVectorStore(items=[])
    store.add("a", [1.0, 0.0], {"name": "A"})
    store.add("b", [0.0, 1.0], {"name": "B"})

    results = store.query([1.0, 0.0], top_k=1)
    assert results[0].item_id == "a"
