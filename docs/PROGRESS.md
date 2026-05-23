# Progress Log

This document tracks task-by-task progress for Persona backend/AI-ML implementation.

## Phase 1 Checklist

- [x] Task 1: Data loaders + temporal split
- [x] Task 2: Signal extraction (rating stats, stylometry, value keywords)
- [x] Task 3: Initial profile schema + profile builder
- [x] Task 4: FastAPI endpoints wiring (profile + task stubs)
- [x] Task 5: Smoke tests

## Phase 2 Checklist

- [x] Task 1: Deterministic mode + profile caching
- [x] Task 2: Structured logging + tracing
- [x] Task 3: Multi-angle retrieval (vector-based)
- [x] Task 4: Rating calibration refinement

## Phase 3 Checklist

- [x] Task 1: Living trajectory features
- [x] Task 2: Nigerian English detection signals
- [x] Task 3: Preference axis extraction
- [x] Task 4: Deliberative scoring utility
- [x] Task 5: Agent/tool-calling scaffold
- [x] Task 6: Task B endpoint integration (non-LLM)
- [x] Task 7: Agent tool definitions
- [x] Task 8: Task A endpoint integration (non-LLM)
- [x] Task 9: OpenAI LLM scaffold and agent endpoint
- [x] Task 10: Task A LLM review scaffold
- [x] Task 11: Embeddings pipeline and vector store
- [x] Task 12: Embedding ingestion script
- [x] Task 13: Task B vector store integration
- [x] Task 14: Dataset-specific ingestion helpers
- [x] Task 15: Vector store persistence
- [x] Task 16: Dataset ingestion CLI

## Phase 4 Checklist (Full-Grade Refinement)

- [x] Task 1: Bug fixes — deliberative scoring, agent plan wiring, task_b_service query_text path
- [x] Task 2: Cold-start system (4 elicitation questions + bootstrap_profile)
- [x] Task 3: Template-based review generator (generate_review from profile signals)
- [x] Task 4: LLM retry with exponential backoff
- [x] Task 5: Dataset row validation in loaders
- [x] Task 6: Evaluation metrics (RMSE, ROUGE-L, NDCG@k, Hit Rate@k, baselines)
- [x] Task 7: Task A evaluation runner (CLI)
- [x] Task 8: Task B evaluation runner with ablation support and per-user breakdown
- [x] Task 9: Ablation study runner (zero each profile layer, report RMSE/NDCG delta)
- [x] Task 10: Richer Task A reasoning trace (_build_reasoning from profile signals)
- [x] Task 11: Structured LLM prompts module (culturally-calibrated Task A + Task B prompts)
- [x] Task 12: Session state for multi-turn Task B (SessionState, SessionStore, TTL+LRU)
- [x] Task 13: Cross-domain retrieval (MultiVectorStoreService, per-domain normalisation)
- [x] Task 14: BERTScore + per-user breakdown in Task A eval runner
- [x] Task 15: POST /profile/update endpoint
- [x] Task 16: Docker + docker-compose
- [x] Task 17: Comprehensive backend architecture documentation
- [x] Task 18: 114 tests passing (all modules covered)

## Task Logs

### Task 1: Data loaders + temporal split

Status: Done

Notes:
- Added dataset path config via env vars and .env.example
- Implemented loaders for Yelp, Amazon, Goodreads with default field maps
- Implemented per-user temporal split utility
- Added pytest smoke tests for loaders and split
- Tests: python -m pytest backend/tests

### Task 2: Signal extraction (rating stats, stylometry, value keywords)

Status: Done

Notes:
- Added rating stats and stylometry extraction
- Added value keyword counters for food, service, price, atmosphere
- Tests: python -m pytest backend/tests

### Task 3: Initial profile schema + profile builder

Status: Done

Notes:
- Added PsychologicalProfile schema and builder
- Includes rating stats, stylometry, and value keyword signals
- Tests: python -m pytest backend/tests

### Task 4: FastAPI endpoints wiring (profile + task stubs)

