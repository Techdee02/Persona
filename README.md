# Persona

**Psychological and Experiential Reasoning for Simulating Online Nigerian Agents**

Persona is a backend AI system that constructs a living psychological profile for each user
and uses it to drive two competition tasks: review simulation (Task A) and agentic
recommendation (Task B). Built for the **DSN × Bluechip Tech LLM Agent Challenge**
(Data and AI Summit Hackathon 3.0).

---

## Why Persona

Recommendation systems trained on Western data routinely fail for African users because of
sparse interaction histories, culturally distinct rating norms, and multi-domain identities.
Persona addresses these gaps directly by building a structured behavioural twin from review
data and grounding all outputs — ratings, generated text, and ranked recommendations — in
that twin.

---

## Tasks

| Task | Input | Output |
|---|---|---|
| **A — Review Simulation** | User history + target item | Predicted rating, reasoning trace, generated review |
| **B — Agentic Recommendation** | User history or cold-start answers | Ranked items with per-item explanations and reasoning trace |

---

## Architecture Overview

```
User Input
    │
    ▼
FastAPI Layer  ──────────────────────────────────────────────────────────
    │                                                                    │
    ▼                                                                    ▼
Profile Engine                                               Cold-Start Engine
  ├── Signal Extractor                                         └── bootstrap_profile()
  │     ├── Rating stats
  │     ├── Stylometry
  │     ├── Value keywords
  │     ├── Trajectory (drift)
  │     └── Cultural signals (Nigerian/pidgin)
  └── PsychologicalProfile
         │
         ├──────────────────────────────────────────┐
         ▼                                          ▼
    Task A Engine                             Task B Engine
    ├── Rating calibration                    ├── Preference axis extraction
    ├── Richer reasoning trace                ├── Multi-angle vector retrieval
    ├── Template review generator             ├── Deliberative scoring
    ├── Structured LLM prompts                ├── Session state (multi-turn)
    └── [LLM review path]                     ├── [LLM agent planning path]
                                              └── Structured LLM prompts
                                                     │
                                    ┌────────────────┴───────────────────┐
                                    ▼                                    ▼
                             VectorStoreService                MultiVectorStoreService
                             ├── sentence-transformers         ├── per-domain stores
                             ├── InMemoryVectorStore           │   (Yelp/Amazon/Goodreads)
                             └── JSON persistence              └── score normalisation + merge
```

### Behavioural Twin Layers

| Layer | Module | What it captures |
|---|---|---|
| L1 Taste Graph | `preference_axes.py` | Cross-domain value priorities (food, service, price, atmosphere) |
| L2 Vocabulary Fingerprint | `signal_extraction.py` | Review length, word count, vocab richness, sentence length |
| L3 Rating Calibration | `rating_calibration.py` | User mean vs population mean; z-score rescaling |
| L4 Cultural Context | `cultural_signals.py` | Nigerian English index, pidgin term hits, code-switching flag |
| L5 Living Trajectory | `trajectory.py` | Early-vs-recent rating drift and review length drift |

---

## System Components

| Component | Technology |
|---|---|
| Backend API | FastAPI (Python 3.12) |
| LLM | OpenAI-compatible API (gpt-4o by default, disabled by default) |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Vector Store | Custom in-memory cosine-similarity store with JSON persistence |
| Caching | TTL + LRU in-memory cache |
| Containerisation | Docker + Docker Compose |

---

## Repo Layout

