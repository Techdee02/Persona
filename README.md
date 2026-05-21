# Persona

Psychological and Experiential Reasoning for Simulating Online Nigerian Agents

Persona is a full-stack AI web application that models users as dynamic psychological agents.
It unifies the team brief into one coherent system and product narrative.

## Why Persona

Recommendation systems trained on Western data often fail for African users due to sparse
signals, cultural rating norms, and multi-role identities. Persona is built to handle these
realities directly by constructing a living psychological profile for each user and using it
to drive both review simulation and recommendations.

## Competition Context

DSN x Bluechip Tech LLM Agent Challenge (Data and AI Summit Hackathon 3.0)

Tasks:
- Task A: User modeling and review simulation
- Task B: Agentic recommendations

Datasets:
- Yelp (primary)
- Amazon Reviews
- Goodreads

## Product Overview

Persona uses a shared Psychological Profile Engine to power both Task A and Task B.
The profile is the product. The tasks are two outputs from the same understanding.

Key outcomes:
- Predict how a specific user would rate and review an unseen item
- Recommend items with explicit reasoning and culturally calibrated ranking

## Architecture

Persona uses a four-layer behavioural twin to make the psychological profile concrete and
operational.

### Behavioural Twin Layers

- Taste Graph (L1): Cross-domain preference structure derived from review history
- Vocabulary Fingerprint (L2): Stylometric signature of how the user writes
- Rating Calibration (L3): User-specific rating bias correction
- Cultural Context Layer (L4): Nigerian/African cultural signals, code-switching patterns

Additional Persona-specific dimensions:
- Value hierarchy (food vs service vs atmosphere)
- Complaint and praise thresholds
- Living trajectory (how the user is evolving over time)

## Task A: Review Simulation

Input:
- User review history
- Item description

Output:
- Predicted star rating
- Generated review in the user's authentic voice

Two-stage generation:
1. Rating prediction with explicit reasoning based on profile dimensions
2. Review generation constrained by the behavioural twin and vocabulary fingerprint

Nigerian contextualization:
- Detects Nigerian English and code-switching patterns
- Preserves cultural phrasing and register in outputs

## Task B: Agentic Recommendation

Input:
- User profile

Output:
- Ranked recommendations with explicit reasoning per item

Agent reasoning flow:
1. Identify preference axes from the psychological profile
2. Extract hard constraints and soft preferences
3. Multi-angle retrieval against the vector store
4. Deliberative scoring and conflict resolution
5. Ranked output with explanations grounded in the reasoning chain

Cold-start handling:
- Short elicitation conversation (3 to 4 targeted questions)
- Bootstrap a thin profile from sparse signals and update in real time

## Data and Evaluation

Data processing:
- Temporal split (80/20 per user)
- Deduplication across datasets
- Feature extraction: rating stats, review length, vocabulary richness
- Cultural enrichment via Nigerian/African signal dictionary

Evaluation metrics:
- Task A: ROUGE-L, BERTScore, RMSE, human behavioural fidelity
- Task B: NDCG@10, Hit Rate, cold-start and cross-domain performance
- Solution paper and reproducibility are scored explicitly

Ablation studies will compare performance with each behavioural layer removed.

## System Components

- Backend API: FastAPI (Python)
- LLM: OpenAI-compatible API (configurable)
- Embeddings: sentence-transformers (`all-MiniLM-L6-v2` by default)
- Vector Store: in-memory with JSON persistence
- Containerization: Docker Compose (planned)

## Repo Layout

```
backend/
  app.py                  FastAPI application and endpoints
  config.py               Environment-based configuration
  profile.py              Psychological profile schema and builder
  signal_extraction.py    Rating stats, stylometry, value keywords
  cultural_signals.py     Nigerian English / pidgin detection
  trajectory.py           Early-vs-recent behavioural drift
  preference_axes.py      Preference axis extraction from profile
  rating_calibration.py   User vs population rating calibration
  deliberative_scoring.py Per-item axis-weighted ranking
  retrieval.py            Cosine-similarity multi-angle retrieval
  vector_store.py         In-memory vector store
  vector_store_persist.py Save / load vector store as JSON
  vector_store_service.py Embedding + store facade
  embeddings.py           sentence-transformers wrapper
  ingest_embeddings.py    JSONL → vector store ingestion
  ingest_datasets.py      Dataset-specific ingestion helpers
  cli.py                  Dataset ingestion CLI entry point
  agent_orchestrator.py   Tool-call plan executor
  agent_tools.py          Tool registry
  agent_tool_defs.py      Registered tools: profile, axes, retrieval, scoring
  task_a_service.py       Task A: rating prediction + review generation
  task_b_service.py       Task B: vector retrieval + deliberative ranking
  task_b_agent_service.py Task B: agentic variant with optional LLM planning
  llm_client.py           OpenAI chat completion client
  llm_factory.py          Client factory (returns None when LLM disabled)
  cache.py                Generic TTL + LRU cache
  services/
    profile_service.py    Profile builder with cache layer
  data/
    schema.py             InteractionRecord dataclass
    loaders.py            Yelp / Amazon / Goodreads file loaders
    split.py              Per-user temporal train/test split
  tests/                  pytest test suite (41 tests)
docs/
  PRD-Backend-AIML.md     Backend AI/ML product requirements
  Backend-AIML-Phases.md  Phase breakdown and acceptance criteria
  PROGRESS.md             Task-by-task implementation log
```

