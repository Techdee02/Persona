from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_task_a_simulate_minimal_payload():
    response = client.post(
        "/task-a/simulate",
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
            "target_item": {"item_id": "i2", "name": "Target"},
            "use_llm": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u1"
    assert "predicted_rating" in body
    assert body["target_item"]["item_id"] == "i2"
