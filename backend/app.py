from fastapi import FastAPI, HTTPException, Request, Response
import logging
import uuid

from .data.schema import InteractionRecord
from .logging_utils import configure_logging
from .services.profile_service import ProfileService
from .llm_factory import create_openai_client
from .task_a_service import TaskAService
from .task_b_agent_service import TaskBAgentService
from .task_b_service import TaskBService
from .retrieval import RetrievalItem
import numpy as np

configure_logging()
logger = logging.getLogger("persona.api")

app = FastAPI(title="Persona API", version="0.1.0")
profile_service = ProfileService()
llm_client = create_openai_client()
task_a_service = TaskAService(profile_service=profile_service, llm_client=llm_client)
task_b_service = TaskBService(profile_service=profile_service)
task_b_agent_service = TaskBAgentService(profile_service=profile_service, llm_client=llm_client)


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
def task_a_simulate(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    records = payload.get("records", [])
    target_item = payload.get("target_item", {})
    population_records = payload.get("population_records", None)
    use_llm = bool(payload.get("use_llm", False))

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not target_item:
        raise HTTPException(status_code=400, detail="target_item is required")

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

    parsed_population = None
    if population_records is not None:
        parsed_population = []
        for record in population_records:
            parsed_population.append(
                InteractionRecord(
                    user_id=str(record.get("user_id", user_id)).strip(),
                    item_id=str(record.get("item_id", "")).strip(),
                    rating=float(record.get("rating", 0.0)),
                    review_text=str(record.get("review_text", "")).strip(),
                    timestamp=str(record.get("timestamp", "")).strip() or None,
                    source=str(record.get("source", "")).strip() or "unknown",
                )
            )

    return task_a_service.simulate_review(
        user_id=user_id,
        records=parsed_records,
        target_item=target_item,
        population_records=parsed_population,
        use_llm=use_llm,
    )


@app.post("/task-b/recommend")
def task_b_recommend(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    records = payload.get("records", [])
    query_vectors = payload.get("query_vectors", [])
    candidates = payload.get("candidates", [])
    top_k = int(payload.get("top_k", 10))
    weights = payload.get("weights", None)
    penalties = payload.get("penalties", None)

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not query_vectors:
        raise HTTPException(status_code=400, detail="query_vectors are required")
    if not candidates:
        raise HTTPException(status_code=400, detail="candidates are required")

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

    query_vecs = [np.array(vec, dtype=float) for vec in query_vectors]
    candidate_items = [
        RetrievalItem(
            item_id=str(item.get("item_id", "")).strip(),
            vector=np.array(item.get("vector", []), dtype=float),
            metadata=item.get("metadata", {}),
        )
        for item in candidates
    ]

    return task_b_service.recommend(
        user_id=user_id,
        records=parsed_records,
        query_vectors=query_vecs,
        candidates=candidate_items,
        top_k=top_k,
        weights=weights,
        penalties=penalties,
    )


@app.post("/task-b/agent")
def task_b_agent(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    records = payload.get("records", [])
    query_vectors = payload.get("query_vectors", [])
    candidates = payload.get("candidates", [])
    top_k = int(payload.get("top_k", 10))
    weights = payload.get("weights", None)
    penalties = payload.get("penalties", None)
    use_llm = bool(payload.get("use_llm", False))

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not query_vectors:
        raise HTTPException(status_code=400, detail="query_vectors are required")
    if not candidates:
        raise HTTPException(status_code=400, detail="candidates are required")

    return task_b_agent_service.recommend(
        user_id=user_id,
        records=records,
        query_vectors=query_vectors,
        candidates=candidates,
        top_k=top_k,
        weights=weights,
        penalties=penalties,
        use_llm=use_llm,
    )
