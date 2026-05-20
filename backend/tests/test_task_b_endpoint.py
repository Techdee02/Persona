from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_task_b_recommend_minimal_payload():
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
            "query_vectors": [[1.0, 0.0]],
            "candidates": [
                {"item_id": "c1", "vector": [1.0, 0.0], "metadata": {"name": "A"}},
                {"item_id": "c2", "vector": [0.0, 1.0], "metadata": {"name": "B"}},
            ],
            "top_k": 1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u1"
    assert len(body["recommendations"]) == 1
    assert body["recommendations"][0]["item_id"] == "c1"