Status: Done

Notes:
- Added FastAPI app with health, profile build, and task stubs
- Added API smoke tests for health and profile build
- Tests: python -m pytest backend/tests

### Task 5: Smoke tests

Status: Done

Notes:
- Added integration smoke tests for profile and task stubs
- Tests: python -m pytest backend/tests

### Phase 2 Task 1: Deterministic mode + profile caching

Status: Done

Notes:
- Added TTL cache for profiles with max size and TTL controls
- Added app config for deterministic mode and cache settings
- Profile endpoint now uses cache-aware service
- Tests: python -m pytest backend/tests

### Phase 2 Task 2: Structured logging + tracing

Status: Done

Notes:
- Added trace id middleware with response header
- Added logging config with trace id filter
- Tests: python -m pytest backend/tests

### Phase 2 Task 3: Multi-angle retrieval (vector-based)

Status: Done

Notes:
- Added vector-based multi-angle retrieval with cosine similarity
- Supports weighted query vectors
- Tests: python -m pytest backend/tests

### Phase 2 Task 4: Rating calibration refinement

Status: Done

Notes:
- Added rating calibration using user vs population distributions
- Provides calibrated rating with clamping
- Tests: python -m pytest backend/tests

### Phase 3 Task 1: Living trajectory features

Status: Done

Notes:
- Added trajectory stats comparing early vs recent behavior
- Integrated trajectory into the psychological profile
- Tests: python -m pytest backend/tests

### Phase 3 Task 2: Nigerian English detection signals

Status: Done

Notes:
- Added cultural signal extraction with pidgin term detection
- Added Nigerian English index and code-switching flag to profile
- Tests: python -m pytest backend/tests

### Phase 3 Task 3: Preference axis extraction

Status: Done

Notes:
- Added preference axis extraction from profile signals
- Includes value priorities, rating bias, and cultural register
- Tests: python -m pytest backend/tests

### Phase 3 Task 4: Deliberative scoring utility

Status: Done

Notes:
- Added deliberative scoring helper with axis weighting and penalties
- Generates explanation snippets for ranking decisions
- Tests: python -m pytest backend/tests

### Phase 3 Task 5: Agent/tool-calling scaffold

Status: Done

Notes:
- Added tool registry and orchestration skeleton
- Supports ordered tool calls and result aggregation
- Tests: python -m pytest backend/tests

### Phase 3 Task 6: Task B endpoint integration (non-LLM)

Status: Done

Notes:
- Wired Task B endpoint to use axes, retrieval, and deliberative scoring
- Added endpoint test with vector payload
- Tests: python -m pytest backend/tests

### Phase 3 Task 7: Agent tool definitions

Status: Done

Notes:
- Added tool registry definitions for profile, axes, retrieval, scoring
- Added basic registry test
- Tests: python -m pytest backend/tests

### Phase 3 Task 8: Task A endpoint integration (non-LLM)

Status: Done

Notes:
- Wired Task A endpoint to rating calibration and profile stats
- Added endpoint test with target item payload
- Tests: python -m pytest backend/tests

### Phase 3 Task 9: OpenAI LLM scaffold and agent endpoint

Status: Done

Notes:
- Added OpenAI client scaffolding and env config
- Added Task B agent endpoint with optional LLM planning
- Tests: python -m pytest backend/tests

### Phase 3 Task 10: Task A LLM review scaffold

Status: Done

Notes:
- Added optional LLM review generation for Task A
- Endpoint supports use_llm flag with OpenAI client
- Tests: python -m pytest backend/tests

### Phase 3 Task 11: Embeddings pipeline and vector store

Status: Done

Notes:
- Added sentence-transformers embedding helper
- Added in-memory vector store for local retrieval
- Tests: python -m pytest backend/tests

### Phase 3 Task 12: Embedding ingestion script

Status: Done

Notes:
- Added JSONL ingestion to build vector store from dataset fields
- Added ingestion smoke test
- Tests: python -m pytest backend/tests

