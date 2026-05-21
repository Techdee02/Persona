# Persona — Backend & AI/ML Architecture

Owner: Backend AI/ML  
Last updated: 2026-05-21

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Data Layer](#3-data-layer)
   - 3.1 InteractionRecord schema
   - 3.2 Dataset loaders and row validation
   - 3.3 Temporal split
4. [Profile Engine](#4-profile-engine)
   - 4.1 Rating stats
   - 4.2 Stylometry
   - 4.3 Value keywords
   - 4.4 Living trajectory
   - 4.5 Cultural signals
   - 4.6 PsychologicalProfile assembly
5. [Cold-Start System](#5-cold-start-system)
6. [Task A Pipeline — Review Simulation](#6-task-a-pipeline--review-simulation)
   - 6.1 Rating calibration
   - 6.2 Template-based review generation
   - 6.3 LLM review path
7. [Task B Pipeline — Agentic Recommendation](#7-task-b-pipeline--agentic-recommendation)
   - 7.1 Preference axis extraction
   - 7.2 Multi-angle retrieval
   - 7.3 Deliberative scoring
   - 7.4 Non-LLM path (TaskBService)
8. [Agent System](#8-agent-system)
   - 8.1 Tool registry
   - 8.2 Agent orchestrator and $ref resolution
   - 8.3 Registered tools
   - 8.4 LLM planning path (TaskBAgentService)
9. [Vector Store System](#9-vector-store-system)
   - 9.1 InMemoryVectorStore
   - 9.2 Embedding model
   - 9.3 VectorStoreService facade
   - 9.4 JSON persistence
   - 9.5 Dataset ingestion pipeline
   - 9.6 CLI
10. [Evaluation System](#10-evaluation-system)
    - 10.1 Metrics
    - 10.2 Task A evaluation runner
    - 10.3 Task B evaluation runner
    - 10.4 Baselines
11. [API Layer](#11-api-layer)
    - 11.1 Endpoint contracts
    - 11.2 Trace-ID middleware
12. [Infrastructure](#12-infrastructure)
    - 12.1 Configuration
    - 12.2 TTL + LRU cache
    - 12.3 Profile service caching
    - 12.4 LLM client and retry policy
    - 12.5 Structured logging and request tracing
    - 12.6 Docker and Compose
13. [Design Decisions](#13-design-decisions)
14. [Extension Points](#14-extension-points)

---

## 1. System Overview

Persona builds a **psychological profile** from a user's review history and uses it as a
shared foundation for two outputs:

- **Task A**: Given a new item, predict the rating the user would assign and generate a
  review in their authentic voice, with Nigerian cultural calibration where signals are
  present.
- **Task B**: Given a user profile and an optional query, retrieve and rank candidate items
  with explicit per-item reasoning grounded in the user's preference axes.

The system is designed to work in two modes:

| Mode | Data available | How profile is built |
|---|---|---|
| **History mode** | User has prior reviews | `build_profile()` over full history |
| **Cold-start mode** | New user, no history | `bootstrap_profile()` from 4 elicitation answers |

All outputs include a reasoning trace so judges and users can audit decisions.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Client (frontend / evaluation scripts / curl)                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FastAPI  (backend/app.py)                                          │
│  ├── Trace-ID middleware (X-Trace-Id header)                        │
│  ├── GET  /health                                                   │
│  ├── GET  /cold-start/questions                                     │
│  ├── POST /cold-start/answer   ──► ColdStartEngine                 │
│  ├── POST /profile/build       ──► ProfileService                  │
│  ├── POST /task-a/simulate     ──► TaskAService                    │
│  ├── POST /task-b/recommend    ──► TaskBService                    │
│  └── POST /task-b/agent        ──► TaskBAgentService               │
└────────────┬───────────────────────────────────────────────────────┘
             │
   ┌─────────┴───────────────────────────────────────┐
   │                                                 │
   ▼                                                 ▼
ProfileEngine                               VectorStoreService
  signal_extraction.py                        embeddings.py
  cultural_signals.py                         vector_store.py
  trajectory.py                               vector_store_persist.py
  profile.py                                  (loaded from VECTOR_STORE_PATH)
  services/profile_service.py
  (TTL+LRU cache)
   │
   ├──────────────────────────┐
   ▼                          ▼
TaskAService              TaskBService / TaskBAgentService
  rating_calibration.py     preference_axes.py
  review_generator.py       retrieval.py
  llm_client.py (opt)       deliberative_scoring.py
                            agent_orchestrator.py (agent path)
                            agent_tool_defs.py
                            llm_client.py (opt)
```

---

## 3. Data Layer

### 3.1 InteractionRecord Schema

**File:** `backend/data/schema.py`

```python
@dataclass(frozen=True)
class InteractionRecord:
    user_id:     str
    item_id:     str
    rating:      float
    review_text: str
    timestamp:   Optional[str]   # ISO date or unix epoch string
    source:      str             # "yelp" | "amazon" | "goodreads"
    metadata:    Dict[str, Any]  # remaining fields from source row
```

`InteractionRecord` is the canonical unit passed through every pipeline stage. It is
frozen (immutable) to prevent accidental mutation inside extractors.

`timestamp` is intentionally kept as a string; the split utility parses it on-demand
using `timestamp_key()` which handles ISO dates, unix epoch strings, and falls back
to `0.0` for unparseable values so sort order degrades gracefully rather than crashing.

### 3.2 Dataset Loaders and Row Validation

**File:** `backend/data/loaders.py`

Three public functions share one private implementation:

```
load_yelp_reviews(path)      → List[InteractionRecord]
load_amazon_reviews(path)    → List[InteractionRecord]
load_goodreads_reviews(path) → List[InteractionRecord]
```

Each maps source-specific field names to canonical names via a `FieldMap` dict:

| Dataset | user_id field | item_id field | rating field | text field | timestamp field |
|---|---|---|---|---|---|
| Yelp | `user_id` | `business_id` | `stars` | `text` | `date` |
| Amazon | `reviewerID` | `asin` | `overall` | `reviewText` | `unixReviewTime` |
| Goodreads | `user_id` | `book_id` | `rating` | `review_text` | `date` |

**Row validation** (added Phase 3, Task 16):

`_row_to_record()` returns `(InteractionRecord, None)` on success or `(None, error_str)`
on failure. Invalid rows are skipped, not raised:

| Validation rule | Action on failure |
|---|---|
| `user_id` is non-empty after strip | Skip, log debug |
| `item_id` is non-empty after strip | Skip, log debug |
| `rating` parseable as `float` | Skip, log debug |
| `rating` in `[0.0, 5.0]` | Skip, log debug |

A single `WARNING` log line per file summarises how many rows were skipped:
```
WARNING Skipped 12 invalid rows from /data/yelp.jsonl
```

Supported file formats: `.jsonl` / `.json` (newline-delimited), `.csv`.

### 3.3 Temporal Split

**File:** `backend/data/split.py`

```python
temporal_split(
    records: Iterable[InteractionRecord],
    train_ratio: float = 0.8,
    min_user_records: int = 2,
) -> Tuple[List[InteractionRecord], List[InteractionRecord]]
```

The split is **per-user** to avoid data leakage:

1. Group records by `user_id`.
2. For users with fewer than `min_user_records` records, place all in train.
3. For qualifying users, sort by `timestamp_key()` and take the first 80 % as train,
   the rest as test.

This ensures the model is always tested on future reviews it has not seen, matching the
production inference scenario.

`timestamp_key(record)` resolution order:
- `None` → `0.0`
- Digit-only string → `float(value)` (unix epoch)
- ISO date `%Y-%m-%d` or `%Y-%m-%d %H:%M:%S` → `datetime.timestamp()`
- Anything else → `0.0` (stable sort fallback)

---

## 4. Profile Engine

**Files:** `backend/profile.py`, `backend/signal_extraction.py`,
`backend/cultural_signals.py`, `backend/trajectory.py`

### 4.1 Rating Stats

**Extractor:** `extract_rating_stats(records) → RatingStats`

```python
@dataclass(frozen=True)
class RatingStats:
    count:      int
    mean:       float
    std_dev:    float    # population std dev (pstdev)
    min_rating: float
    max_rating: float
```

- Empty records → all zeros (safe default; downstream code handles `count == 0`).
- `std_dev` uses population std dev (`pstdev`) since user histories are the full
  population, not a sample.

### 4.2 Stylometry

**Extractor:** `extract_stylometry(records) → StylometryStats`

```python
@dataclass(frozen=True)
class StylometryStats:
    avg_review_length:   float   # characters
    avg_word_count:      float
    vocab_richness:      float   # unique words / total words (TTR)
    avg_sentence_length: float   # words per sentence
```

- Words matched by `[A-Za-z']+` (captures contractions).
- Sentences split on `[.!?]+` with `max(1, count)` to avoid divide-by-zero.
- `vocab_richness` is **type-token ratio** (TTR) across the entire review corpus
  for the user, not per-review, so longer histories produce more stable estimates.

### 4.3 Value Keywords

**Extractor:** `extract_value_keywords(records) → Dict[str, int]`

Four domain categories with fixed keyword sets:

| Category | Keywords |
|---|---|
| `food` | food, taste, flavor, fresh, spicy, grill |
| `service` | service, staff, wait, server, attentive |
| `price` | price, cheap, expensive, value, cost |
| `atmosphere` | ambience, atmosphere, music, decor, vibe |

Count semantics: the count for a category increments by 1 per review that contains
**any** keyword from that category (not per keyword occurrence). This measures
*topic breadth* across reviews rather than word frequency.

### 4.4 Living Trajectory

**Extractor:** `extract_trajectory(records) → TrajectoryStats`

```python
@dataclass(frozen=True)
class TrajectoryStats:
    early_mean_rating:        float
    recent_mean_rating:       float
    delta_rating:             float    # recent - early
    early_avg_review_length:  float
    recent_avg_review_length: float
    delta_review_length:      float    # recent - early
```

Records are sorted by `timestamp_key()` and split at the midpoint into early and
recent halves. Requires at least 4 records; fewer returns all-zero stats.

`delta_rating > 0` means the user has become more generous over time.
`delta_review_length > 0` means reviews are getting longer (more detailed).

Both deltas are features that preference axis extraction and downstream LLM prompts
can use to characterise a *changing* user, not a static one.

### 4.5 Cultural Signals

**Extractor:** `extract_cultural_signals(records) → CulturalSignals`

```python
@dataclass(frozen=True)
class CulturalSignals:
    nigerian_english_index:  float    # pidgin_hits / total_words
    code_switching_detected: bool     # True if any pidgin hit
    pidgin_term_hits:        int
```

Detected pidgin/Nigerian English terms (case-insensitive, full-word match):

```
abeg  abi  dey  na  oga  sef  sha  wahala  jollof  suya  wah  omo
```

`nigerian_english_index` is a density score (hits per total word), not a binary flag,
allowing downstream components to scale their response proportionally.

`code_switching_detected = pidgin_term_hits > 0` is a convenience flag for boolean
branching in the review generator and preference axis extractor.

### 4.6 PsychologicalProfile Assembly

**File:** `backend/profile.py`

```python
@dataclass(frozen=True)
class PsychologicalProfile:
    user_id:         str
    rating_stats:    RatingStats
    stylometry:      StylometryStats
    value_keywords:  Dict[str, int]
    trajectory:      TrajectoryStats
    cultural_signals: CulturalSignals
```

`build_profile(user_id, records)` calls all five extractors and assembles the profile.
The profile is frozen; it is never mutated after construction.

`to_dict()` and `profile_from_dict()` provide serialisation round-trips for caching,
API responses, and agent tool argument passing.

---

## 5. Cold-Start System

**File:** `backend/cold_start.py`

Handles new users who have no review history.

### Elicitation Questions

Four fixed questions targeting the most important profile dimensions:

| Question ID | Dimension targeted | Options |
|---|---|---|
| `rating_tendency` | `RatingStats.mean`, `std_dev` | `top_marks`, `reserve_top` |
| `value_priority` | `value_keywords` | `food_quality`, `service`, `price_value`, `atmosphere` |
| `review_style` | `StylometryStats.avg_review_length` | `brief_and_direct`, `detailed_and_thorough` |
| `cultural_register` | `CulturalSignals` | `yes_often`, `sometimes`, `rarely` |

### Signal Mapping

Each answer maps to concrete overrides applied to default profile values:

```
rating_tendency=top_marks   → mean=4.5, std_dev=0.5
rating_tendency=reserve_top → mean=3.5, std_dev=0.8

value_priority=food_quality → value_keywords={food:3, service:0, price:0, atmosphere:0}

review_style=brief           → avg_review_length=80,  avg_word_count=16
review_style=detailed        → avg_review_length=300, avg_word_count=60

cultural_register=yes_often → nigerian_english_index=0.06, code_switching=True
cultural_register=sometimes → nigerian_english_index=0.02, code_switching=True
cultural_register=rarely    → nigerian_english_index=0.0,  code_switching=False
```

Unknown question IDs or answer values are silently ignored; the profile falls back to
defaults for unmapped dimensions. This makes the endpoint safe for partial submissions.

### bootstrap_profile()

Returns a complete `PsychologicalProfile` with:
- `rating_stats.count = 0` (signals it is a bootstrapped profile)
- `TrajectoryStats` all zeros (no temporal data available)
- All other fields set from answer signal map

The bootstrapped profile is compatible with all downstream consumers:
`extract_preference_axes()`, `TaskAService`, `TaskBService`. They all handle
`count == 0` or zero-trajectory gracefully.

---

## 6. Task A Pipeline — Review Simulation

**File:** `backend/task_a_service.py`

### Inputs

```json
{
  "user_id": "string",
  "records": [ InteractionRecord, ... ],
  "target_item": { "name": "...", "description": "...", ... },
  "population_records": [ InteractionRecord, ... ],   // optional
  "use_llm": false
}
```

### Pipeline steps

```
records
  └─► build_profile_cached()   →  PsychologicalProfile
                                         │
population_records (or records as fallback)
  └─► build_rating_calibration() → RatingCalibration
                                         │
profile.rating_stats.mean
  └─► calibration.calibrate()  →  predicted_rating (float, clamped 1–5)
                                         │
                                         ├── use_llm=False → generate_review(profile, target_item)
                                         └── use_llm=True  → _generate_review_with_llm(...)
```

### 6.1 Rating Calibration

**File:** `backend/rating_calibration.py`

```python
@dataclass(frozen=True)
class RatingCalibration:
    user_mean:       float
    user_std:        float
    population_mean: float
    population_std:  float

    def calibrate(self, rating: float) -> float:
        z = (rating - user_mean) / user_std
        calibrated = population_mean + z * population_std
        return max(1.0, min(5.0, calibrated))
```

Z-score rescaling maps the user's personal scale to the population scale:
- A user who habitually rates 4.5 in a population that averages 3.8 will have their
  predicted 4.5 pulled down to a more typical value.
- If either `user_std` or `population_std` is zero (single-record history), the raw
  rating is returned unchanged.

When `population_records` is not provided the endpoint falls back to using the user's
own records as the population, making calibration a no-op in that case.

### 6.2 Template-Based Review Generation

**File:** `backend/review_generator.py`

Produces a review string without any LLM call, driven entirely by profile signals.

**Sentiment bucket** (from `profile.rating_stats.mean`):

| Mean | Bucket |
|---|---|
| ≥ 4.0 | `positive` |
| ≥ 2.5 | `neutral` |
| < 2.5 | `negative` |

**Assembly:**

1. Pick a sentiment-appropriate **opener** from a curated list.
2. For up to the **top 2 value categories** by count, pick a sentiment-appropriate
   phrase for that category (food/service/price/atmosphere).
3. If `target_item` contains a `name` or `title` field, add an item-specific sentence.
4. **Cultural closer**: if `code_switching_detected`, pick a pidgin closer
   (`"Abeg, try am yourself"`, `"Na so e be sha"`, `"Omo, e get as e be"`);
   otherwise pick a standard English closer.
5. Trim to `1.5 × avg_review_length` characters if the result exceeds the user's
   typical length. Trim on a word boundary.

**Determinism**: pass `seed=int` to `generate_review()` for reproducible output. The
review generator uses `random.Random(seed)` internally and does not touch the global
random state.

### 6.3 LLM Review Path

When `use_llm=True` and an `OpenAIClient` is configured:

```python
messages = [
    {"role": "system", "content": "Write a short review in the user's voice based on the profile."},
    {"role": "user",   "content": f"Profile: {profile_dict}\nItem: {target_item}"},
]
response = llm_client.chat_completion(messages, temperature=0.2)
```

The temperature of 0.2 keeps output near-deterministic for scoring consistency.
The system prompt constrains the model to mimic the user's voice; the profile dict
passed includes all five signal dimensions so the model can calibrate length, tone,
and cultural register.

### Output

```json
{
  "user_id": "u1",
  "target_item": { ... },
  "predicted_rating": 3.8,
  "reasoning": "Rating derived from user mean with calibration.",
  "review_text": "Really enjoyed this. The food was the highlight. ..."
}
```

---

## 7. Task B Pipeline — Agentic Recommendation

**File:** `backend/task_b_service.py`

### Inputs

```json
{
  "user_id":      "string",
  "records":      [ InteractionRecord, ... ],
  "query_vectors": [[1.0, 0.0], ...],      // optional if query_text provided
  "candidates":   [{"item_id":"...", "vector":[...], "metadata":{...}}, ...],
  "top_k":        10,
  "weights":      [1.0, ...],              // optional, per query_vector
  "penalties":    {"category_name": 0.4}, // optional
  "query_text":   "spicy grilled food"    // optional; triggers vector store path
}
```

### 7.1 Preference Axis Extraction

**File:** `backend/preference_axes.py`

Converts a `PsychologicalProfile` into a list of `PreferenceAxis` objects used to
steer scoring.

```python
@dataclass(frozen=True)
class PreferenceAxis:
    name:      str
    rationale: str
    weight:    float
```

Three types of axes are produced:

**Value axes** (one per non-zero value keyword category):
```
weight = category_count / total_mentions
name   = "food" | "service" | "price" | "atmosphere"
```

**Rating bias axis** (added when |mean - 3.0| ≥ 0.5):
```
bias_label = "generous" if mean > 3.0 else "harsh"
weight = min(|mean - 3.0| / 2.0, 1.0)
```

**Cultural register axis** (added when code-switching detected):
```
weight = min(nigerian_english_index × 10, 1.0)
```

Axes are sorted by weight descending. The top axes represent what the user cares about
most and are used by the deliberative scorer to boost matching items.

### 7.2 Multi-Angle Retrieval

**File:** `backend/retrieval.py`

```python
multi_angle_retrieve(
    items:         Iterable[RetrievalItem],
    query_vectors: Sequence[np.ndarray],
    top_k:         int = 10,
    weights:       Sequence[float] | None = None,
) -> List[RetrievalResult]
```

For each candidate item, computes a weighted average cosine similarity across all
query vectors:

```
score(item) = Σ (cosine(item.vector, qᵢ) × wᵢ) / Σ wᵢ
```

This allows multiple angles of the user's preference to be expressed simultaneously
(e.g. `q₁ = "spicy food"`, `q₂ = "budget-friendly"`) with independent weights.

**Cosine similarity** is computed as:
```
cos(a, b) = dot(a, b) / (‖a‖ × ‖b‖)
```
Returns `0.0` when either vector is empty or either norm is zero.

Results are sorted by score descending and truncated to `top_k`.

**Vector store path**: when `query_text` is supplied and a `VectorStoreService` is
attached, items are fetched directly from the vector store using embedding similarity.
The `multi_angle_retrieve` call is bypassed in this case; the vector store's own
ranked results (already cosine-sorted) are used as `RetrievalResult` objects directly.
This preserves the correct ordering without redundant computation.

### 7.3 Deliberative Scoring

**File:** `backend/deliberative_scoring.py`

```python
deliberative_score(
    candidates: List[RetrievalResult],
    axes:       List[PreferenceAxis],
    penalties:  Dict[str, float] | None = None,
) -> List[ScoredRecommendation]
```

For each candidate:

```
axis_score    = Σ axis.weight  for each axis where axis.name ∈ candidate.metadata
penalty_score = Σ penalty_val  for each key   where key       ∈ candidate.metadata
final_score   = candidate.score + axis_score - penalty_score
```

The metadata-matching design means scoring is **item-specific**: an item tagged
`{"food": true}` receives the food-axis boost; an item without that key does not.
This is the mechanism by which the user's preference axes translate into differentiated
ranking.

**Explanation generation** per item:
```
"Similarity score 0.82; Matched axes: food, service; Conflicts: slow_service"
```

Results are sorted by `final_score` descending.

### 7.4 Non-LLM Path Output

```json
{
  "user_id": "u1",
  "axes": [
    {"name": "food", "rationale": "Mentions food in 4 reviews", "weight": 0.8},
    {"name": "rating_bias", "rationale": "Average rating 4.2 indicates a generous rater", "weight": 0.6}
  ],
  "recommendations": [
    {
      "item_id": "biz_01",
      "score": 1.62,
      "explanation": "Similarity score 0.82; Matched axes: food",
      "metadata": {"name": "Chicken Republic", "categories": "fast food"}
    }
  ]
}
```

---

## 8. Agent System

**Files:** `backend/agent_tools.py`, `backend/agent_orchestrator.py`,
`backend/agent_tool_defs.py`, `backend/task_b_agent_service.py`

The agent system implements a structured tool-calling loop that allows the Task B
pipeline to be driven by an LLM ordering its own steps.

### 8.1 Tool Registry

```python
class ToolRegistry:
    def register(name: str, func: Callable[[Dict], Dict]) -> None
    def run(call: ToolCall) -> ToolResult
    def has(name: str) -> bool
    def list_tools() -> List[str]
```

Tools are plain functions `Dict[str, object] → Dict[str, object]`. The registry decouples
tool definitions from the orchestrator and makes it easy to add or replace tools without
touching the planning logic.

### 8.2 Agent Orchestrator and $ref Resolution

**File:** `backend/agent_orchestrator.py`

`run_agent(registry, plan)` executes a list of `ToolCall` objects in order:

1. For each call, run `_resolve_args(call.arguments, context)` to substitute `$ref`
   placeholders with results from earlier tool calls.
2. Execute the tool via `registry.run(call)`.
3. Store the result in `context[call.name]`.

**`$ref` argument resolution:**

```python
{"$ref": "build_profile"}
```

resolves to the full output dict of the `build_profile` tool call.
References are resolved recursively so nested argument structures work:

```python
{"profile": {"$ref": "build_profile"}}
# → {"profile": {"user_id": "u1", "rating_stats": {...}, ...}}
```

This forms the data pipeline between steps: `extract_axes` receives the profile dict
produced by `build_profile`, and `score_candidates` receives the axes dict produced by
`extract_axes`.

`AgentOutput` contains the full step trace:
```python
@dataclass
class AgentOutput:
    steps: List[AgentStep]    # thought + tool_call + tool_result per step
    final: Dict[str, object]  # aggregated tool_results
```

### 8.3 Registered Tools

**File:** `backend/agent_tool_defs.py`

| Tool name | Function | Input | Output |
|---|---|---|---|
| `build_profile` | `_build_profile(profile_service, args)` | `{user_id, records}` | `PsychologicalProfile.to_dict()` |
| `extract_axes` | `_extract_axes(args)` | `{profile}` | `{axes: [PreferenceAxis.__dict__, ...]}` |
| `retrieve_candidates` | `_retrieve_candidates(args)` | `{candidates, query_vectors, top_k, weights}` | `{retrieved: [RetrievalResult.__dict__, ...]}` |
| `score_candidates` | `_score_candidates(args)` | `{candidates, axes, penalties}` | `{scored: [ScoredRecommendation.__dict__, ...]}` |

`_score_candidates` accepts axes in two forms:
- A plain list of `PreferenceAxis` objects (deterministic plan path)
- A dict `{"axes": [...]}` from a `$ref` to `extract_axes` output

In both cases it converts to `PreferenceAxis` objects before calling `deliberative_score`.

### 8.4 LLM Planning Path (TaskBAgentService)

**File:** `backend/task_b_agent_service.py`

When `use_llm=True`:

1. Build a list of four tool schemas with `additionalProperties: True` (permissive,
   since the LLM provides no useful arguments — just ordering).
2. Send a chat completion with `tool_choice="auto"`.
3. Parse the returned `tool_calls` list to extract the tool name ordering.
4. Build the plan by looking up each name in the deterministic plan's `arg_map`.
   This uses the LLM's **ordering** but the system's **arguments**.
5. If the LLM returns no tool calls or unrecognised names, fall back to the deterministic
   plan.

**Why this design**: the LLM's value is in deciding which steps to run and in what
order based on the context, not in generating correct arguments (it cannot, since it
has no access to the user data). The system provides correct arguments for any step
the LLM selects.

**Deterministic plan** (used directly when `use_llm=False`):

```
ToolCall("build_profile", {user_id, records})
    ↓
ToolCall("extract_axes",  {profile: {$ref: "build_profile"}})
    ↓
ToolCall("retrieve_candidates", {candidates, query_vectors, top_k, weights})
    ↓
ToolCall("score_candidates", {candidates, axes: {$ref: "extract_axes"}, penalties})
```

The `$ref` wiring ensures axes extracted from the user's profile flow automatically
into the scoring step.

---

## 9. Vector Store System

### 9.1 InMemoryVectorStore

**File:** `backend/vector_store.py`

```python
@dataclass
class InMemoryVectorStore:
    items: List[RetrievalItem]

    def add(item_id, vector, metadata) -> None
    def query(query_vector, top_k=10) -> List[RetrievalResult]
```

`query()` computes cosine similarity between `query_vector` and every stored vector,
sorts descending, returns the top `top_k`. O(n) per query — adequate for demo-scale
datasets; ChromaDB or FAISS can replace this for production scale.

Vectors are stored as `np.ndarray(dtype=float)` and added via the shared
`_cosine_similarity()` in `retrieval.py`.

### 9.2 Embedding Model

**File:** `backend/embeddings.py`

```python
@dataclass(frozen=True)
class EmbeddingModel:
    name:  str
    model: SentenceTransformer

load_embedding_model(model_name="all-MiniLM-L6-v2") → EmbeddingModel
embed_texts(embedding_model, texts: Iterable[str]) → List[List[float]]
```

`SentenceTransformer("all-MiniLM-L6-v2")` produces 384-dimensional unit vectors.
`show_progress_bar=False` suppresses tqdm output in API and test contexts.

The model is loaded once at `VectorStoreService.create()` time and reused for all
subsequent embed calls.

### 9.3 VectorStoreService Facade

**File:** `backend/vector_store_service.py`

```python
@dataclass
class VectorStoreService:
    store:           InMemoryVectorStore
    embedding_model: EmbeddingModel

    @classmethod
    def create(cls, model_name="all-MiniLM-L6-v2", store_path="") -> VectorStoreService

    def add_text_items(items: List[Dict], text_field: str) -> None
    def query(query_text: str, top_k=10) -> List[Dict]
```

`create()` behaviour:
- If `store_path` is set **and the file exists**: load via `load_vector_store(store_path)`.
  Logs: `INFO Loaded vector store from ... (N items)`.
- If `store_path` is set **but file is missing**: logs a `WARNING` and starts empty.
- If `store_path` is empty: starts empty with no log.

`query(query_text)` embeds the query string on-the-fly using the loaded model, runs
`store.query()`, and returns a list of `{item_id, score, metadata}` dicts sorted by
score descending.

### 9.4 JSON Persistence

**File:** `backend/vector_store_persist.py`

```python
save_vector_store(store: InMemoryVectorStore, path: str) -> None
load_vector_store(path: str) -> InMemoryVectorStore
```

Serialisation format:
```json
[
  {"item_id": "biz_01", "vector": [0.12, -0.34, ...], "metadata": {"name": "..."}},
  ...
]
```

`save_vector_store` writes via `Path.write_text()` (atomic on most POSIX systems).
`load_vector_store` reads, parses, and calls `store.add()` for each entry, restoring
full `np.ndarray` vectors.

### 9.5 Dataset Ingestion Pipeline

**Files:** `backend/ingest_embeddings.py`, `backend/ingest_datasets.py`

```python
ingest_dataset(
    dataset_path:    str,
    text_field:      str,
    id_field:        str,
    metadata_fields: List[str],
    model_name:      str = "all-MiniLM-L6-v2",
) -> InMemoryVectorStore
```

Steps:
1. Load all JSONL records from `dataset_path`.
2. Extract `text_field` from each record for embedding.
3. Embed in batch with `embed_texts()`.
4. For each record/vector pair, add to the store with `id_field` as item_id and
   `metadata_fields` as the metadata dict.

Dataset-specific helpers in `ingest_datasets.py` pre-fill the field names:

```python
ingest_yelp_reviews(path)      # text="text",        id="business_id"
ingest_amazon_reviews(path)    # text="reviewText",   id="asin"
ingest_goodreads_reviews(path) # text="review_text",  id="book_id"
```

### 9.6 CLI

**File:** `backend/cli.py`

```bash
python -m backend.cli \
  --dataset  yelp|amazon|goodreads \
  --input    /path/to/dataset.jsonl \
  --output   /path/to/vector_store.json
```

Calls the appropriate `ingest_*` helper then `save_vector_store()`. Suitable for a
one-time pre-processing step or a cron job when the dataset is refreshed.

---

## 10. Evaluation System

**Package:** `backend/evaluation/`

### 10.1 Metrics

**File:** `backend/evaluation/metrics.py`

All metrics are implemented in pure Python — no external scoring libraries required.

#### RMSE (Task A)

```
RMSE = sqrt( Σ (predicted_i - ground_truth_i)² / N )
```

Measures rating prediction error. Lower is better. Compared against the
mean-rating baseline to report `rmse_improvement`.

#### ROUGE-L (Task A)

Sentence-level F1 via Longest Common Subsequence (LCS):

```
precision = LCS_length / |hypothesis_tokens|
recall    = LCS_length / |reference_tokens|
F1        = 2 × precision × recall / (precision + recall)
```

The LCS is computed with a rolling two-row dynamic programming implementation
(`O(m × n)` time, `O(n)` space).

`rouge_l_corpus()` returns the mean F1 over all (hypothesis, reference) pairs.

#### NDCG@k (Task B)

Binary-relevance Discounted Cumulative Gain:

```
DCG  = Σ rel_i / log₂(rank + 2)         (for rank 0..k-1)
IDCG = DCG of ideal ordering
NDCG = DCG / IDCG
```

`rel_i = 1` if `ranked_items[i] ∈ relevant_items`, else `0`.

#### Hit Rate@k (Task B)

```
HR@k = 1  if any item in ranked_items[:k] is in relevant_items
       0  otherwise
```

Per-user binary metric; caller averages over the user set.

### 10.2 Task A Evaluation Runner

**File:** `backend/evaluation/task_a_eval.py`

```bash
python -m backend.evaluation.task_a_eval \
  --records data/records.jsonl \
  --split   0.8
```

Algorithm:
1. Temporal split (default 80/20).
2. For each test record:
   - Build profile from the user's train records.
   - Build `RatingCalibration(user_records, all_train_records)`.
   - Calibrate the user's mean rating → predicted rating.
   - Generate a template review.
3. Compute `persona_rmse` and `baseline_rmse` (global mean).
4. Compute `rouge_l` over (generated, reference) pairs where reference is non-empty.

Output JSON includes `rmse_improvement = baseline_rmse - persona_rmse`.

### 10.3 Task B Evaluation Runner

**File:** `backend/evaluation/task_b_eval.py`

```bash
python -m backend.evaluation.task_b_eval \
  --records data/records.jsonl \
  --store   data/vector_store.json \
  --k       10
```

Algorithm:
1. Temporal split (default 80/20).
2. For each user who has train records:
   - Build profile from train records.
   - Extract preference axes.
   - Embed the user's most recent review text as the query vector.
   - Query the vector store for top-k candidates.
   - Apply deliberative scoring.
   - Compare ranked list against the user's test-set item IDs (relevant set).
   - Record NDCG@k and Hit Rate@k.
3. Also compute baseline NDCG@k and Hit Rate@k using the popularity baseline.

Output JSON includes `ndcg_improvement` and per-metric persona vs baseline values.

### 10.4 Baselines

```python
mean_rating_baseline(ratings)           → float      # global mean
popularity_baseline(item_counts, k=10)  → List[str]  # top-k by interaction count
```

These are the minimum bars the system must beat. Both baselines are parameter-free
and serve as the denominator for improvement claims in the solution paper.

---

## 11. API Layer

**File:** `backend/app.py`

### 11.1 Endpoint Contracts

#### GET /health

```json
{ "status": "ok" }
```

#### GET /cold-start/questions

Returns the static elicitation question list.

```json
{
  "questions": [
    {
      "id": "rating_tendency",
      "question": "When you enjoy something...",
      "options": ["top_marks", "reserve_top"]
    },
    ...
  ]
}
```

#### POST /cold-start/answer

**Request:**
```json
{
  "user_id": "u_new",
  "answers": [
    {"question_id": "rating_tendency",   "answer": "top_marks"},
    {"question_id": "value_priority",    "answer": "food_quality"},
    {"question_id": "review_style",      "answer": "brief_and_direct"},
    {"question_id": "cultural_register", "answer": "sometimes"}
  ]
}
```

**Response:** `PsychologicalProfile.to_dict()` — identical schema to `/profile/build`.

**Errors:** 400 if `user_id` is empty or `answers` is empty.

#### POST /profile/build

**Request:**
```json
{
  "user_id": "u1",
  "records": [
    {
      "item_id": "biz_01",
      "rating": 4.0,
      "review_text": "The jollof rice was excellent.",
      "timestamp": "2023-06-15",
      "source": "yelp"
    }
  ]
}
```

**Response:**
```json
{
  "user_id": "u1",
  "rating_stats":    { "count": 1, "mean": 4.0, "std_dev": 0.0, "min_rating": 4.0, "max_rating": 4.0 },
  "stylometry":      { "avg_review_length": 29.0, "avg_word_count": 5.0, "vocab_richness": 1.0, "avg_sentence_length": 5.0 },
  "value_keywords":  { "food": 1, "service": 0, "price": 0, "atmosphere": 0 },
  "trajectory":      { "early_mean_rating": 0.0, "recent_mean_rating": 0.0, ... },
  "cultural_signals":{ "nigerian_english_index": 0.0025, "code_switching_detected": false, "pidgin_term_hits": 0 }
}
```

**Errors:** 400 if `user_id` is empty.

#### POST /task-a/simulate

**Request:**
```json
{
  "user_id": "u1",
  "records": [ ... ],
  "target_item": { "name": "Kilimanjaro Restaurant", "description": "Nigerian cuisine" },
  "population_records": [ ... ],
  "use_llm": false
}
```

**Response:**
```json
{
  "user_id": "u1",
  "target_item": { "name": "Kilimanjaro Restaurant", "description": "Nigerian cuisine" },
  "predicted_rating": 3.9,
  "reasoning": "Rating derived from user mean with calibration.",
  "review_text": "Really enjoyed this. The food was the highlight. Kilimanjaro Restaurant delivered what I was looking for. Abeg, try am yourself and see."
}
```

**Errors:** 400 if `user_id` or `target_item` is missing.

#### POST /task-b/recommend

**Request:**
```json
{
  "user_id": "u1",
  "records": [ ... ],
  "query_text": "spicy grilled food Lagos",
  "top_k": 10
}
```

or with explicit vectors:

```json
{
  "user_id": "u1",
  "records": [ ... ],
  "query_vectors": [[0.12, -0.34, ...]],
  "candidates": [{"item_id": "c1", "vector": [...], "metadata": {"food": true}}],
  "top_k": 5,
  "weights": [1.0],
  "penalties": {"slow_service": 0.3}
}
```

**Response:**
```json
{
  "user_id": "u1",
  "axes": [
    {"name": "food", "rationale": "Mentions food in 4 reviews", "weight": 0.8}
  ],
  "recommendations": [
    {
      "item_id": "biz_01",
      "score": 1.62,
      "explanation": "Similarity score 0.82; Matched axes: food",
      "metadata": { "name": "Chicken Republic", "food": true }
    }
  ]
}
```

**Errors:** 400 if `user_id` is missing; 400 if neither `query_text` nor `query_vectors`
is provided; 400 if `candidates` is missing when `query_text` is not provided.

#### POST /task-b/agent

Identical request shape to `/task-b/recommend` (without `query_text`). Additional field:

```json
{ "use_llm": false }
```

**Response:**
```json
{
  "user_id": "u1",
  "steps": [
    {"thought": "Calling build_profile", "tool": "build_profile", "result": { ... }},
    {"thought": "Calling extract_axes",   "tool": "extract_axes",  "result": { ... }},
    {"thought": "Calling retrieve_candidates", ...},
    {"thought": "Calling score_candidates",    ...}
  ],
  "final": {
    "tool_results": [ {...}, {...}, {...}, {...} ]
  }
}
```

**Errors:** 400 if `user_id`, `query_vectors`, or `candidates` is missing.

### 11.2 Trace-ID Middleware

Every request gets a `X-Trace-Id` header (UUID v4, or forwarded from the caller):

```python
@app.middleware("http")
async def add_trace_id(request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Trace-Id"] = trace_id
    logger.info("request_completed", extra={"trace_id": trace_id})
    return response
```

The trace ID is included in all log lines via `TraceIdFilter` in `logging_utils.py`,
enabling full request correlation in log aggregation systems.

---

## 12. Infrastructure

### 12.1 Configuration

**File:** `backend/config.py`

All settings are read from environment variables at import time via `app_config_from_env()`.

```python
@dataclass(frozen=True)
class AppConfig:
    deterministic_mode:         bool
    profile_cache_ttl_seconds:  int
    profile_cache_max_size:     int
    enable_llm:                 bool
    openai_api_key:             str
    openai_model:               str
    vector_store_path:          str
```

Helper functions handle type coercion with defaults:
- `_get_bool_env(name, default)` — recognises `"1"`, `"true"`, `"yes"`, `"y"`.
- `_get_int_env(name, default)` — falls back to `default` on empty string.
- `os.getenv(name, "").strip()` — for optional string fields.

`_get_env(name)` raises `ValueError` for missing required env vars (used for dataset
paths when the loaders are called, not at app startup).

**`DatasetPaths`** is a separate frozen dataclass constructed by `dataset_paths_from_env()`
and only needed when the data loaders are called directly (evaluation scripts, CLI).

### 12.2 TTL + LRU Cache

**File:** `backend/cache.py`

```python
class TTLCache(Generic[K, V]):
    def __init__(self, max_size: int, ttl_seconds: int)
    def get(key: K) -> Optional[V]
    def set(key: K, value: V) -> None
    def size() -> int
```

Implemented on `collections.OrderedDict` with two eviction policies:
- **TTL**: entries expire `ttl_seconds` after insertion. Checked on `get()`; expired
  entries are removed lazily.
- **LRU**: when `len > max_size`, the oldest entry (front of the ordered dict) is
  evicted. `set()` and successful `get()` both move entries to the end (most-recent).

Both policies interact safely: an expired entry that is also the LRU candidate is
removed by the TTL check before LRU eviction would need to consider it.

### 12.3 Profile Service Caching

**File:** `backend/services/profile_service.py`

`ProfileService.build_profile_cached(user_id, records)` caches profiles keyed by a
SHA-256 hash of the serialised `(user_id, records)` payload. This means:
- Same user with same records → cache hit.
- Same user with any change in records → cache miss (recomputes).

The hash payload includes `item_id`, `rating`, `review_text`, `timestamp`, and `source`
for each record (not `metadata`, which is considered non-semantic for profiling).

Default cache: 1000 entries, 1-hour TTL (both configurable via env vars).

### 12.4 LLM Client and Retry Policy

**File:** `backend/llm_client.py`

```python
class OpenAIClient:
    def chat_completion(messages, tools=None, tool_choice=None, temperature=0.2) -> Dict
```

**Retry policy** (wrapped around `client.chat.completions.create()`):

| Attempt | Delay before | Exceptions caught |
|---|---|---|
| 1 (first try) | none | — |
| 2 | 1 s | `RateLimitError`, `APIStatusError` with code in {429,500,502,503,504} |
| 3 | 2 s | same |
| raise | — | same (after 3 attempts exhausted) |

Exponential backoff doubles the delay per retry. Non-retryable `APIStatusError` codes
(e.g. 400 Bad Request, 401 Unauthorized) are re-raised immediately.

`OpenAIClient` is only instantiated when `ENABLE_LLM=true` and `OPENAI_API_KEY` is set
(via `llm_factory.create_openai_client()`). All service constructors accept
`llm_client=None` and degrade gracefully to the template/deterministic path.

### 12.5 Structured Logging and Request Tracing

**File:** `backend/logging_utils.py`

Log format:
```
2026-05-21 10:15:43,201 INFO trace_id=3f8a1b2c-... request_completed
```

`TraceIdFilter` adds `trace_id="-"` to any log record that does not already have a
`trace_id` attribute, ensuring the format string always resolves (background threads,
startup logs, test output).

`configure_logging()` is called once at `app.py` import time. It uses `basicConfig`
with `level=INFO` and attaches the filter to the root logger.

### 12.6 Docker and Compose

**`backend/Dockerfile`**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY .. .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`docker-compose.yml`**
```yaml
services:
  api:
    build: { context: ., dockerfile: backend/Dockerfile }
    ports:  ["8000:8000"]
    env_file: [.env]
    volumes: ["./data:/data"]          # exposes CLI-built vector stores
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

`./data` is mounted read-write so the CLI can write vector store JSON files inside
the container's `/data` path, which then persist on the host for subsequent runs.

---

## 13. Design Decisions

### Why in-memory vector store instead of ChromaDB or FAISS?

The PRD listed ChromaDB but the actual implementation uses a custom in-memory store.
Rationale: zero external service dependency (no Docker sidecar needed), full control
over persistence format (plain JSON, readable and debuggable), and O(n) cosine scan
is fast enough for demo-scale datasets (tens of thousands of items). The interface
(`add`, `query`) is stable and can be replaced with a production vector database behind
the same `VectorStoreService` facade without changing any API or pipeline code.

### Why template-based review generation rather than always using LLM?

Templates produce deterministic, latency-free output that can be run without an API key.
This satisfies the PRD requirement for a deterministic demo mode and makes evaluation
reproducible. The LLM path is available when `use_llm=True` and is intended as the
production-quality path; the template path is the fallback and baseline.

### Why per-candidate metadata matching in deliberative scoring?

An earlier implementation added `axis_score = sum(axis.weight for axis in axes)` as a
global constant to every candidate's score — a no-op for ranking. The corrected design
matches axis names against candidate metadata keys so only items that are actually
relevant to the user's axes receive a boost. This requires dataset ingestion to populate
metadata fields that correspond to axis names (e.g. `"food": true` for food-category
items).

### Why SHA-256 hash as cache key instead of (user_id, record_count)?

A count-based key would produce false cache hits when records change (e.g. a record is
updated with a corrected rating). The hash covers all semantically relevant fields and
produces a different key on any data change while remaining collision-resistant.

### Why profile_service is module-level in app.py?

FastAPI's module-level initialisation means `ProfileService` (and its `TTLCache`) are
shared across all requests in a single process — the intended behaviour. The cache is
not request-scoped. In a multi-worker deployment each worker has its own cache, which
is acceptable since the cache is advisory (not authoritative).

### Why is `timestamp_key` public in `data/split.py`?

`trajectory.py` needs the same timestamp parsing logic. Duplicating it would create a
maintenance burden. Making it public and importing it is preferable to importing a
private function (which signals it is not part of the module's contract).

---

## 14. Extension Points

| Feature | Current implementation | Upgrade path |
|---|---|---|
| Vector database | `InMemoryVectorStore` (O(n) cosine scan) | Drop-in `ChromaDBVectorStore` behind `VectorStoreService` |
| LLM provider | OpenAI via `llm_client.py` | Add `AnthropicClient` / `OllamaClient` with same `chat_completion()` interface; update `llm_factory.py` |
| Review generation | Template-based (`review_generator.py`) | Extend `TaskAService.simulate_review()` with BERTScore-ranked template selection or structured LLM prompting |
| Evaluation | ROUGE-L only for text quality | Add `rouge-score` package for ROUGE-1/2, add `bert-score` package for BERTScore |
| Cold-start elicitation | 4 fixed questions | Add adaptive question selection based on partial answer uncertainty |
| Cultural signals | 12 fixed pidgin terms | Expand dictionary from sociolinguistic corpus; add Yoruba, Igbo, Hausa term sets |
| Cross-domain retrieval | Single dataset vector store | Support multiple stores and merge results with source-specific weights |
| Ablation studies | Manual | Add `evaluation/ablation.py` that runs evaluation with each profile layer zeroed out |
| Multi-turn recommendation | Not implemented | Add session state to `/task-b/recommend` to update constraints across turns |
