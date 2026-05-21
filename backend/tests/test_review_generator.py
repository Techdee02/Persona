from backend.cultural_signals import CulturalSignals
from backend.profile import PsychologicalProfile
from backend.review_generator import generate_review
from backend.signal_extraction import RatingStats, StylometryStats
from backend.trajectory import TrajectoryStats


def _profile(mean: float, food: int = 0, cultural: bool = False) -> PsychologicalProfile:
    return PsychologicalProfile(
        user_id="u1",
        rating_stats=RatingStats(count=5, mean=mean, std_dev=0.5, min_rating=1.0, max_rating=5.0),
        stylometry=StylometryStats(
            avg_review_length=150.0, avg_word_count=30.0,
            vocab_richness=0.5, avg_sentence_length=10.0,
        ),
        value_keywords={"food": food, "service": 0, "price": 0, "atmosphere": 0},
        trajectory=TrajectoryStats(0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        cultural_signals=CulturalSignals(
            nigerian_english_index=0.05 if cultural else 0.0,
            code_switching_detected=cultural,
            pidgin_term_hits=2 if cultural else 0,
        ),
    )


def test_generate_review_returns_string():
    review = generate_review(_profile(4.5), {}, seed=42)
    assert isinstance(review, str)
    assert len(review) > 0


def test_positive_profile_positive_sentiment():
    review = generate_review(_profile(4.5), {}, seed=0)
    positive_words = {"enjoyed", "worth", "can't", "definitely", "delivered"}
    assert any(w in review.lower() for w in positive_words)


def test_negative_profile_negative_sentiment():
    review = generate_review(_profile(1.5), {}, seed=0)
    negative_words = {"disappoint", "expected", "underwhelm", "left"}
    assert any(w in review.lower() for w in negative_words)


def test_food_value_mentioned_when_top_category():
    review = generate_review(_profile(4.0, food=5), {}, seed=0)
    food_words = {"food", "tasty", "flavour", "kitchen", "menu"}
    assert any(w in review.lower() for w in food_words)


def test_cultural_closer_when_code_switching():
    review = generate_review(_profile(4.0, cultural=True), {}, seed=0)
    pidgin_words = {"abeg", "sha", "omo", "na so"}
    assert any(w in review.lower() for w in pidgin_words)


def test_item_name_appears_in_review():
    review = generate_review(_profile(4.0), {"name": "Mama Titi's Kitchen"}, seed=0)
    assert "Mama Titi's Kitchen" in review


def test_deterministic_with_same_seed():
    r1 = generate_review(_profile(4.0), {}, seed=7)
    r2 = generate_review(_profile(4.0), {}, seed=7)
    assert r1 == r2
