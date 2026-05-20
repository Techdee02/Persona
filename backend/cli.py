from __future__ import annotations

import argparse

from .ingest_datasets import ingest_amazon_reviews, ingest_goodreads_reviews, ingest_yelp_reviews
from .vector_store_persist import save_vector_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Persona dataset ingestion CLI")
    parser.add_argument("--dataset", choices=["yelp", "amazon", "goodreads"], required=True)
    parser.add_argument("--input", required=True, help="Path to JSONL dataset")
    parser.add_argument("--output", required=True, help="Path to save vector store JSON")

    args = parser.parse_args()

    if args.dataset == "yelp":
        store = ingest_yelp_reviews(args.input)
    elif args.dataset == "amazon":
        store = ingest_amazon_reviews(args.input)
    else:
        store = ingest_goodreads_reviews(args.input)

    save_vector_store(store, args.output)


if __name__ == "__main__":
    main()
