from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from sentence_transformers import SentenceTransformer


@dataclass(frozen=True)
class EmbeddingModel:
    name: str
    model: SentenceTransformer


def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> EmbeddingModel:
    model = SentenceTransformer(model_name)
    return EmbeddingModel(name=model_name, model=model)


def embed_texts(embedding_model: EmbeddingModel, texts: Iterable[str]) -> List[List[float]]:
    embeddings = embedding_model.model.encode(list(texts), show_progress_bar=False)
    return [vector.tolist() for vector in embeddings]
