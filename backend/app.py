from fastapi import FastAPI, HTTPException

from .data.schema import InteractionRecord
from .services.profile_service import ProfileService

app = FastAPI(title="Persona API", version="0.1.0")
profile_service = ProfileService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/profile/build")
def build_profile_endpoint(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    records = payload.get("records", [])

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    parsed_records = []
    for record in records:
        parsed_records.append(
            InteractionRecord(
                user_id=user_id,
                item_id=str(record.get("item_id", "")).strip(),
                rating=float(record.get("rating", 0.0)),
                review_text=str(record.get("review_text", "")).strip(),
                timestamp=str(record.get("timestamp", "")).strip() or None,
                source=str(record.get("source", "")).strip() or "unknown",
            )
        )

    profile = profile_service.build_profile_cached(user_id, parsed_records)
    return profile.to_dict()


@app.post("/task-a/simulate")
def task_a_stub() -> dict:
    return {
        "status": "stub",
        "message": "Task A pipeline will be added in Phase 2.",
    }


@app.post("/task-b/recommend")
def task_b_stub() -> dict:
    return {
        "status": "stub",
        "message": "Task B pipeline will be added in Phase 2.",
    }
