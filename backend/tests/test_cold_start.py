from backend.cold_start import ColdStartAnswer, bootstrap_profile, COLD_START_QUESTIONS


def test_questions_list_has_four_items():
    assert len(COLD_START_QUESTIONS) == 4


def test_bootstrap_profile_generous_rater():
    answers = [ColdStartAnswer(question_id="rating_tendency", answer="top_marks")]
    profile = bootstrap_profile("u1", answers)
    assert profile.rating_stats.mean == 4.5


def test_bootstrap_profile_value_priority_food():
    answers = [ColdStartAnswer(question_id="value_priority", answer="food_quality")]
    profile = bootstrap_profile("u1", answers)
    assert profile.value_keywords["food"] == 3
    assert profile.value_keywords["service"] == 0


def test_bootstrap_profile_detailed_reviewer():
    answers = [ColdStartAnswer(question_id="review_style", answer="detailed_and_thorough")]
    profile = bootstrap_profile("u1", answers)
    assert profile.stylometry.avg_review_length == 300.0


def test_bootstrap_profile_cultural_signals():
    answers = [ColdStartAnswer(question_id="cultural_register", answer="yes_often")]
    profile = bootstrap_profile("u1", answers)
    assert profile.cultural_signals.code_switching_detected is True
    assert profile.cultural_signals.nigerian_english_index > 0


def test_bootstrap_profile_combined_answers():
    answers = [
        ColdStartAnswer(question_id="rating_tendency", answer="reserve_top"),
        ColdStartAnswer(question_id="value_priority", answer="service"),
        ColdStartAnswer(question_id="review_style", answer="brief_and_direct"),
        ColdStartAnswer(question_id="cultural_register", answer="rarely"),
    ]
    profile = bootstrap_profile("u1", answers)
    assert profile.rating_stats.mean == 3.5
    assert profile.value_keywords["service"] == 3
    assert profile.stylometry.avg_review_length == 80.0
    assert profile.cultural_signals.code_switching_detected is False


def test_bootstrap_profile_unknown_answer_ignored():
    answers = [ColdStartAnswer(question_id="rating_tendency", answer="not_a_valid_option")]
    profile = bootstrap_profile("u1", answers)
    # Falls back to defaults — should not raise
    assert profile.user_id == "u1"
