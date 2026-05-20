from backend.vector_store import InMemoryVectorStore
from backend.vector_store_persist import load_vector_store, save_vector_store


def test_vector_store_save_load(tmp_path):
    store = InMemoryVectorStore(items=[])
    store.add("a", [1.0, 0.0], {"name": "A"})

    path = tmp_path / "store.json"
    save_vector_store(store, str(path))

    loaded = load_vector_store(str(path))
    assert len(loaded.items) == 1
    assert loaded.items[0].item_id == "a"
