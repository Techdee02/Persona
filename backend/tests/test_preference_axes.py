from backend.profile import PsychologicalProfile
from backend.signal_extraction import RatingStats, StylometryStats
from backend.cultural_signals import CulturalSignals
from backend.trajectory import TrajectoryStats
from backend.preference_axes import extract_preference_axes


def test_extract_preference_axes_from_profile():
    profile = PsychologicalProfile(
        user_id="u1",
        rating_stats=RatingStats(count=3, mean=4.2, std_dev=0.5, min_rating=3.0, max_rating=5.0),
        stylometry=StylometryStats(
            avg_review_length=100.0,
            avg_word_count=20.0,
            vocab_richness=0.4,
            avg_sentence_length=10.0,
        ),
        value_keywords={"food": 4, "service": 1, "price": 0, "atmosphere": 0},
        trajectory=TrajectoryStats(
            early_mean_rating=3.0,
            recent_mean_rating=4.0,
            delta_rating=1.0,
            early_avg_review_length=50.0,
            recent_avg_review_length=100.0,
            delta_review_length=50.0,
        ),
        cultural_signals=CulturalSignals(
            nigerian_english_index=0.2,
            code_switching_detected=True,
            pidgin_term_hits=3,
        ),
    )

    axes = extract_preference_axes(profile)
    names = [axis.name for axis in axes]

    assert "food" in names
    assert "rating_bias" in names
    assert "cultural_register" in names