### Phase 3 Task 13: Task B vector store integration

Status: Done

Notes:
- Added vector store service for embedding-based queries
- Task B endpoint accepts query_text for vector store retrieval
- Tests: python -m pytest backend/tests

### Phase 3 Task 14: Dataset-specific ingestion helpers

Status: Done

Notes:
- Added dataset-specific ingestion helpers for Yelp/Amazon/Goodreads
- Added ingestion smoke test
- Tests: python -m pytest backend/tests

### Phase 3 Task 15: Vector store persistence

Status: Done

Notes:
- Added save/load helpers for vector store JSON snapshots
- Added persistence smoke test
- Tests: python -m pytest backend/tests

### Phase 3 Task 16: Dataset ingestion CLI

Status: Done

Notes:
- Added CLI to ingest dataset JSONL and persist vector store
- Added CLI smoke test
- Tests: python -m pytest backend/tests

---

## Phase 4 Task Logs

### Phase 4 Task 1: Bug fixes

Status: Done

Notes:
- deliberative_scoring.py: fixed global-constant axis_score to per-candidate metadata matching
- task_b_agent_service.py: LLM dead-code fixed; score_candidates now wired via $ref
- agent_tool_defs.py: _score_candidates now converts dict/list axes to PreferenceAxis objects
- task_b_service.py: query_text path now uses vector store results directly (no zero-vector bypass)
- data/split.py: timestamp_key made public; trajectory.py updated to import it
- Tests: python -m pytest backend/tests

### Phase 4 Task 2: Cold-start system

Status: Done

Notes:
- Created backend/cold_start.py with 4 elicitation questions and signal map
- bootstrap_profile() returns complete PsychologicalProfile (count=0, zero trajectory)
- Added GET /cold-start/questions and POST /cold-start/answer endpoints
- 7 unit tests + 4 endpoint tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 3: Template-based review generator

Status: Done

Notes:
- Created backend/review_generator.py with sentiment-based openers, value phrases, pidgin closers
- Cultural closer used when code_switching_detected; trimmed to 1.5× avg_review_length
- seed parameter for deterministic output
- Wired into TaskAService replacing the previous stub string
- 7 unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 4: LLM retry with exponential backoff

Status: Done

Notes:
- backend/llm_client.py: 3 attempts, 1s→2s→4s delay
- Catches RateLimitError and APIStatusError with codes {429,500,502,503,504}
- Non-retryable errors (400, 401) re-raised immediately
- Tests: python -m pytest backend/tests

### Phase 4 Task 5: Dataset row validation

Status: Done

Notes:
- backend/data/loaders.py: _row_to_record returns (record, error_str) tuple
- Validates: non-empty user_id, non-empty item_id, parseable float rating, rating in [0.0, 5.0]
- Logs WARNING with total skip count per file
- 4 unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 6–8: Evaluation system

Status: Done

Notes:
- backend/evaluation/metrics.py: RMSE, ROUGE-L (LCS-based pure Python), NDCG@k, Hit Rate@k
- backend/evaluation/task_a_eval.py: CLI runner with temporal split
- backend/evaluation/task_b_eval.py: CLI runner with vector store + deliberative scoring
- Both runners updated with per-user breakdown (sparse/medium/dense + cultural signal)
- task_b_eval supports ablate_layer parameter for ablation runner
- 13 metric unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 9: Ablation study runner

Status: Done

Notes:
- backend/evaluation/ablation.py: zeroes each profile layer in turn
- Re-runs Task A (RMSE, ROUGE-L) and Task B (NDCG, Hit Rate) for each ablated profile
- Reports delta vs full model for all four metrics
- CLI: python -m backend.evaluation.ablation --records ... --store ... --k 10
- Tests: python -m pytest backend/tests

### Phase 4 Task 10: Richer Task A reasoning trace

Status: Done

