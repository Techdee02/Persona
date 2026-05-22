from fastapi import FastAPI, HTTPException, Request, Response
import logging
import uuid

from .cold_start import COLD_START_QUESTIONS, ColdStartAnswer, bootstrap_profile
from .config import app_config_from_env
from .data.schema import InteractionRecord
from .logging_utils import configure_logging
from .multi_vector_store import MultiVectorStoreService
from .services.profile_service import ProfileService
from .session import session_store
from .llm_factory import create_openai_client
from .task_a_service import TaskAService
from .task_b_agent_service import TaskBAgentService
from .task_b_service import TaskBService
from .vector_store_service import VectorStoreService
from .retrieval import RetrievalItem
import numpy as np

configure_logging()
logger = logging.getLogger("persona.api")

_config = app_config_from_env()

app = FastAPI(title="Persona API", version="0.1.0")
profile_service = ProfileService()
llm_client = create_openai_client()
task_a_service = TaskAService(profile_service=profile_service, llm_client=llm_client)
vector_store_service = VectorStoreService.create(store_path=_config.vector_store_path)
task_b_service = TaskBService(profile_service=profile_service, vector_store_service=vector_store_service)
task_b_agent_service = TaskBAgentService(profile_service=profile_service, llm_client=llm_client)

# Multi-domain store — populated when per-domain paths are configured.
_domain_stores: dict = {}
for _domain, _path in [
    ("yelp", _config.vector_store_path_yelp),
    ("amazon", _config.vector_store_path_amazon),
    ("goodreads", _config.vector_store_path_goodreads),
]:
    if _path:
        _domain_stores[_domain] = VectorStoreService.create(store_path=_path)

multi_vector_store_service: MultiVectorStoreService | None = (
    MultiVectorStoreService(stores=_domain_stores) if _domain_stores else None
)


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


def _parse_records(raw: list, default_user_id: str) -> list:
    return [
        InteractionRecord(
            user_id=str(r.get("user_id", default_user_id)).strip(),
            item_id=str(r.get("item_id", "")).strip(),
            rating=float(r.get("rating", 0.0)),
            review_text=str(r.get("review_text") or r.get("text", "")).strip(),
            timestamp=str(r.get("timestamp", "")).strip() or None,
            source=str(r.get("source", "")).strip() or "unknown",
        )
        for r in raw
    ]


@app.post("/profile/build")
def build_profile_endpoint(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    parsed_records = _parse_records(payload.get("records", []), user_id)
    profile = profile_service.build_profile_cached(user_id, parsed_records)
    return profile.to_dict()


@app.post("/profile/update")
def update_profile_endpoint(payload: dict) -> dict:
    """
    Append new interaction records to a user's profile and return the rebuilt profile.

    The cache uses a content hash of all records as its key, so supplying a
    superset of records always triggers a fresh build and caches the result.
    """
    user_id = str(payload.get("user_id", "")).strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    existing = _parse_records(payload.get("existing_records", []), user_id)
    new = _parse_records(payload.get("new_records", []), user_id)
    if not new:
        raise HTTPException(status_code=400, detail="new_records are required")

    merged = existing + new
    profile = profile_service.build_profile_cached(user_id, merged)
    return {"updated": True, "profile": profile.to_dict()}


@app.post("/task-a/simulate")
def task_a_simulate(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    target_item = payload.get("target_item", {})
    use_llm = bool(payload.get("use_llm", False))

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not target_item:
        raise HTTPException(status_code=400, detail="target_item is required")

    parsed_records = _parse_records(payload.get("records", []), user_id)
    pop_raw = payload.get("population_records", None)
    parsed_population = _parse_records(pop_raw, user_id) if pop_raw is not None else None

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
    query_vectors = payload.get("query_vectors", [])
    candidates = payload.get("candidates", [])
    top_k = int(payload.get("top_k", 10))
    weights = payload.get("weights", None)
    penalties = payload.get("penalties", None)
    query_text = payload.get("query_text", None)
    session_id = payload.get("session_id", None)
    constraints = payload.get("constraints", {})

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not query_text and not query_vectors:
        raise HTTPException(status_code=400, detail="query_text or query_vectors are required")
    if not candidates and not query_text:
        raise HTTPException(status_code=400, detail="candidates are required when query_text is not provided")

    parsed_records = _parse_records(payload.get("records", []), user_id)
    query_vecs = [np.array(vec, dtype=float) for vec in query_vectors]
    candidate_items = [
        RetrievalItem(
            item_id=str(item.get("item_id", "")).strip(),
            vector=np.array(item.get("vector", []), dtype=float),
            metadata=item.get("metadata", {}),
        )
        for item in candidates
    ]

    # Session handling: load or create, apply constraints and excluded IDs.
    session = session_store.get_or_create(user_id, session_id) if session_id is not None else None
    if session and constraints:
        session.apply_constraints(constraints)

    effective_top_k = top_k + len(session.excluded_ids) if session else top_k

    result = task_b_service.recommend(
        user_id=user_id,
        records=parsed_records,
        query_vectors=query_vecs,
        candidates=candidate_items,
        top_k=effective_top_k,
        weights=weights,
        penalties=penalties,
        query_text=query_text,
    )

    if session:
        # Filter out previously seen items then trim to requested top_k.
        filtered = [
            r for r in result.get("recommendations", [])
            if r.get("item_id") not in session.excluded_ids
        ][:top_k]
        returned_ids = [r["item_id"] for r in filtered]
        session.record_recommendations(returned_ids)
        result = {**result, "recommendations": filtered, "session_id": session.session_id}

    return result


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


@app.get("/cold-start/questions")
def cold_start_questions() -> dict:
    return {"questions": COLD_START_QUESTIONS}


@app.post("/cold-start/answer")
def cold_start_answer(payload: dict) -> dict:
    user_id = str(payload.get("user_id", "")).strip()
    raw_answers = payload.get("answers", [])

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not raw_answers:
        raise HTTPException(status_code=400, detail="answers are required")

    answers = [
        ColdStartAnswer(
            question_id=str(ans.get("question_id", "")).strip(),
            answer=str(ans.get("answer", "")).strip(),
        )
        for ans in raw_answers
    ]

    profile = bootstrap_profile(user_id, answers)
    return profile.to_dict()
