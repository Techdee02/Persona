# Backend AI/ML Phases

Owner: Backend AI/ML Developer
Last updated: 2026-05-22

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

## Phase 5: Operational Readiness ✓ Complete

Goal: get the real-data vector store live, fix deployment blockers, and validate the full LLM pipeline end-to-end.

Deliverables (all delivered):
- Streaming JSONL persistence — fixed silent OOM on large stores ✓
- Streaming batched ingestion + --limit / --batch-size CLI flags ✓
- python-dotenv integration — .env auto-loaded at startup ✓
- Logging formatter fix — trace_id filter correctly attached to handlers ✓
- .gitignore extended — large data/vector store files excluded ✓
- 50k Yelp vector store built and end-to-end validated ✓ (expanded to 200k in Phase 6)
- Dockerfile COPY paths corrected; backend/services and backend/tests __init__.py added ✓
- Record parser accepts both `review_text` and `text` field names ✓
- Agent plan guaranteed to run all 4 steps even when LLM returns fewer ✓
- Full LLM end-to-end validation (gpt-4o): Task A culturally-calibrated review generation
  and Task B 4-step agent pipeline both confirmed working ✓

Acceptance criteria:
- API loads Yelp vector store at startup ✓
- /task-b/recommend returns real Yelp recommendations with scored results ✓
- /task-a/simulate use_llm=true: Nigerian English detected, pidgin review generated ✓
- /task-b/agent use_llm=true: all 4 steps execute, cultural_register axis extracted ✓
- All 8 endpoints tested and responding correctly ✓
- 114 tests passing after all fixes ✓
- Docker deployment artifacts correct and all source files tracked in git ✓

## Phase 6: Dense Vector Store ✓ Complete

Goal: expand the Yelp vector store to 200k records for denser retrieval coverage and add
a resilient multi-checkpoint ingestion workflow.

Deliverables (all delivered):
- Multi-checkpoint ingestion script (ingest_checkpoints.py) — single-pass, saves at 50k/100k/150k/200k ✓
- 200k Yelp vector store built in 89 minutes (37–38 rec/s, batch_size=512) ✓
- Live progress monitoring via log file (tail -f /tmp/persona_checkpoints/ingest.log) ✓
- Graceful Ctrl+C handling — partial store saved before exit ✓
- .env wired to 200k store; API startup confirmed (load time ~30s) ✓
- End-to-end validation: /task-b/recommend returns real Yelp items, cosine 0.60–0.69 ✓
- All docs updated to reflect 200k store ✓

Acceptance criteria:
- API loads 200k-item Yelp vector store at startup ✓
- /task-b/recommend returns real Yelp recommendations with scored results ✓
- Checkpoint files at 50k, 100k, 150k, 200k all valid and independently loadable ✓

## Phase Risks and Mitigations

- LLM instability: deterministic mode, caching, and structured prompts mitigate this
- Data sparsity: cold-start bootstrap profile handles new users without history
- Latency: profile TTL+LRU cache; template path avoids LLM when not needed
- Multi-worker cache consistency: current in-process cache; Redis upgrade path documented
- Vector store disk space: JSONL streaming write/read; stores excluded from git via .gitignore
- LLM partial tool-call responses: agent plan fill-in ensures all 4 steps always execute
- Codespace restart wipes /tmp: multi-checkpoint script saves to /workspaces after each run

## Phase 7: Production Deployment ✓ Complete

Goal: deploy the full stack to a public HTTPS endpoint for the hackathon judges.

Deliverables (all delivered):
- DigitalOcean Droplet (Ubuntu 22.04, 2 GB RAM, lon1) ✓
- Vector store uploaded to DO Spaces (persona-space / lon1, 1.6 GB) ✓
- entrypoint.sh auto-download validated on first container boot ✓
- DuckDNS subdomain: personabackend.duckdns.org → 188.166.149.75 ✓
- Let's Encrypt SSL cert via Certbot (expires 2026-08-21) ✓
- Nginx HTTPS reverse proxy live ✓
- Vercel frontend wired to HTTPS backend (VITE_API_URL updated) ✓
- Full deployment guide: docs/DEPLOYMENT.md ✓

Acceptance criteria:
- https://personabackend.duckdns.org/health returns {"status":"ok"} ✓
- Frontend at persona-eight-flax.vercel.app calls backend with no CORS/mixed-content errors ✓
- Vector store auto-downloads from Spaces on fresh container boot ✓

## Open Questions

- BERTScore: include in final evaluation report? (requires `bert-score` install)
- Cross-domain retrieval domain weights: should Yelp or Amazon score higher for restaurant queries?
- SSL auto-renewal: add monthly cron job on droplet for `certbot renew`?
