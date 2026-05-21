import math

from backend.evaluation.metrics import (
    hit_rate_at_k,
    mean_rating_baseline,
    ndcg_at_k,
    popularity_baseline,
    rmse,
    rouge_l,
    rouge_l_corpus,
)


# ── RMSE ─────────────────────────────────────────────────────────────────────

def test_rmse_perfect_prediction():
    assert rmse([3.0, 4.0, 5.0], [3.0, 4.0, 5.0]) == 0.0


def test_rmse_known_value():
    # errors are 1.0 each → RMSE = 1.0
    assert rmse([2.0, 3.0], [3.0, 4.0]) == pytest_approx(1.0)


def test_rmse_empty():
    assert rmse([], []) == 0.0


# ── ROUGE-L ───────────────────────────────────────────────────────────────────

def test_rouge_l_identical():
    assert rouge_l("the food was great", "the food was great") == 1.0


def test_rouge_l_no_overlap():
    assert rouge_l("apple banana", "orange kiwi") == 0.0


def test_rouge_l_partial():
    score = rouge_l("the food was great", "the food was okay")
    assert 0.0 < score < 1.0


def test_rouge_l_corpus_mean():
    score = rouge_l_corpus(
        ["the food was great", "nice place"],
        ["the food was great", "nice place"],
    )
    assert score == 1.0


# ── NDCG ─────────────────────────────────────────────────────────────────────

def test_ndcg_perfect():
    assert ndcg_at_k(["a", "b", "c"], {"a", "b"}, k=3) == 1.0


def test_ndcg_no_relevant():
    assert ndcg_at_k(["x", "y"], {"a"}, k=2) == 0.0


def test_ndcg_partial():
    score = ndcg_at_k(["x", "a", "y"], {"a"}, k=3)
    assert 0.0 < score < 1.0


# ── Hit Rate ─────────────────────────────────────────────────────────────────

def test_hit_rate_hit():
    assert hit_rate_at_k(["a", "b", "c"], {"b"}, k=3) == 1.0


def test_hit_rate_miss():
    assert hit_rate_at_k(["a", "b", "c"], {"z"}, k=3) == 0.0


def test_hit_rate_outside_k():
    assert hit_rate_at_k(["a", "b", "c"], {"c"}, k=2) == 0.0


# ── Baselines ─────────────────────────────────────────────────────────────────

def test_mean_rating_baseline():
    assert mean_rating_baseline([3.0, 4.0, 5.0]) == 4.0


def test_popularity_baseline_order():
    counts = {"a": 10, "b": 5, "c": 8}
    result = popularity_baseline(counts, k=2)
    assert result == ["a", "c"]


# helper so we don't need pytest.approx import at top level
def pytest_approx(val, rel=1e-6):
    import pytest
    return pytest.approx(val, rel=rel)
