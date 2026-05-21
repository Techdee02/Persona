"""
Structured prompt builders for Task A (review generation) and Task B (agent planning).

All public functions return a list of OpenAI-compatible chat message dicts.
Cultural calibration is applied automatically when Nigerian English is detected.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def build_task_a_prompt(
    profile: Dict[str, object],
    target_item: Dict[str, object],
) -> List[Dict[str, str]]:
    """Return messages for Task A: generate a review in the user's voice."""
    system = _task_a_system(profile)
    user = _task_a_user(profile, target_item)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_task_b_prompt(
    profile: Dict[str, object],
    axes: List[Dict[str, object]],
    candidates: List[Dict[str, object]],
    session_context: Optional[str] = None,
) -> List[Dict[str, str]]:
    """Return messages for Task B: rank candidates and explain recommendations."""
    system = _task_b_system(profile)
    user = _task_b_user(profile, axes, candidates, session_context)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Task A ────────────────────────────────────────────────────────────────────

def _task_a_system(profile: Dict[str, object]) -> str:
    cultural = profile.get("cultural_signals", {})
    cs_detected = cultural.get("code_switching_detected", False)
    ni_index = float(cultural.get("nigerian_english_index", 0.0))

    base = (
        "You are a review-writing assistant that generates authentic, personalised "
        "restaurant and product reviews. Your output must faithfully reflect the "
        "user's documented writing style, rating tendencies, and cultural register. "
        "Write only the review text — no preamble, no explanation."
    )

    if cs_detected or ni_index > 0.2:
        base += (
            "\n\nIMPORTANT: This user writes in Nigerian English and occasionally "
            "uses Pidgin expressions (e.g., 'na wa', 'e don do', 'omo'). "
            "Incorporate this register naturally — do not exaggerate or stereotype. "
            "Match the user's typical code-switching frequency."
        )
    return base


def _task_a_user(
    profile: Dict[str, object],
    target_item: Dict[str, object],
) -> str:
    rating_stats = profile.get("rating_stats", {})
    stylometry = profile.get("stylometry", {})
    value_kw = profile.get("value_keywords", {})
    trajectory = profile.get("trajectory", {})
    cultural = profile.get("cultural_signals", {})

    top_values = sorted(value_kw.items(), key=lambda kv: kv[1], reverse=True)[:3]
    value_str = ", ".join(f"{k} ({v})" for k, v in top_values) or "none recorded"

    traj_note = ""
    delta = float(trajectory.get("delta_rating", 0.0))
    if abs(delta) >= 0.3:
        traj_note = (
            f" Their ratings have {'improved' if delta > 0 else 'declined'} recently "
            f"(delta {delta:+.2f}), so the tone should reflect that drift."
        )

    return (
        f"USER PROFILE SUMMARY\n"
        f"- Average rating: {rating_stats.get('mean', 3.0):.2f}/5 "
        f"(σ={rating_stats.get('std_dev', 0.0):.2f}, n={rating_stats.get('count', 0)})\n"
        f"- Typical review length: ~{stylometry.get('avg_word_count', 80):.0f} words\n"
        f"- Vocab richness: {stylometry.get('vocab_richness', 0.5):.2f}\n"
        f"- Top value priorities: {value_str}\n"
        f"- Nigerian English index: {cultural.get('nigerian_english_index', 0.0):.2f}\n"
        f"{traj_note}\n\n"
        f"TARGET ITEM\n"
        f"Name: {target_item.get('name', 'Unknown')}\n"
        f"Category: {target_item.get('categories', target_item.get('category', 'N/A'))}\n"
        f"Additional metadata: {_format_metadata(target_item)}\n\n"
        "Write a review for this item in the user's voice. "
        "Match their typical length and vocabulary style. "
        "Focus on the value dimensions they care about most."
    )


# ── Task B ────────────────────────────────────────────────────────────────────

def _task_b_system(profile: Dict[str, object]) -> str:
    cultural = profile.get("cultural_signals", {})
    cs_detected = cultural.get("code_switching_detected", False)

    base = (
        "You are a personalised recommendation agent. "
        "Given a user's psychological profile and a list of candidate items, "
        "rank the items and provide brief per-item explanations grounded in the user's "
        "stated preferences, rating tendencies, and cultural context. "
        "Return a JSON object with key 'ranked_items': a list ordered best-to-worst, "
        "each entry containing 'item_id' and 'explanation'."
    )

    if cs_detected:
        base += (
            "\n\nThis user identifies with Nigerian cultural context. "
            "Acknowledge culturally relevant signals (e.g., Nigerian cuisine, local service norms) "
            "in your explanations where appropriate."
        )
    return base


def _task_b_user(
    profile: Dict[str, object],
    axes: List[Dict[str, object]],
    candidates: List[Dict[str, object]],
    session_context: Optional[str],
) -> str:
    rating_stats = profile.get("rating_stats", {})
    cultural = profile.get("cultural_signals", {})

    axes_str = "\n".join(
        f"  - {ax.get('name')} (weight={ax.get('weight', 0):.2f}): {ax.get('rationale', '')}"
        for ax in axes[:5]
    ) or "  (none extracted)"

    candidates_str = "\n".join(
        f"  {i+1}. item_id={c.get('item_id', '?')} score={c.get('score', 0):.3f} "
        f"metadata={c.get('metadata', {})}"
        for i, c in enumerate(candidates[:20])
    )

    context_block = f"\nSESSION CONTEXT\n{session_context}\n" if session_context else ""

    return (
        f"USER PROFILE\n"
        f"- Mean rating: {rating_stats.get('mean', 3.0):.2f}/5\n"
        f"- Nigerian English index: {cultural.get('nigerian_english_index', 0.0):.2f}\n"
        f"- Code-switching: {cultural.get('code_switching_detected', False)}\n\n"
        f"PREFERENCE AXES\n{axes_str}\n"
        f"{context_block}\n"
        f"CANDIDATES (retrieval score shown)\n{candidates_str}\n\n"
        "Rank these candidates for this user. "
        "Return only the JSON object described in the system prompt."
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_metadata(item: Dict[str, object]) -> str:
    skip = {"name", "categories", "category"}
    pairs = [(k, v) for k, v in item.items() if k not in skip]
    if not pairs:
        return "none"
    return "; ".join(f"{k}={v}" for k, v in pairs[:5])
