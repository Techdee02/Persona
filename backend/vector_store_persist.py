from __future__ import annotations

import json
from pathlib import Path

from .vector_store import InMemoryVectorStore


def save_vector_store(store: InMemoryVectorStore, path: str) -> None:
    """
    Persist a vector store to disk in JSONL format (one item per line).

    Stream-writes one record at a time so memory usage stays bounded
    regardless of store size.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for item in store.items:
            fh.write(json.dumps({
                "item_id": item.item_id,
                "vector": item.vector.tolist(),
                "metadata": item.metadata,
            }))
            fh.write("\n")


def load_vector_store(path: str) -> InMemoryVectorStore:
    """
    Load a vector store from disk.

    Supports both JSONL format (one item per line) and the legacy single-array
    JSON format for backward compatibility with small test stores.

    Streams JSONL line by line so memory usage is bounded to one parsed item
    at a time plus the accumulated store.
    """
    file_path = Path(path)
    store = InMemoryVectorStore(items=[])

    with file_path.open("r", encoding="utf-8") as fh:
        first_char = fh.read(1)
        if not first_char:
            return store  # empty file

        if first_char == "[":
            # Legacy single-array JSON — small files only; load in full.
            rest = first_char + fh.read()
            for item in json.loads(rest):
                store.add(
                    item_id=str(item.get("item_id", "")),
                    vector=item.get("vector", []),
                    metadata=item.get("metadata", {}),
                )
        else:
            # JSONL: stream one line at a time.
            # Re-parse the first (already-consumed) line.
            first_line = first_char + fh.readline()
            _add_line(store, first_line)
            for line in fh:
                _add_line(store, line)

    return store


def _add_line(store: InMemoryVectorStore, line: str) -> None:
    line = line.strip()
    if not line:
        return
    item = json.loads(line)
    store.add(
        item_id=str(item.get("item_id", "")),
        vector=item.get("vector", []),
        metadata=item.get("metadata", {}),
    )
