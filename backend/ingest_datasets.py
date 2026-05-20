from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .ingest_embeddings import ingest_dataset
from .vector_store import InMemoryVectorStore


@dataclass(frozen=True)
class DatasetIngestConfig:
    dataset_path: str
    text_field: str
    id_field: str
    metadata_fields: List[str]


def ingest_yelp_reviews(path: str) -> InMemoryVectorStore:
    config = DatasetIngestConfig(
        dataset_path=path,
        text_field="text",
        id_field="business_id",
        metadata_fields=["name", "categories", "stars"],
    )
    return ingest_dataset(**config.__dict__)


def ingest_amazon_reviews(path: str) -> InMemoryVectorStore:
    config = DatasetIngestConfig(
        dataset_path=path,
        text_field="reviewText",
        id_field="asin",
        metadata_fields=["summary", "overall"],
    )
    return ingest_dataset(**config.__dict__)


def ingest_goodreads_reviews(path: str) -> InMemoryVectorStore:
    config = DatasetIngestConfig(
        dataset_path=path,
        text_field="review_text",
        id_field="book_id",
        metadata_fields=["rating"],
    )
    return ingest_dataset(**config.__dict__)
