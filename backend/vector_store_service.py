from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .embeddings import EmbeddingModel, embed_texts, load_embedding_model
from .vector_store import InMemoryVectorStore


@dataclass
class VectorStoreService:
    store: InMemoryVectorStore
    embedding_model: EmbeddingModel

    @classmethod
    def create(cls, model_name: str = "all-MiniLM-L6-v2") -> "VectorStoreService":
        embedding_model = load_embedding_model(model_name)
        return cls(store=InMemoryVectorStore(items=[]), embedding_model=embedding_model)

    def add_text_items(self, items: List[Dict[str, object]], text_field: str) -> None:
        texts = [str(item.get(text_field, "")) for item in items]
        vectors = embed_texts(self.embedding_model, texts)

        for item, vector in zip(items, vectors):
            item_id = str(item.get("item_id", "")).strip()
            metadata = {k: v for k, v in item.items() if k != text_field}
            self.store.add(item_id=item_id, vector=vector, metadata=metadata)

    def query(self, query_text: str, top_k: int = 10) -> List[Dict[str, object]]:
        query_vector = embed_texts(self.embedding_model, [query_text])[0]
        results = self.store.query(query_vector, top_k=top_k)

        return [
            {
                "item_id": result.item_id,
                "score": result.score,
                "metadata": result.metadata,
            }
            for result in results
        ]
