from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import numpy as np


@dataclass(frozen=True)
class RetrievalItem:
    item_id: str
    vector: np.ndarray
    metadata: dict


@dataclass(frozen=True)
class RetrievalResult:
    item_id: str
    score: float
    metadata: dict


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return 0.0
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def multi_angle_retrieve(
    items: Iterable[RetrievalItem],
    query_vectors: Sequence[np.ndarray],
    top_k: int = 10,
    weights: Sequence[float] | None = None,
) -> List[RetrievalResult]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    if not query_vectors:
        return []

    if weights is None:
        weights = [1.0] * len(query_vectors)
    if len(weights) != len(query_vectors):
        raise ValueError("weights must match number of query_vectors")

    results: List[RetrievalResult] = []
    for item in items:
        scores = [
            _cosine_similarity(item.vector, query_vector) * weight
            for query_vector, weight in zip(query_vectors, weights)
        ]
        combined = sum(scores) / sum(weights)
        results.append(RetrievalResult(item_id=item.item_id, score=combined, metadata=item.metadata))

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_k]
