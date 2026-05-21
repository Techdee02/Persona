from __future__ import annotations

import math
from typing import List, Set, Sequence


# ── Task A metrics ────────────────────────────────────────────────────────────

def rmse(predictions: Sequence[float], ground_truth: Sequence[float]) -> float:
    """Root-mean-square error between predicted and actual ratings."""
    if len(predictions) != len(ground_truth):
        raise ValueError("predictions and ground_truth must have equal length")
    if not predictions:
        return 0.0
    return math.sqrt(sum((p - g) ** 2 for p, g in zip(predictions, ground_truth)) / len(predictions))


def rouge_l(hypothesis: str, reference: str) -> float:
    """
    Sentence-level ROUGE-L F1 via longest common subsequence.
    Operates on whitespace-tokenised words; case-insensitive.
    """
    h_tokens = hypothesis.lower().split()
    r_tokens = reference.lower().split()
    lcs = _lcs_length(h_tokens, r_tokens)
    if lcs == 0:
        return 0.0
    precision = lcs / len(h_tokens) if h_tokens else 0.0
    recall = lcs / len(r_tokens) if r_tokens else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def rouge_l_corpus(hypotheses: List[str], references: List[str]) -> float:
    """Mean ROUGE-L F1 over a list of hypothesis/reference pairs."""
    if len(hypotheses) != len(references):
        raise ValueError("hypotheses and references must have equal length")
    if not hypotheses:
        return 0.0
    return sum(rouge_l(h, r) for h, r in zip(hypotheses, references)) / len(hypotheses)


def _lcs_length(a: List[str], b: List[str]) -> int:
    """Dynamic-programming LCS length."""
    m, n = len(a), len(b)
    # Use two rolling rows to keep memory O(n).
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(curr[j - 1], prev[j])
        prev, curr = curr, [0] * (n + 1)
    return prev[n]


# ── Task B metrics ────────────────────────────────────────────────────────────

def ndcg_at_k(ranked_items: List[str], relevant_items: Set[str], k: int = 10) -> float:
    """
    NDCG@k using binary relevance (1 if item in relevant_items, else 0).
    ranked_items is the ordered recommendation list (best first).
    """
    dcg = _dcg(ranked_items[:k], relevant_items)
    ideal = _dcg(sorted(ranked_items[:k], key=lambda x: x in relevant_items, reverse=True), relevant_items)
    return dcg / ideal if ideal > 0 else 0.0


def hit_rate_at_k(ranked_items: List[str], relevant_items: Set[str], k: int = 10) -> float:
    """
    Hit Rate@k: 1.0 if at least one relevant item appears in the top-k, else 0.0.
    Averaged over a list of (ranked_items, relevant_items) pairs by the caller.
    """
    return 1.0 if any(item in relevant_items for item in ranked_items[:k]) else 0.0


def _dcg(ranked_items: List[str], relevant_items: Set[str]) -> float:
    return sum(
        (1.0 if item in relevant_items else 0.0) / math.log2(rank + 2)
        for rank, item in enumerate(ranked_items)
    )


# ── Baseline helpers ──────────────────────────────────────────────────────────

def mean_rating_baseline(ratings: List[float]) -> float:
    """Global mean rating — the simplest Task A baseline."""
    return sum(ratings) / len(ratings) if ratings else 0.0


def popularity_baseline(item_interaction_counts: dict[str, int], k: int = 10) -> List[str]:
    """Top-k most interacted-with items — the simplest Task B baseline."""
    return sorted(item_interaction_counts, key=item_interaction_counts.get, reverse=True)[:k]
