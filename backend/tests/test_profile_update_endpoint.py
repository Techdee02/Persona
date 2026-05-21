"""Tests for the POST /profile/update endpoint."""
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

_RECORD = {
    "item_id": "restaurant_1",
    "rating": 4.5,
    "review_text": "Really enjoyed the jollof rice here.",
    "timestamp": "2024-01-01",
    "source": "yelp",
}


def test_profile_update_returns_updated_flag():
    resp = client.post("/profile/update", json={
        "user_id": "u_update_1",
        "existing_records": [_RECORD],
        "new_records": [{"item_id": "restaurant_2", "rating": 3.0,
                         "review_text": "Decent.", "timestamp": "2024-02-01",
                         "source": "yelp"}],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["updated"] is True
    assert "profile" in body


def test_profile_update_missing_user_id_returns_400():
    resp = client.post("/profile/update", json={
        "existing_records": [_RECORD],
        "new_records": [_RECORD],
    })
    assert resp.status_code == 400


def test_profile_update_missing_new_records_returns_400():
    resp = client.post("/profile/update", json={
        "user_id": "u_update_2",
        "existing_records": [_RECORD],
        "new_records": [],
    })
    assert resp.status_code == 400


def test_profile_update_empty_existing_records_still_works():
    resp = client.post("/profile/update", json={
        "user_id": "u_update_3",
        "existing_records": [],
        "new_records": [_RECORD],
    })
    assert resp.status_code == 200
    assert resp.json()["updated"] is True
