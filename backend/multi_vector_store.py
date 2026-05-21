"""
Cross-domain retrieval: query multiple VectorStoreService instances and merge results.

Usage:
    service = MultiVectorStoreService(stores={"yelp": yelp_svc, "amazon": amazon_svc})
    results = service.query("great jollof rice near me", top_k=10)

Scores from different stores are normalised before merging so no single domain
dominates due to distributional differences in embedding norms.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .vector_store_service import VectorStoreService

logger = logging.getLogger("persona.multi_vector_store")


class MultiVectorStoreService:
    """Fan out a query to multiple stores, normalise per-store scores, merge."""

    def __init__(self, stores: Dict[str, VectorStoreService]) -> None:
        if not stores:
            raise ValueError("At least one store is required")
        self._stores = stores

    def query(
        self,
        query_text: str,
        top_k: int = 10,
        domain_weights: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, object]]:
        """
        Query all stores, merge results by weighted score, return top_k.

        Each result dict has: item_id, score, metadata, domain.
        """
        all_results: List[Dict[str, object]] = []

        for domain, store in self._stores.items():
            try:
                raw = store.query(query_text, top_k=top_k)
            except Exception:
                logger.exception("Error querying store %s", domain)
                continue

            if not raw:
                continue

            # Min-max normalise scores within this domain.
            scores = [r["score"] for r in raw]
            min_s, max_s = min(scores), max(scores)
            span = max_s - min_s or 1.0

            weight = (domain_weights or {}).get(domain, 1.0)

            for r in raw:
                norm_score = ((r["score"] - min_s) / span) * weight
                all_results.append({
                    "item_id": r["item_id"],
                    "score": norm_score,
                    "metadata": {**r.get("metadata", {}), "_domain": domain},
                    "domain": domain,
                })

        # Deduplicate by item_id, keeping highest score.
        seen: Dict[str, Dict[str, object]] = {}
        for r in all_results:
            iid = r["item_id"]
            if iid not in seen or r["score"] > seen[iid]["score"]:
                seen[iid] = r

        ranked = sorted(seen.values(), key=lambda r: r["score"], reverse=True)
        return ranked[:top_k]

    @property
    def domains(self) -> List[str]:
        return list(self._stores.keys())

    def add_store(self, domain: str, store: VectorStoreService) -> None:
        self._stores[domain] = store
        logger.info("Added store for domain '%s'", domain)

    def remove_store(self, domain: str) -> bool:
        removed = self._stores.pop(domain, None)
        if removed:
            logger.info("Removed store for domain '%s'", domain)
        return removed is not None
