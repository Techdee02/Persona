"""Tests for structured LLM prompt builders."""
from backend.llm_prompts import build_task_a_prompt, build_task_b_prompt


def _profile(code_switching=False, ni_index=0.0):
    return {
        "rating_stats": {"mean": 4.0, "std_dev": 0.5, "count": 10},
        "stylometry": {"avg_word_count": 80, "vocab_richness": 0.6},
        "value_keywords": {"food": 5, "service": 3, "price": 1, "atmosphere": 0},
        "trajectory": {"delta_rating": 0.4, "early_mean_rating": 3.6, "recent_mean_rating": 4.0},
        "cultural_signals": {
            "code_switching_detected": code_switching,
            "nigerian_english_index": ni_index,
            "pidgin_term_hits": 2 if code_switching else 0,
        },
    }


def test_task_a_prompt_returns_two_messages():
    msgs = build_task_a_prompt(_profile(), {"name": "Chicken Republic"})
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"


def test_task_a_system_includes_nigerian_english_note_when_detected():
    msgs = build_task_a_prompt(_profile(code_switching=True, ni_index=0.5), {"name": "Item"})
    system = msgs[0]["content"]
    assert "Nigerian English" in system


def test_task_a_system_no_nigerian_note_when_not_detected():
    msgs = build_task_a_prompt(_profile(), {"name": "Item"})
    system = msgs[0]["content"]
    assert "Nigerian English" not in system


def test_task_a_user_contains_item_name():
    msgs = build_task_a_prompt(_profile(), {"name": "Suya Spot"})
    assert "Suya Spot" in msgs[1]["content"]


def test_task_a_user_mentions_value_priorities():
    msgs = build_task_a_prompt(_profile(), {"name": "X"})
    assert "food" in msgs[1]["content"]


def test_task_b_prompt_returns_two_messages():
    axes = [{"name": "food", "weight": 0.6, "rationale": "Mentioned in 5 reviews"}]
    candidates = [{"item_id": "abc", "score": 0.8, "metadata": {"food": True}}]
    msgs = build_task_b_prompt(_profile(), axes, candidates)
    assert len(msgs) == 2


def test_task_b_system_includes_cultural_note_when_detected():
    msgs = build_task_b_prompt(_profile(code_switching=True), [], [])
    assert "Nigerian" in msgs[0]["content"]


def test_task_b_user_includes_session_context():
    msgs = build_task_b_prompt(_profile(), [], [], session_context="Turn 2. Excluded: abc.")
    assert "Turn 2" in msgs[1]["content"]
