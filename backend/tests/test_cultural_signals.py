from backend.data.schema import InteractionRecord
from backend.cultural_signals import extract_cultural_signals


def _record(text: str) -> InteractionRecord:
    return InteractionRecord(
        user_id="u1",
        item_id="i1",
        rating=4.0,
        review_text=text,
        timestamp="2021-01-01",
        source="yelp",
    )


def test_extract_cultural_signals_no_text():
    signals = extract_cultural_signals([_record("")])
    assert signals.nigerian_english_index == 0.0
    assert signals.code_switching_detected is False


def test_extract_cultural_signals_detects_pidgin():
    signals = extract_cultural_signals([_record("Abeg the suya na correct")])
    assert signals.pidgin_term_hits >= 2
    assert signals.code_switching_detected is True