Notes:
- backend/task_a_service.py: _build_reasoning() derives detailed string from all signal layers
- Covers: calibration direction, top preference axes with weights, trajectory drift (when ≥0.3),
  stylometry fingerprint, cultural register (when code-switching detected)
- 7 unit tests (test_task_a_reasoning.py)
- Tests: python -m pytest backend/tests

### Phase 4 Task 11: Structured LLM prompts module

Status: Done

Notes:
- backend/llm_prompts.py: build_task_a_prompt(), build_task_b_prompt()
- System prompts adapt based on code_switching_detected and nigerian_english_index
- Task A user message includes structured profile summary + target item block
- Task B user message includes axes, session context, candidate list
- Wired into task_a_service (LLM path) and task_b_agent_service
- 8 unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 12: Session state for multi-turn Task B

Status: Done

Notes:
- backend/session.py: SessionState, SessionStore with TTL+LRU eviction
- excluded_ids accumulate across turns; constraints merged per request
- session_id support in POST /task-b/recommend: get_or_create, filter, update
- context_summary() for LLM prompt injection
- 7 unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 13: Cross-domain retrieval

Status: Done

Notes:
- backend/multi_vector_store.py: MultiVectorStoreService fans queries to per-domain stores
- Per-domain min-max score normalisation before merge
- Deduplication by item_id (highest score wins); faulty stores skipped with ERROR log
- Three new env vars: VECTOR_STORE_PATH_YELP, _AMAZON, _GOODREADS
- Wired into app.py startup; activated when any per-domain path is configured
- 7 unit tests
- Tests: python -m pytest backend/tests

### Phase 4 Task 14: BERTScore + per-user breakdown in Task A eval

Status: Done

Notes:
- task_a_eval.py: optional --bertscore flag using bert_score (graceful warning if not installed)
- Per-user breakdown by history length (sparse/medium/dense) and cultural signal
- Same breakdown added to task_b_eval.py
- Tests: python -m pytest backend/tests

### Phase 4 Task 15: POST /profile/update endpoint

Status: Done

Notes:
- backend/app.py: POST /profile/update accepts existing_records + new_records
- Merges lists and calls build_profile_cached; content-hash cache ensures fresh build
- Returns {updated: true, profile: {...}}
- 4 endpoint tests (test_profile_update_endpoint.py)
- Tests: python -m pytest backend/tests

### Phase 4 Task 16: Docker + docker-compose

Status: Done

Notes:
- backend/Dockerfile: python:3.12-slim, uvicorn entrypoint
- docker-compose.yml: single api service, .env mounting, ./data:/data volume, health-check
- Tests: docker compose up --build (manual verification)

### Phase 4 Task 17: Comprehensive documentation

Status: Done

Notes:
- docs/Backend-Architecture.md: 14 sections, ~1700 lines covering all modules, API contracts,
  design decisions, extension points
- README.md: updated architecture diagram, repo layout, env var table, eval examples,
  API endpoint table, test count
- docs/PROGRESS.md: this file
- docs/Backend-AIML-Phases.md: phase breakdown and acceptance criteria

### Phase 4 Task 18: Full test coverage

Status: Done

Notes:
- 114 tests, all passing (~32s)
- New test modules: test_session.py, test_llm_prompts.py, test_multi_vector_store.py,
  test_task_a_reasoning.py, test_profile_update_endpoint.py, test_task_b_agent_endpoint.py
- All modules covered: cold_start, review_generator, metrics, loaders, vector_store_service,
  deliberative_scoring, agent, task_a, task_b, session, multi_vector_store, llm_prompts

---

## Phase 5 Checklist (Operational Readiness)

