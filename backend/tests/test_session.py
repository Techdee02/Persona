"""Tests for session state management."""
import time
import pytest

from backend.session import SessionState, SessionStore


def test_session_create_and_retrieve():
    store = SessionStore()
    state = store.create("user1")
    assert state.user_id == "user1"
    assert state.turn == 0
    assert len(state.excluded_ids) == 0

    fetched = store.get(state.session_id)
    assert fetched is not None
    assert fetched.session_id == state.session_id


def test_session_records_recommendations():
    store = SessionStore()
    state = store.create("user2")
    state.record_recommendations(["item_a", "item_b"])
    assert state.turn == 1
    assert "item_a" in state.excluded_ids
    assert "item_b" in state.excluded_ids


def test_session_get_or_create_returns_existing():
    store = SessionStore()
    state = store.create("user3", session_id="fixed-id")
    state.record_recommendations(["x"])

    same = store.get_or_create("user3", "fixed-id")
    assert same.session_id == "fixed-id"
    assert "x" in same.excluded_ids


def test_session_get_or_create_creates_new_when_missing():
    store = SessionStore()
    state = store.get_or_create("user4", "nonexistent-id")
    assert state.user_id == "user4"
    assert state.turn == 0


def test_session_expires():
    store = SessionStore(ttl=0)
    state = store.create("user5")
    sid = state.session_id
    time.sleep(0.01)
    assert store.get(sid) is None


def test_session_context_summary():
    store = SessionStore()
    state = store.create("user6")
    state.record_recommendations(["a", "b"])
    state.apply_constraints({"cuisine": "Nigerian"})
    summary = state.context_summary()
    assert "Turn 1" in summary
    assert "cuisine=Nigerian" in summary


def test_session_delete():
    store = SessionStore()
    state = store.create("user7")
    sid = state.session_id
    assert store.delete(sid) is True
    assert store.get(sid) is None
    assert store.delete(sid) is False
