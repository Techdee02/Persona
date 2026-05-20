from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_profile_build_minimal_payload():
    response = client.post(
        "/profile/build",
        json={
            "user_id": "u2",
            "records": [],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u2"
    assert body["rating_stats"]["count"] == 0


def test_profile_build_missing_user_id():
    response = client.post("/profile/build", json={"records": []})
    assert response.status_code == 400


def test_task_a_stub():
    response = client.post("/task-a/simulate", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "stub"


def test_task_b_stub():
    response = client.post("/task-b/recommend", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "stub"
