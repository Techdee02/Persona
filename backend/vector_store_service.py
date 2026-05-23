from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .embeddings import EmbeddingModel, embed_texts, load_embedding_model
from .vector_store import InMemoryVectorStore
from .vector_store_persist import load_vector_store

logger = logging.getLogger("persona.vector_store_service")


@dataclass
class VectorStoreService:
    store: InMemoryVectorStore
    embedding_model: EmbeddingModel

    @classmethod
    def create(
        cls,
        model_name: str = "all-MiniLM-L6-v2",
        store_path: str = "",
    ) -> "VectorStoreService":
        embedding_model = load_embedding_model(model_name)

        if store_path and Path(store_path).exists():
            store = load_vector_store(store_path)
            logger.info("Loaded vector store from %s (%d items)", store_path, len(store.items))
        else:
            if store_path:
                logger.warning("VECTOR_STORE_PATH set to %s but file not found; starting empty", store_path)
            store = InMemoryVectorStore(items=[])

        return cls(store=store, embedding_model=embedding_model)

    def add_text_items(self, items: List[Dict[str, object]], text_field: str) -> None:
        texts = [str(item.get(text_field, "")) for item in items]
        vectors = embed_texts(self.embedding_model, texts)

        for item, vector in zip(items, vectors):
            item_id = str(item.get("item_id", "")).strip()
            metadata = {k: v for k, v in item.items() if k != text_field}
            self.store.add(item_id=item_id, vector=vector, metadata=metadata)

    def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, object]]:
        query_vector = embed_texts(self.embedding_model, [query_text])[0]
        # Over-fetch so deduplication leaves at least top_k unique businesses
        raw_results = self.store.query(query_vector, top_k=top_k * 5)

        seen: set = set()
        results = []
        for result in raw_results:
            if result.item_id in seen:
                continue
            seen.add(result.item_id)
            results.append(result)
            if len(results) >= top_k:
                break

        return [
            {
                "item_id": result.item_id,
                "score": result.score,
                "metadata": result.metadata,
            }
            for result in results
        ]