```
backend/
  app.py                   FastAPI app, middleware, all endpoint handlers
  config.py                Typed AppConfig dataclass; all settings from env vars
  profile.py               PsychologicalProfile schema + build_profile()
  cold_start.py            Elicitation questions + bootstrap_profile()
  signal_extraction.py     Rating stats, stylometry, value keyword counters
  cultural_signals.py      Nigerian English / pidgin term detection
  trajectory.py            Early-vs-recent rating and length drift
  preference_axes.py       PreferenceAxis extraction from profile
  rating_calibration.py    User vs population z-score calibration
  review_generator.py      Template-based review generation from profile
  deliberative_scoring.py  Per-item axis-weighted + penalty scoring
  retrieval.py             Cosine-similarity multi-angle retrieval
  vector_store.py          InMemoryVectorStore (add, query)
  vector_store_persist.py  save_vector_store / load_vector_store (JSON)
  vector_store_service.py  Embedding + store facade; loads from path at startup
  multi_vector_store.py    MultiVectorStoreService: cross-domain fan-out + merge
  embeddings.py            sentence-transformers encode wrapper
  ingest_embeddings.py     JSONL → embed → InMemoryVectorStore
  ingest_datasets.py       Dataset-specific ingestion configs (Yelp/Amazon/Goodreads)
  cli.py                   Dataset ingestion CLI entry point
  agent_orchestrator.py    Tool-call plan executor with $ref argument resolution
  agent_tools.py           ToolRegistry, ToolCall, ToolResult types
  agent_tool_defs.py       Registered tools: build_profile, extract_axes,
                           retrieve_candidates, score_candidates
  llm_prompts.py           Structured culturally-calibrated prompt builders (Task A + B)
  session.py               SessionState + SessionStore for multi-turn Task B
  task_a_service.py        Task A: calibration + richer reasoning trace + review generation
  task_b_service.py        Task B: vector retrieval + deliberative ranking + session support
  task_b_agent_service.py  Task B agent: tool-call plan + optional LLM planning
  llm_client.py            OpenAI chat completion with retry + backoff
  llm_factory.py           Client factory (None when ENABLE_LLM=false)
  logging_utils.py         Structured logging + trace-ID filter
  cache.py                 Generic TTL + LRU OrderedDict cache
  services/
    profile_service.py     Profile builder with TTL+LRU cache layer
  data/
    schema.py              InteractionRecord dataclass
    loaders.py             Yelp / Amazon / Goodreads loaders with row validation
    split.py               Per-user temporal train/test split
  evaluation/
    metrics.py             RMSE, ROUGE-L, NDCG@k, Hit Rate@k, baselines
    task_a_eval.py         Task A eval: RMSE, ROUGE-L, BERTScore (opt), per-user breakdown
    task_b_eval.py         Task B eval: NDCG@k, Hit Rate@k, ablation support, breakdown
    ablation.py            Ablation study: zero each profile layer, report RMSE/NDCG delta
  tests/                   pytest suite — 114 tests, all passing
backend/Dockerfile
docker-compose.yml
docs/
  PRD-Backend-AIML.md      Backend AI/ML product requirements
  Backend-AIML-Phases.md   Phase breakdown and acceptance criteria
  Backend-Architecture.md  Comprehensive system design and module reference
  PROGRESS.md              Task-by-task implementation log
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

| Variable | Default | Description |
|---|---|---|
| `DATASET_YELP_PATH` | — | Absolute path to Yelp JSONL |
| `DATASET_AMAZON_PATH` | — | Absolute path to Amazon JSONL |
| `DATASET_GOODREADS_PATH` | — | Absolute path to Goodreads JSONL |
| `VECTOR_STORE_PATH` | _(empty)_ | Pre-built vector store JSON to load at startup |
| `VECTOR_STORE_PATH_YELP` | _(empty)_ | Per-domain Yelp store for cross-domain retrieval |
| `VECTOR_STORE_PATH_AMAZON` | _(empty)_ | Per-domain Amazon store |
| `VECTOR_STORE_PATH_GOODREADS` | _(empty)_ | Per-domain Goodreads store |
| `DETERMINISTIC_MODE` | `false` | Reproducible outputs for demos |
| `PROFILE_CACHE_TTL_SECONDS` | `3600` | Profile cache TTL |
| `PROFILE_CACHE_MAX_SIZE` | `1000` | Max cached profiles (LRU eviction) |
| `ENABLE_LLM` | `false` | Enable OpenAI LLM features |
| `OPENAI_API_KEY` | _(empty)_ | Required when `ENABLE_LLM=true` |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model name |

### 3a. Run directly

```bash
uvicorn backend.app:app --reload
# API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### 3b. Run with Docker Compose

```bash
docker compose up --build
```

The `./data` directory is mounted into the container so the CLI-built vector store is
accessible at the path set in `VECTOR_STORE_PATH`.

### 4. Run tests

```bash
python -m pytest backend/tests -v
# 114 tests, ~32 s
```

---

## Dataset Ingestion

Build a vector store from a JSONL dataset before recommendations can serve real items.

### Flow

```
Dataset JSONL
    │   (row validation: user_id, item_id, rating in [0,5])
    ▼
ingest_datasets.py    (dataset-specific field mapping)
    ▼
ingest_embeddings.py  (sentence-transformers encode → float vectors)
    ▼
InMemoryVectorStore   (cosine-similarity index)
    ▼
vector_store_persist  (save as JSON snapshot)
    ▼
API startup           (load JSON when VECTOR_STORE_PATH is set)
```

### CLI

