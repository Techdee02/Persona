from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_task_b_recommend_with_query_text():
    response = client.post(
        "/task-b/recommend",
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
            "query_text": "spicy grilled",
            "top_k": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u1"
    assert "recommendations" in body
