from __future__ import annotations

import argparse
import logging

from .ingest_datasets import ingest_amazon_reviews, ingest_goodreads_reviews, ingest_yelp_reviews
from .vector_store_persist import save_vector_store

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Persona dataset ingestion CLI")
    parser.add_argument("--dataset", choices=["yelp", "amazon", "goodreads"], required=True)
    parser.add_argument("--input",  required=True, help="Path to JSONL dataset file")
    parser.add_argument("--output", required=True, help="Path to save vector store JSON")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max records to ingest (useful for dev/demo stores from large datasets)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=512,
        help="Embedding batch size (default 512)",
    )

    args = parser.parse_args()

    kwargs = {"path": args.input, "batch_size": args.batch_size, "limit": args.limit}

    if args.dataset == "yelp":
        store = ingest_yelp_reviews(**kwargs)
    elif args.dataset == "amazon":
        store = ingest_amazon_reviews(**kwargs)
    else:
        store = ingest_goodreads_reviews(**kwargs)

    save_vector_store(store, args.output)
    print(f"Saved vector store with {len(store.items)} items → {args.output}")


if __name__ == "__main__":
    main()
