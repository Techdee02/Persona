import json
import tempfile
from pathlib import Path

from backend.vector_store_service import VectorStoreService


def test_create_empty_when_no_path():
    service = VectorStoreService.create(store_path="")
    assert len(service.store.items) == 0


def test_create_empty_when_path_missing():
    service = VectorStoreService.create(store_path="/nonexistent/store.json")
    assert len(service.store.items) == 0


def test_create_loads_persisted_store():
    payload = [
        {"item_id": "item1", "vector": [1.0, 0.0], "metadata": {"name": "A"}},
        {"item_id": "item2", "vector": [0.0, 1.0], "metadata": {"name": "B"}},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp_path = f.name

    try:
        service = VectorStoreService.create(store_path=tmp_path)
        assert len(service.store.items) == 2
        ids = {item.item_id for item in service.store.items}
        assert ids == {"item1", "item2"}
    finally:
        Path(tmp_path).unlink(missing_ok=True)