- [x] Task 1: Streaming JSONL persistence (OOM fix for large stores)
- [x] Task 2: Streaming batched ingestion + --limit / --batch-size CLI flags
- [x] Task 3: python-dotenv integration (.env auto-loaded at startup)
- [x] Task 4: Logging formatter fix (trace_id filter on handlers, not root logger)
- [x] Task 5: .gitignore — exclude large data/vector store files
- [x] Task 6: 50k Yelp vector store built and end-to-end validated (superseded by Phase 6)
- [x] Task 7: Dockerfile COPY paths fixed + missing __init__.py files added
- [x] Task 8: Record parser accepts both `review_text` and `text` fields
- [x] Task 9: Agent plan always runs all 4 steps even when LLM returns fewer
- [x] Task 10: Full LLM end-to-end validation (Task A + Task B agent with OpenAI)

## Phase 5 Task Logs

### Phase 5 Task 1: Streaming JSONL persistence

Status: Done

Notes:
- root cause: save_vector_store previously built a single giant JSON string in memory
  (json.dumps of 50k × 384-dim vectors = ~800MB string), causing silent OOM; output
  file was 0 bytes
- Fix: stream-write one JSONL line per item; memory use is O(1) vs store size
- Fix: load_vector_store stream-reads line by line; auto-detects legacy JSON array
  format (first char "[") for backward compatibility
- Commit: bad1ee3

### Phase 5 Task 2: Streaming batched ingestion + CLI flags

Status: Done

Notes:
- ingest_embeddings.py previously loaded the entire JSONL into memory before embedding
- Fix: added _stream_batches() generator; read/embed/add in configurable batch_size
  chunks (default 512); memory bounded regardless of dataset size
- Added limit parameter to cap total records ingested (useful for dev/demo stores)
- CLI: --limit and --batch-size flags wired end-to-end through cli.py → ingest_datasets.py → ingest_embeddings.py
- Commit: 2a3ec72

### Phase 5 Task 3: python-dotenv integration

Status: Done

Notes:
- config.py used os.getenv() which reads from the system environment, not .env on disk
- Without a manual `export` step, VECTOR_STORE_PATH and all other vars were empty at
  startup; vector store silently loaded 0 items
- Fix: config.py imports python-dotenv at module level and calls load_dotenv() before
  app_config_from_env(); override=False means real env vars take precedence over .env
- Added python-dotenv to requirements.txt
- Commit: 2092f43

### Phase 5 Task 4: Logging formatter fix

Status: Done

Notes:
- configure_logging() used basicConfig() which sets format on the handler it creates,
  then addFilter() added TraceIdFilter to the root logger — but logging checks filters
  on the handler, not the logger, for format field resolution
- Result: %(trace_id)s raised ValueError("Formatting field not found") on every log
  line when running outside uvicorn's pre-configured logging
- Fix: configure_logging() now explicitly creates a StreamHandler, sets formatter and
  filter on the handler, then adds the handler to the root logger
- Commit: 584c56a

### Phase 5 Task 5: .gitignore extension

Status: Done

