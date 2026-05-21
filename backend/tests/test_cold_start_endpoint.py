from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_cold_start_questions_returns_list():
    response = client.get("/cold-start/questions")
    assert response.status_code == 200
    body = response.json()
    assert "questions" in body
    assert len(body["questions"]) == 4


def test_cold_start_answer_builds_profile():
    response = client.post(
        "/cold-start/answer",
        json={
            "user_id": "u_new",
            "answers": [
                {"question_id": "rating_tendency", "answer": "top_marks"},
                {"question_id": "value_priority", "answer": "food_quality"},
                {"question_id": "review_style", "answer": "brief_and_direct"},
                {"question_id": "cultural_register", "answer": "sometimes"},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "u_new"
    assert body["rating_stats"]["mean"] == 4.5
    assert body["value_keywords"]["food"] == 3


def test_cold_start_answer_missing_user_id():
    response = client.post("/cold-start/answer", json={"answers": []})
    assert response.status_code == 400


def test_cold_start_answer_missing_answers():
    response = client.post("/cold-start/answer", json={"user_id": "u1", "answers": []})
    assert response.status_code == 400
