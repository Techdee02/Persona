from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "X-Trace-Id" in response.headers


def test_profile_build():
    response = client.post(
        "/profile/build",
        json={
            "user_id": "u1",
            "records": [
                {
                    "item_id": "i1",
                    "rating": 4.0,
                    "review_text": "Great food",
                    "timestamp": "2021-01-01",
                    "source": "yelp",
                }
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u1"
    assert body["rating_stats"]["count"] == 1