## Getting Started

### Install dependencies

```bash
pip install -r backend/requirements.txt
```

### Configure environment

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

Key variables:

| Variable | Default | Description |
|---|---|---|
| `DATASET_YELP_PATH` | — | Absolute path to Yelp JSONL file |
| `DATASET_AMAZON_PATH` | — | Absolute path to Amazon JSONL file |
| `DATASET_GOODREADS_PATH` | — | Absolute path to Goodreads JSONL file |
| `VECTOR_STORE_PATH` | _(empty)_ | Path to a pre-built vector store JSON. When set and the file exists the API loads it at startup. |
| `DETERMINISTIC_MODE` | `false` | Lock random seeds for reproducible demo output |
| `PROFILE_CACHE_TTL_SECONDS` | `3600` | Profile cache time-to-live |
| `PROFILE_CACHE_MAX_SIZE` | `1000` | Maximum cached profiles (LRU eviction) |
| `ENABLE_LLM` | `false` | Enable OpenAI-backed LLM features |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key (required when `ENABLE_LLM=true`) |
| `OPENAI_MODEL` | `gpt-4o` | Model name passed to the OpenAI chat completion API |

### Run the API

```bash
uvicorn backend.app:app --reload
```

The API will be available at `http://localhost:8000`. Swagger UI is at `/docs`.

### Run tests

```bash
python -m pytest backend/tests -v
```

## Dataset Ingestion

Before recommendations can work with real items, build a vector store from your dataset.
The CLI reads a JSONL file, embeds the relevant text field with sentence-transformers, and
writes a JSON snapshot that the API can load at startup.

### Ingestion flow

```
Dataset JSONL
    │
    ▼
ingest_datasets.py          (dataset-specific field mapping)
    │
    ▼
ingest_embeddings.py        (embed text fields → float vectors)
    │
    ▼
InMemoryVectorStore         (cosine-similarity index in memory)
    │
    ▼
vector_store_persist.py     (save to JSON snapshot)
    │
    ▼
API startup                 (load JSON → serve queries via VECTOR_STORE_PATH)
```

### CLI usage

```bash
python -m backend.cli \
  --dataset  yelp|amazon|goodreads \
  --input    /path/to/dataset.jsonl \
  --output   /path/to/vector_store.json
```

**Examples**

```bash
# Ingest Yelp business reviews
python -m backend.cli \
  --dataset yelp \
  --input   data/yelp_academic_dataset_review.jsonl \
  --output  data/yelp_vector_store.json

# Ingest Amazon product reviews
python -m backend.cli \
  --dataset amazon \
  --input   data/amazon_reviews.jsonl \
  --output  data/amazon_vector_store.json

# Ingest Goodreads book reviews
python -m backend.cli \
  --dataset goodreads \
  --input   data/goodreads_reviews.jsonl \
  --output  data/goodreads_vector_store.json
```

**Field mapping per dataset**

| Dataset | Text field embedded | ID field | Extra metadata |
|---|---|---|---|
| Yelp | `text` | `business_id` | `name`, `categories`, `stars` |
| Amazon | `reviewText` | `asin` | `summary`, `overall` |
| Goodreads | `review_text` | `book_id` | `rating` |

### Loading the store at API startup

Set `VECTOR_STORE_PATH` in your `.env` to the JSON file produced above:

```
VECTOR_STORE_PATH=/path/to/yelp_vector_store.json
```

The API logs on startup how many items were loaded:

```
INFO  Loaded vector store from /path/to/yelp_vector_store.json (52000 items)
```

If the file is missing or the variable is empty, the API starts with an empty store and
only vector-free profile-based recommendations are available.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `POST` | `/profile/build` | Build a psychological profile from interaction records |
| `POST` | `/task-a/simulate` | Predict rating and generate review for a target item |
| `POST` | `/task-b/recommend` | Rank items using profile axes and deliberative scoring |
| `POST` | `/task-b/agent` | Agentic Task B variant with optional LLM tool-call planning |

Full request/response schemas are available at `/docs` when the API is running.

## Next Steps

- Scaffold frontend (React + TypeScript)
- Add Docker Compose for one-command local run
- Wire evaluation scripts (ROUGE-L, BERTScore, NDCG@10)
- Ablation study automation
- Cross-domain transfer logic in retrieval

## License

TBD