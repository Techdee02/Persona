from backend.deliberative_scoring import deliberative_score
from backend.preference_axes import PreferenceAxis
from backend.retrieval import RetrievalResult


def test_deliberative_scoring_orders_by_score():
    candidates = [
        RetrievalResult(item_id="a", score=0.3, metadata={}),
        RetrievalResult(item_id="b", score=0.2, metadata={}),
    ]
    axes = [PreferenceAxis(name="food", rationale="", weight=0.5)]

    results = deliberative_score(candidates, axes)
    assert results[0].item_id == "a"
    assert "Matched axes" in results[0].explanation


def test_deliberative_scoring_boosts_matching_metadata():
    # Item "b" has "food" in metadata so it gets an axis boost; "a" does not.
    candidates = [
        RetrievalResult(item_id="a", score=0.5, metadata={}),
        RetrievalResult(item_id="b", score=0.2, metadata={"food": True}),
    ]
    axes = [PreferenceAxis(name="food", rationale="", weight=0.5)]

    results = deliberative_score(candidates, axes)
    assert results[0].item_id == "b"
    assert results[0].score == 0.2 + 0.5
    assert results[1].score == 0.5


def test_deliberative_scoring_applies_penalties():
    # Item has matching axis key AND matching penalty key in metadata.
    candidates = [
        RetrievalResult(item_id="a", score=0.5, metadata={"service": True, "slow_service": True})
    ]
    axes = [PreferenceAxis(name="service", rationale="", weight=0.2)]

    results = deliberative_score(candidates, axes, penalties={"slow_service": 0.4})
    assert results[0].score == 0.5 + 0.2 - 0.4
    assert "Conflicts" in results[0].explanation


def test_deliberative_scoring_no_metadata_match_leaves_score_unchanged():
    # No metadata keys match axes or penalties — score equals raw retrieval score.
    candidates = [RetrievalResult(item_id="a", score=0.5, metadata={})]
    axes = [PreferenceAxis(name="service", rationale="", weight=0.2)]

    results = deliberative_score(candidates, axes, penalties={"slow_service": 0.4})
    assert results[0].score == 0.5
