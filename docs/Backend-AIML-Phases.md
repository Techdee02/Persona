# Backend AI/ML Phases

Owner: Backend AI/ML Developer
Last updated: 2026-05-21

This document breaks backend and AI/ML work into three phases: pipeline readiness, production hardening, and full-grade refinement.

## Phase 1: Working Pipeline

Goal: get an end-to-end system running with minimum viable quality and stable outputs.

Deliverables:
- Data loader for Yelp/Amazon/Goodreads with temporal split
- Signal extraction for rating stats, stylometry, and value keywords
- Initial psychological profile JSON schema
- Task A: rating prediction + review generation pipeline (single pass)
- Task B: basic retrieval + ranking pipeline
- Simple cold-start flow with 3 to 4 questions
- FastAPI endpoints wired end-to-end
- Baseline evaluation scripts and first metrics run

Acceptance criteria:
- Task A and Task B endpoints respond reliably for a demo user
- Outputs include reasoning traces and cultural flags
- One-click local run via Docker Compose

## Phase 2: Standard and Production-Ready

Goal: improve stability, reproducibility, and evaluation quality without changing core logic.

Deliverables:
- Robust data validation, schema checks, and error handling
- Deterministic mode for demos and judging
- Profile caching and request-level tracing
- Rate limiting and safe retry policy for LLM calls
- Multi-angle retrieval for Task B
- Calibration refinement for rating bias
- Structured logs for trace replay and debugging
- Evaluation scripts updated with clear baselines

Acceptance criteria:
- P95 latency targets met (Task A under 2.5s, Task B under 3.5s)
- Deterministic outputs when requested
- Evaluation runs are reproducible

## Phase 3: Full-Grade Refinement ✓ Complete

Goal: maximize scoring and polish with additional features and deeper modeling.

Deliverables (all delivered):
- Living trajectory features (early vs recent behavior) ✓
- Nigerian English detection and code-switching preservation ✓
- Enhanced preference axis extraction ✓
- Deliberative scoring improvements with per-candidate metadata matching ✓
- Agent/tool-calling scaffold with $ref argument wiring ✓
- Vector store persistence and ingestion CLI ✓

Acceptance criteria:
- Clear lift over Phase 2 baselines in key metrics ✓
- Outputs show culturally grounded explanations ✓

## Phase 4: Competition-Grade Refinement ✓ Complete

Goal: production-quality outputs, deep evaluation, and solution paper artifacts.

Deliverables (all delivered):
- Bug fixes: deliberative scoring, agent plan wiring, task_b_service query_text path ✓
- Cold-start system (4 elicitation questions + bootstrap_profile) ✓
- Template-based review generator with cultural register ✓
- LLM retry with exponential backoff ✓
- Dataset row validation in loaders ✓
- Full evaluation system: RMSE, ROUGE-L, NDCG@k, Hit Rate@k, baselines ✓
- Ablation study runner: zero each profile layer, report RMSE/NDCG delta ✓
- Per-user breakdown by history length and cultural signal ✓
- Richer Task A reasoning trace derived from all signal layers ✓
- Structured LLM prompts with cultural calibration (Task A + Task B) ✓
- Session state for multi-turn Task B recommendations ✓
- Cross-domain retrieval via MultiVectorStoreService ✓
- POST /profile/update endpoint ✓
- Docker + docker-compose ✓
- 114 tests, all passing ✓
- Comprehensive architecture and API documentation ✓

Acceptance criteria:
- All endpoints respond with auditable reasoning traces ✓
- Evaluation scripts ready for dataset runs ✓
- Ablation results ready for the solution paper ✓
- Full test coverage across all modules ✓

## Phase Risks and Mitigations

- LLM instability: deterministic mode, caching, and structured prompts mitigate this
- Data sparsity: cold-start bootstrap profile handles new users without history
- Latency: profile TTL+LRU cache; template path avoids LLM when not needed
- Multi-worker cache consistency: current in-process cache; Redis upgrade path documented

## Open Questions

- Which LLM is final for demo and judging?
- BERTScore: include in final evaluation report? (requires `bert-score` install)
- Cross-domain retrieval domain weights: should Yelp or Amazon score higher for restaurant queries?
