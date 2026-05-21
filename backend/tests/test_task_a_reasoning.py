"""Tests for the richer Task A reasoning trace."""
from backend.task_a_service import _build_reasoning
from backend.rating_calibration import RatingCalibration
from backend.profile import PsychologicalProfile
from backend.signal_extraction import RatingStats, StylometryStats
from backend.cultural_signals import CulturalSignals
from backend.trajectory import TrajectoryStats


def _make_profile(
    mean=4.0,
    std_dev=0.5,
    count=10,
    delta_rating=0.0,
    code_switching=False,
    ni_index=0.0,
    avg_word_count=80.0,
    vocab_richness=0.6,
    value_keywords=None,
):
    return PsychologicalProfile(
        user_id="u1",
        rating_stats=RatingStats(count=count, mean=mean, std_dev=std_dev,
                                 min_rating=mean - 1, max_rating=mean + 1),
        stylometry=StylometryStats(avg_review_length=avg_word_count * 5,
                                   avg_word_count=avg_word_count,
                                   vocab_richness=vocab_richness,
                                   avg_sentence_length=15.0),
        value_keywords=value_keywords or {"food": 5, "service": 2, "price": 1, "atmosphere": 0},
        trajectory=TrajectoryStats(
            early_mean_rating=mean - delta_rating / 2,
            recent_mean_rating=mean + delta_rating / 2,
            delta_rating=delta_rating,
            early_avg_review_length=80.0,
            recent_avg_review_length=80.0,
            delta_review_length=0.0,
        ),
        cultural_signals=CulturalSignals(
            nigerian_english_index=ni_index,
            code_switching_detected=code_switching,
            pidgin_term_hits=2 if code_switching else 0,
        ),
    )


def _calibration(user_mean=4.0, pop_mean=3.5):
    return RatingCalibration(user_mean=user_mean, user_std=0.5,
                             population_mean=pop_mean, population_std=0.5)


def test_reasoning_includes_user_mean():
    profile = _make_profile(mean=4.2)
    r = _build_reasoning(profile, _calibration(4.2, 3.5), 3.9)
    assert "4.20" in r


def test_reasoning_mentions_top_axes():
    profile = _make_profile(value_keywords={"food": 8, "service": 2, "price": 0, "atmosphere": 0})
    r = _build_reasoning(profile, _calibration(), 4.0)
    assert "food" in r


def test_reasoning_mentions_trajectory_when_large():
    profile = _make_profile(delta_rating=0.5)
    r = _build_reasoning(profile, _calibration(), 4.0)
    assert any(word in r.lower() for word in ("improved", "declined", "trajectory"))


def test_reasoning_skips_trajectory_when_small():
    profile = _make_profile(delta_rating=0.1)
    r = _build_reasoning(profile, _calibration(), 4.0)
    assert "improved" not in r and "declined" not in r


def test_reasoning_includes_cultural_signal_when_detected():
    profile = _make_profile(code_switching=True, ni_index=0.4)
    r = _build_reasoning(profile, _calibration(), 4.0)
    assert "Nigerian English" in r


def test_reasoning_no_cultural_signal_when_absent():
    profile = _make_profile(code_switching=False)
    r = _build_reasoning(profile, _calibration(), 4.0)
    assert "Nigerian English" not in r


def test_reasoning_no_history_fallback():
    profile = _make_profile(count=0, mean=3.0)
    r = _build_reasoning(profile, _calibration(3.0, 3.0), 3.0)
    assert "No rating history" in r
