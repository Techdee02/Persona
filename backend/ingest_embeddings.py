from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from .embeddings import embed_texts, load_embedding_model
from .vector_store import InMemoryVectorStore

logger = logging.getLogger("persona.ingest")


def ingest_dataset(
    dataset_path: str,
    text_field: str,
    id_field: str,
    metadata_fields: List[str],
    model_name: str = "all-MiniLM-L6-v2",
    batch_size: int = 512,
    limit: Optional[int] = None,
) -> InMemoryVectorStore:
    """
    Stream-ingest a JSONL dataset into an InMemoryVectorStore.

    Records are read and embedded in batches of `batch_size` to keep memory
    usage bounded regardless of dataset size. `limit` caps the total number of
    records ingested (useful for dev/demo stores from large datasets).
    """
    embedding_model = load_embedding_model(model_name)
    store = InMemoryVectorStore(items=[])
    total = 0

    for batch in _stream_batches(dataset_path, batch_size=batch_size, limit=limit):
        texts = [r.get(text_field, "") for r in batch]
        vectors = embed_texts(embedding_model, texts)

        for record, vector in zip(batch, vectors):
            item_id = str(record.get(id_field, "")).strip()
            if not item_id:
                continue
            metadata = {field: record.get(field) for field in metadata_fields}
            store.add(item_id=item_id, vector=vector, metadata=metadata)
            total += 1

        logger.info("Ingested %d records so far …", total)

    logger.info("Ingestion complete — %d items in store", total)
    return store


def _stream_batches(
    path: str,
    batch_size: int,
    limit: Optional[int],
) -> Iterator[List[Dict]]:
    """Yield successive batches of raw dicts from a JSONL file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    batch: List[Dict] = []
    ingested = 0

    with file_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if limit is not None and ingested >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                batch.append(json.loads(line))
                ingested += 1
            except json.JSONDecodeError:
                continue

            if len(batch) >= batch_size:
                yield batch
                batch = []

    if batch:
        yield batch


def _load_jsonl(path: str) -> List[Dict[str, object]]:
    """Load entire JSONL file into memory (legacy; prefer _stream_batches)."""
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