Notes:
- data/*.json, data/*.jsonl, data/*.log, data/*.pdf, *.tar, *.gz, *.docx excluded
- Prevents accidentally staging 408MB vector store or 2.1GB Yelp review files
- Unstaged previously-staged data files from index
- Commit: 584c56a

### Phase 5 Task 6: 50k Yelp vector store — build and end-to-end validation

Status: Done (superseded by Phase 6 Task 2 — 200k store)

Notes:
- Built from Yelp Academic Dataset (2.85M reviews, 2.1GB JSONL) using --limit 50000
- Ingestion: ~20 minutes, sentence-transformers all-MiniLM-L6-v2, batch_size=512
- Output: data/yelp_vector_store.json, 408MB JSONL, 50,000 items
- Startup: "INFO Loaded vector store from ... (50000 items)" confirmed
- End-to-end test: POST /task-b/recommend with Nigerian food query returns 5 Yelp items,
  cosine scores 0.57–0.76
- POST /task-a/simulate: rating + reasoning trace + template review all correct
- GET /cold-start/questions: all 4 questions returned
- All 8 endpoints tested and responding correctly

### Phase 5 Task 7: Dockerfile COPY paths and missing __init__.py files

Status: Done

Notes:
- Dockerfile built with context=. (repo root) but used `COPY requirements.txt .`
  (no file at repo root) and `COPY .. .` (above build context — Docker error)
- Fix: `COPY backend/requirements.txt ./backend/requirements.txt` and `COPY . .`
- backend/services/__init__.py and backend/tests/__init__.py were absent; added
  empty files so both sub-packages are explicit Python packages (required for
  consistent imports inside Docker and strict-mode environments)
- Commit: 63962a8

### Phase 5 Task 8: Record parser accepts both `review_text` and `text` fields

Status: Done

Notes:
- _parse_records in app.py called r.get("review_text", "") only; callers sending
  Yelp-style "text" field got empty review text, zeroing stylometry, value
  keywords, trajectory, and cultural signals (code_switching_detected always false)
- Fix: r.get("review_text") or r.get("text", "") — prefers review_text, falls
  back to text; all signal extractors now receive review content correctly
- Validated: Nigerian user with pidgin reviews correctly detected
  nigerian_english_index=0.12, code_switching_detected=true, pidgin_term_hits=7
- Commit: 4cbcb5a

### Phase 5 Task 9: Agent plan always runs all 4 steps

Status: Done

Notes:
- _plan_with_llm mapped only the tool calls the LLM returned in its response;
  when the LLM returned 2 calls (build_profile, extract_axes) the agent silently
  stopped and never ran retrieve_candidates or score_candidates
- Fix: after mapping LLM-returned names, append any required steps not present
  in the LLM response, preserving execution order
  (build_profile → extract_axes → retrieve_candidates → score_candidates)
- Commit: 4cbcb5a

### Phase 5 Task 10: Full LLM end-to-end validation

Status: Done

Notes:
- ENABLE_LLM=true, OPENAI_MODEL=gpt-4o confirmed working with live API key
- POST /task-a/simulate use_llm=true:
  - Rating calibrated correctly (4.0, σ=1.22, n=4)
  - Full 5-component reasoning trace including Nigerian English detection
    (index=0.12, pidgin hits=7, code_switching_detected=true)
  - LLM generated culturally-calibrated pidgin review:
    "Food dey okay, but price no too friendly. Na wa for service."
- POST /task-b/agent use_llm=true:
  - All 4 agent steps executed: build_profile → extract_axes →
    retrieve_candidates → score_candidates
  - cultural_register axis correctly extracted (code_switching_detected=true)
  - LLM planning + deterministic argument filling confirmed working
- POST /task-b/recommend (no LLM): 5 Yelp items, cosine 0.57–0.76
- 114 tests still passing after all fixes

---

## Phase 6 Checklist (200k Vector Store + Multi-Checkpoint Ingestion)

- [x] Task 1: Multi-checkpoint ingestion script (ingest_checkpoints.py)
- [x] Task 2: 200k Yelp vector store built and end-to-end validated
- [x] Task 3: .env wired to 200k store; API startup confirmed

## Phase 6 Task Logs

### Phase 6 Task 1: Multi-checkpoint ingestion script

Status: Done

Notes:
- Created ingest_checkpoints.py at repo root — single-pass ingestion with checkpoint
  saves at 50k, 100k, 150k, 200k records in one streaming run (no re-reading dataset)
- Live progress: carriage-return progress bar every batch (512 records), timestamped
  milestone lines to log file every 10k records, disk-free reported at each checkpoint
- Outputs to /tmp/persona_checkpoints/ (117 GB free on the /tmp volume)
- Ctrl+C handler: saves partial store before exit so no progress is lost
- Log file at /tmp/persona_checkpoints/ingest.log for clean tail -f monitoring
- The /tmp volume is wiped on codespace restart; checkpoint files should be copied to
  /workspaces/Persona/backend/data/ immediately after each successful checkpoint

### Phase 6 Task 2: 200k Yelp vector store — build and end-to-end validation

Status: Done

Notes:
- Built from Yelp Academic Dataset (6.99M reviews, 5.3 GB JSONL) in a single 89-minute
  pass using ingest_checkpoints.py, sentence-transformers all-MiniLM-L6-v2, batch_size=512
- Ingestion rate: ~37–38 records/s sustained on CPU
- Checkpoint files produced:
    yelp_50k.jsonl   —  50,176 items,  409 MB  (saved at ~22 min)
    yelp_100k.jsonl  — 100,352 items,  818 MB  (saved at ~44 min)
    yelp_150k.jsonl  — 150,016 items,  1.2 GB  (saved at ~66 min)
    yelp_200k.jsonl  — 200,192 items,  1.6 GB  (saved at ~89 min)
- 200k store copied to backend/data/yelp_vector_store_200k.jsonl
- Startup confirmed: "INFO Loaded vector store from ... (200192 items)" in ~30s
- End-to-end test: POST /task-b/recommend with Nigerian food query returns 5 Yelp items
  with cosine scores in 0.60–0.69 range; profile axes (cultural_register, rating_bias,
  food, service) correctly extracted and applied to deliberative scoring

### Phase 6 Task 3: .env wired to 200k store

Status: Done

Notes:
- Created .env from .env.example
- Set VECTOR_STORE_PATH=/workspaces/Persona/backend/data/yelp_vector_store_200k.jsonl
- API loads 200k store at startup without any other config changes required

---

## Phase 7 Checklist (Production Deployment)

- [x] Task 1: DigitalOcean Droplet provisioned (Ubuntu 22.04, 2 GB RAM, lon1)
- [x] Task 2: Docker installed and repo cloned on droplet
- [x] Task 3: Vector store uploaded to DigitalOcean Spaces (persona-space / lon1)
- [x] Task 4: entrypoint.sh auto-download validated — 200k store downloaded on first boot
- [x] Task 5: DuckDNS subdomain configured (personabackend.duckdns.org → 188.166.149.75)
- [x] Task 6: Let's Encrypt SSL certificate issued via Certbot (expires 2026-08-21)
- [x] Task 7: Full HTTPS stack live — curl https://personabackend.duckdns.org/health returns {"status":"ok"}
- [x] Task 8: Vercel frontend wired to HTTPS backend (VITE_API_URL updated, redeployed)
- [x] Task 9: Deployment guide written (docs/DEPLOYMENT.md)

## Phase 7 Task Logs

### Phase 7 Task 1–4: Droplet + Vector Store

Status: Done

Notes:
- Provisioned 2 GB RAM / 1 vCPU Ubuntu 22.04 droplet in lon1 region
- Installed Docker via get.docker.com convenience script (Docker 29.5.2)
- Cloned repo from GitHub; wrote .env with DO Spaces credentials and OpenAI key
- Uploaded yelp_vector_store_200k.jsonl (1.6 GB) to DO Spaces bucket persona-space
  using boto3 with endpoint https://lon1.digitaloceanspaces.com
- On first `docker compose up -d`, entrypoint.sh downloaded the 1.6 GB file and
  confirmed "Loaded vector store from /data/yelp_vector_store_200k.jsonl (200192 items)"

### Phase 7 Task 5–7: DuckDNS + SSL

Status: Done

Notes:
- Registered personabackend.duckdns.org (free) at duckdns.org; pointed to 188.166.149.75
- DNS propagated immediately
- Ran Certbot in webroot mode via Docker Compose certbot profile
- Two-step nginx config: HTTP-only first (for ACME challenge), then full TLS config after cert issued
- cert path: /etc/letsencrypt/live/personabackend.duckdns.org/fullchain.pem
- curl https://personabackend.duckdns.org/health → {"status":"ok"} confirmed

### Phase 7 Task 8–9: Frontend wiring + docs

Status: Done

Notes:
- Set VITE_API_URL=https://personabackend.duckdns.org in Vercel environment variables
- Redeployed Vercel frontend; mixed content and CORS errors resolved
- Written docs/DEPLOYMENT.md covering full setup, operational commands, first-boot
  behaviour, SSL renewal, and troubleshooting table