```bash
python -m backend.cli \
  --dataset  yelp|amazon|goodreads \
  --input    /path/to/dataset.jsonl \
  --output   /path/to/vector_store.json
```

**Field mapping**

| Dataset | Text embedded | Item ID | Stored metadata |
|---|---|---|---|
| Yelp | `text` | `business_id` | `name`, `categories`, `stars` |
| Amazon | `reviewText` | `asin` | `summary`, `overall` |
| Goodreads | `review_text` | `book_id` | `rating` |

### Startup loading

```bash
VECTOR_STORE_PATH=/data/yelp_vector_store.json
```

Startup log: `INFO Loaded vector store from ... (52000 items)`

If the file is absent or the variable is empty the API starts with an empty store;
profile-based recommendations still work.

---

## Evaluation

Run evaluation scripts once datasets are available. Both scripts accept JSONL files using
the same schema as the loaders.

### Task A — Rating RMSE and ROUGE-L

```bash
python -m backend.evaluation.task_a_eval \
  --records  data/records.jsonl \
  --split    0.8 \
  --bertscore          # optional: requires bert-score package
```

Output includes per-user breakdown by history length and cultural signal presence:
```json
{
  "test_size": 1240,
  "persona_rmse": 0.71,
  "baseline_rmse": 0.89,
  "rmse_improvement": 0.18,
  "rouge_l": 0.14,
  "breakdown": {
    "by_history_length": {
      "sparse":  {"rmse": 0.81, "users": 120},
      "medium":  {"rmse": 0.68, "users": 890},
      "dense":   {"rmse": 0.61, "users": 230}
    },
    "by_cultural_signal": {
      "with_nigerian_english":    {"rmse": 0.65, "users": 310},
      "without_nigerian_english": {"rmse": 0.74, "users": 930}
    }
  }
}
```

### Task B — NDCG@10 and Hit Rate@10

```bash
python -m backend.evaluation.task_b_eval \
  --records data/records.jsonl \
  --store   data/vector_store.json \
  --k       10
```

Output includes the same per-user breakdown:
```json
{
  "evaluated_users": 340,
  "k": 10,
  "persona_ndcg": 0.23,
  "baseline_ndcg": 0.11,
  "ndcg_improvement": 0.12,
  "persona_hit_rate": 0.41,
  "baseline_hit_rate": 0.19,
  "breakdown": {
    "by_history_length": { "sparse": {...}, "medium": {...}, "dense": {...} },
    "by_cultural_signal": { "with_nigerian_english": {...}, "without_nigerian_english": {...} }
  }
}
```

### Ablation Study

```bash
python -m backend.evaluation.ablation \
  --records data/records.jsonl \
  --store   data/vector_store.json \
  --k       10
```

Zeroes out each profile layer in turn (rating\_stats, stylometry, value\_keywords, trajectory, cultural\_signals) and reports RMSE and NDCG delta vs the full model — ready for the solution paper.

```json
{
  "full_model": { "task_a": {"rmse": 0.71, "rouge_l": 0.14}, "task_b": {"ndcg": 0.23} },
  "ablations": {
    "cultural_signals": {
      "task_a_delta": {"rmse_delta": 0.08, "rouge_l_delta": -0.03},
      "task_b_delta": {"ndcg_delta": -0.05}
    }
  }
}
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/cold-start/questions` | Return the 4 elicitation questions |
| `POST` | `/cold-start/answer` | Bootstrap a profile from elicitation answers |
| `POST` | `/profile/build` | Build a profile from full interaction history |
| `POST` | `/profile/update` | Append new records and return the rebuilt profile |
| `POST` | `/task-a/simulate` | Predict rating + detailed reasoning trace + generated review |
| `POST` | `/task-b/recommend` | Rank items with profile axes, deliberative scoring, session support |
| `POST` | `/task-b/agent` | Agentic Task B with optional LLM tool-call planning |

Full request/response schemas: `http://localhost:8000/docs`

For detailed endpoint contracts, architecture decisions, and module-level design, see
[docs/Backend-Architecture.md](docs/Backend-Architecture.md).

---

## Next Steps

- Frontend scaffold (React + TypeScript) — separate developer
- Solution paper write-up and reproducibility artifacts
- BERTScore integration for richer review quality measurement (requires `bert-score` package)
- Expanded pidgin/Nigerian English dictionary (Yoruba, Igbo, Hausa term sets)
- Adaptive cold-start question selection based on partial answer uncertainty
- Production vector database (ChromaDB / FAISS) behind `VectorStoreService` facade

---

## License

TBD
