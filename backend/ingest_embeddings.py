from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .embeddings import embed_texts, load_embedding_model
from .vector_store import InMemoryVectorStore


def ingest_dataset(
    dataset_path: str,
    text_field: str,
    id_field: str,
    metadata_fields: List[str],
    model_name: str = "all-MiniLM-L6-v2",
) -> InMemoryVectorStore:
    records = _load_jsonl(dataset_path)
    texts = [record.get(text_field, "") for record in records]

    embedding_model = load_embedding_model(model_name)
    vectors = embed_texts(embedding_model, texts)

    store = InMemoryVectorStore(items=[])
    for record, vector in zip(records, vectors):
        metadata = {field: record.get(field) for field in metadata_fields}
        store.add(item_id=str(record.get(id_field, "")), vector=vector, metadata=metadata)

    return store


def _load_jsonl(path: str) -> List[Dict[str, object]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    records: List[Dict[str, object]] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    return records
