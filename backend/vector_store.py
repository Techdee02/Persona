from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np

from .retrieval import RetrievalItem, RetrievalResult, _cosine_similarity


@dataclass
class InMemoryVectorStore:
    items: List[RetrievalItem]

    def add(self, item_id: str, vector: List[float], metadata: Dict[str, object]) -> None:
        self.items.append(
            RetrievalItem(item_id=item_id, vector=np.array(vector, dtype=float), metadata=metadata)
        )

    def query(self, query_vector: List[float], top_k: int = 10) -> List[RetrievalResult]:
        query = np.array(query_vector, dtype=float)
        results = []
        for item in self.items:
            score = _cosine_similarity(item.vector, query)
            results.append(RetrievalResult(item_id=item.item_id, score=score, metadata=item.metadata))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]
