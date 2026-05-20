from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .vector_store import InMemoryVectorStore


def save_vector_store(store: InMemoryVectorStore, path: str) -> None:
    payload = [
        {
            "item_id": item.item_id,
            "vector": item.vector.tolist(),
            "metadata": item.metadata,
        }
        for item in store.items
    ]

    Path(path).write_text(json.dumps(payload), encoding="utf-8")


def load_vector_store(path: str) -> InMemoryVectorStore:
    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8"))

    store = InMemoryVectorStore(items=[])
    for item in payload:
        store.add(
            item_id=str(item.get("item_id", "")),
            vector=item.get("vector", []),
            metadata=item.get("metadata", {}),
        )

    return store
