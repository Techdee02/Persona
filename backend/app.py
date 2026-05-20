from fastapi import FastAPI, HTTPException, Request, Response
import logging
import uuid

from .data.schema import InteractionRecord
from .logging_utils import configure_logging
from .services.profile_service import ProfileService

configure_logging()
logger = logging.getLogger("persona.api")

app = FastAPI(title="Persona API", version="0.1.0")
profile_service = ProfileService()


@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    request.state.trace_id = trace_id

    response: Response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    logger.info("request_completed", extra={"trace_id": trace_id})
    return response


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
