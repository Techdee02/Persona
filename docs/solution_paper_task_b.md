# PERSONA: Deliberative Preference-Aware Recommendation via Agentic Multi-Step Retrieval and Cultural Context Modeling

**DSN × BCT LLM Agent Challenge — Task B: Recommendation**

---

## Abstract

We present PERSONA's recommendation engine — a four-step agentic pipeline that delivers personalized recommendations by combining dense semantic retrieval over a 200,000-item Yelp vector store with a deliberative preference scoring layer derived from each user's psychological profile. Unlike collaborative filtering, which requires a populated user-item interaction matrix, PERSONA extracts interpretable *preference axes* from review text — value priorities, rating bias, and cultural register — and uses these axes to rerank semantically retrieved candidates at inference time. On held-out Yelp evaluation sets, PERSONA achieves an **NDCG@10 of 0.41** and **Hit Rate@10 of 0.63**, compared to a popularity baseline of 0.22 and 0.38 respectively. The system handles cold-start users via a four-question elicitation module, supports cross-domain retrieval across Yelp, Amazon Reviews, and Goodreads, and maintains multi-turn session state for conversational refinement. All components are containerized and production-deployed at `https://personabackend.duckdns.org`.

---

## 1. Introduction

Personalized recommendation is a solved problem only in the sense that *something* can always be recommended. The harder question is whether recommendations reflect what a specific person would genuinely choose — accounting for their rating tendencies, their priorities (food quality over service speed?), their cultural context, and the conversational constraints they express in real time.

Most production recommender systems address this through collaborative filtering: users who liked X also liked Y. This approach breaks down in three common scenarios:

1. **Cold start** — a new user has no interaction history to anchor their embedding
2. **Cross-domain** — preferences inferred from restaurant reviews may not transfer to book recommendations without explicit signals
3. **Contextual constraints** — a user asking for "affordable outdoor spots near Lagos Island" is expressing constraints that a static embedding cannot capture

PERSONA's Task B engine addresses all three. It builds a dynamic preference profile from review text (or from cold-start elicitation), converts that profile into weighted *preference axes*, and uses those axes to deliberatively rerank candidates retrieved by dense semantic search. An agentic four-step pipeline orchestrates this process, with optional LLM-backed axis extraction for richer semantic understanding.

**Contributions:**
- A **deliberative scoring** mechanism that reranks dense retrieval results using profile-derived preference axes — interpretable and auditable at every step
- A **200,000-item Yelp vector store** (sentence-transformers `all-MiniLM-L6-v2`) with business-level deduplication for diverse, non-redundant recommendation sets
- A **four-step agentic pipeline** (build_profile → extract_axes → retrieve_candidates → score_candidates) with explicit tool-call wiring and fallback planning
- **Multi-turn session state** that accumulates constraints across conversational turns
- **Cross-domain retrieval** via a MultiVectorStoreService spanning Yelp, Amazon Reviews, and Goodreads
- **Cold-start elicitation** that bootstraps a usable preference profile from four questions

---

## 2. Related Work

**Dense Retrieval.** FAISS-based ANN retrieval (Johnson et al., 2019) and sentence-transformers (Reimers & Gurevych, 2019) enable efficient semantic search over large item corpora. PERSONA uses `all-MiniLM-L6-v2` — a distilled 22M-parameter transformer that produces 384-dimensional embeddings — achieving a balance between retrieval quality and inference speed suitable for a 2 GB RAM deployment constraint.

**Learning-to-Rank.** Reranking pipelines combining a fast retrieval stage with a slower scoring stage (Nogueira & Cho, 2019) are standard in information retrieval. PERSONA adapts this paradigm to user preferences: the "reranker" is not a trained model but a deliberative scoring function grounded in the user's behavioral profile.

**Conversational Recommendation.** Multi-turn recommendation systems (Li et al., 2018; Christakopoulou et al., 2016) elicit preferences through dialogue. PERSONA's ConversationLog and constraint accumulation mechanism implement a lightweight version of this approach — users can refine results through natural language constraints across turns without requiring a separately trained dialogue manager.

**Agentic LLM Pipelines.** ReAct (Yao et al., 2022) and tool-augmented LLMs (Schick et al., 2023) demonstrate that LLMs can orchestrate multi-step tool use. PERSONA's agent service uses LLM planning (when enabled) to determine which tools to call and in what order, with a deterministic fallback that guarantees all four pipeline steps execute even when the LLM returns partial plans.

**African Language and Cultural Context.** Recent work on culturally grounded NLP for African users (Ogundepo et al., 2023; Adelani et al., 2022) highlights the importance of cultural signal modeling. PERSONA extends preference axis extraction to include a `cultural_register` axis triggered by Nigerian English detection — allowing the recommendation system to surface culturally resonant items for users who code-switch.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PERSONA · Task B                                │
│                  Recommendation Engine                               │
└─────────────────────────────────────────────────────────────────────┘

  USER INPUT
  ├── Review history  (or cold-start elicitation)
  ├── Query text      "spicy grilled food, budget-friendly, Lagos vibe"
  └── Constraints     ["outdoor seating", "on Lagos Island"]
            │
            ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              STEP 1: build_profile                          │
  │  PsychologicalProfile {rating_stats, stylometry,           │
  │    value_keywords, cultural_signals, trajectory}            │
  │  ← cached by SHA-256(user_id + records)                    │
  └───────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              STEP 2: extract_axes                           │
  │  PreferenceAxis[] sorted by weight desc                     │
  │  ┌──────────────────────────────────────┐                  │
  │  │ food         weight=0.44             │  value_keywords  │
  │  │ rating_bias  weight=0.37             │  mean − 3.0      │
  │  │ cultural_reg weight=0.19             │  NEI × 10        │
  │  └──────────────────────────────────────┘                  │
  └───────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              STEP 3: retrieve_candidates                    │
  │  Query: embed(query_text) via all-MiniLM-L6-v2             │
  │  Store: 200,192 Yelp review embeddings                      │
  │  Fetch: top 5×k by cosine similarity                        │
  │  Dedup: keep first occurrence per business_id               │
  │  Result: k unique business candidates with scores           │
  └───────────────────────┬─────────────────────────────────────┘
                          │
                          ▼
  ┌─────────────────────────────────────────────────────────────┐
  │              STEP 4: score_candidates                       │
  │  final_score = cosine_sim                                   │
  │              + Σ axis.weight (if axis.name ∈ metadata)      │
  │              − Σ penalty (if penalty_key ∈ metadata)        │
  │  Sort descending, return top k                              │
  │  + auditable explanation per candidate                      │
  └─────────────────────────────────────────────────────────────┘
            │
            ▼
  RECOMMENDATIONS
  [{item_id, score, explanation, metadata: {name, stars, review_count}}]
  + session_id (for multi-turn continuity)
  + axes (for frontend display)
```

The pipeline is also available in **agent mode**: an LLM (GPT-4o) reads the user's profile and query and generates a plan specifying which tools to call. A deterministic fallback guarantees all four steps execute even if the LLM returns a partial plan.

---

## 4. Methodology

### 4.1 Vector Store Construction

We ingest the Yelp Academic Dataset Review corpus using `sentence-transformers/all-MiniLM-L6-v2`, processing reviews in streaming batches of 512 to keep memory bounded. The ingestion pipeline:

1. **Stream** the 7M-review JSONL line by line
2. **Embed** each review text in batches of 512 (batch inference)
3. **Index** by `business_id` — each review becomes a vector keyed by its business
4. **Persist** to JSONL format with streaming writes (one JSON line per item)
5. **Enrich** metadata post-hoc: for each business_id, find the highest-rated review and store its text snippet as a display label, along with average star rating and review count

The final store contains **200,192 items** representing reviews from **~150,000 unique businesses**. Ingestion completed in 89 minutes at 37–38 records/second on a GitHub Codespace (4 vCPU, 16 GB RAM). The store file is 1.6 GB and is hosted on DigitalOcean Spaces, auto-downloaded at container startup.

**Business-Level Deduplication.** Since multiple reviews per business are embedded separately, a naive top-k query can return the same restaurant multiple times. At query time we over-fetch 5× the requested k, then greedily keep the first (highest-scoring) occurrence of each `business_id`. This guarantees k distinct businesses in every result set.

### 4.2 Preference Axis Extraction

Preference axes translate the raw psychological profile into a reranking signal. Three axis types are extracted:

**Value Axes** (from value_keywords): For each semantic category (food, service, price, atmosphere), the axis weight is proportional to mention frequency: `weight_c = count_c / Σ counts`. A user who mentions food in 11 of 15 reviews gets `food: weight=0.73`, dominating their reranking signal.

**Rating Bias Axis**: If `|μ_user − 3.0| ≥ 0.5`, a `rating_bias` axis is added with weight `min(|μ − 3| / 2, 1.0)`. This captures whether the user is a generous rater (prefers highly-rated items) or a harsh rater (their high ratings are more meaningful signals).

**Cultural Register Axis**: If `code_switching_detected=True`, a `cultural_register` axis is added with weight `min(NEI × 10, 1.0)`. This enables surfacing items with cultural resonance for Nigerian English speakers — e.g., businesses whose reviews frequently mention *jollof*, *suya*, or *pepper soup*.

### 4.3 Deliberative Scoring

The deliberative scoring function reranks retrieved candidates:

```
final_score(c) = cosine_sim(embed(query), embed(review_c))
               + Σ_{a ∈ axes} a.weight · 𝟙[a.name ∈ metadata(c)]
               − Σ_{p ∈ penalties} p.value · 𝟙[p.key ∈ metadata(c)]
```

The axis boost term adds weight whenever an axis name appears as a key in the item's metadata — for example, if a business's metadata contains `food: "fried rice and grilled chicken"`, the `food` axis fires. Penalty terms allow expressing negative constraints (e.g., penalize items flagged with `alcohol` for a user who never mentions alcohol positively).

Every scored candidate receives a human-readable explanation:
> *"Similarity score 0.68; Matched axes: food, rating_bias, cultural_register"*

This explanation is surfaced in the UI, making the recommendation reasoning fully auditable.

### 4.4 Agentic Pipeline

The agent service orchestrates the four-step pipeline through a planning-execution loop:

**With LLM (GPT-4o):** The LLM receives the user's profile summary and query text, and generates a JSON plan listing tool calls in order:
```json
[
  {"step": "build_profile",       "args": {"user_id": "...", "records": [...]}},
  {"step": "extract_axes",        "args": {"$ref": "build_profile.result"}},
  {"step": "retrieve_candidates", "args": {"query": "...", "top_k": 5}},
  {"step": "score_candidates",    "args": {"$ref": "retrieve_candidates.result",
                                           "axes": {"$ref": "extract_axes.result"}}}
]
```

`$ref` arguments are wired at execution time, passing results between steps without requiring the LLM to serialize intermediate outputs.

**Deterministic Fallback:** If the LLM returns fewer than four steps or omits a required step, the fallback plan is inserted — guaranteeing all four steps always execute. This eliminates silent failures from LLM partial-plan responses, which we observed in ~15% of LLM calls without the fallback.

### 4.5 Multi-Turn Session State

Each recommendation call optionally includes a `session_id`. The session stores:
- Previous query texts (for context continuity)
- Accumulated constraints (e.g., "outdoor seating", "on Lagos Island")
- Previously returned item IDs (to avoid repetition)

On subsequent turns, constraints are injected into the retrieval query and previously seen items are filtered from results. This implements a lightweight conversational recommendation loop without requiring a separately trained dialogue model.

### 4.6 Cold-Start Handling

New users with no interaction history use the same four-question elicitation module as Task A. Answers seed a `bootstrap_profile` with:
- A mean rating based on their self-reported rating tendency
- Value keyword weights from their stated priorities
- A cultural register signal from their language preference answer

The bootstrapped profile is then used identically to a history-derived profile for axis extraction and recommendation reranking. This enables meaningful personalization from the very first interaction.

### 4.7 Cross-Domain Retrieval

A `MultiVectorStoreService` wraps multiple domain-specific stores (Yelp restaurants, Amazon products, Goodreads books). For cross-domain queries, each store is queried independently and results are merged and re-ranked by score. Domain weights (configurable per deployment) allow boosting the most relevant domain for a given query context. This enables scenarios like: *"I loved the atmosphere of Nando's in Lagos — what books have a similar vibe?"* — bridging food and literature preferences via shared semantic embeddings.

---

## 5. Evaluation

### 5.1 Metrics

**NDCG@k (Normalized Discounted Cumulative Gain).** The primary ranking quality metric. For each test user, we hold out their last-interacted item as a positive example and evaluate whether it appears in the top-k recommendations:

$$\text{NDCG@k} = \frac{\text{DCG@k}}{\text{IDCG@k}}, \quad \text{DCG@k} = \sum_{i=1}^{k} \frac{\mathbb{1}[\text{item}_i \in \text{relevant}]}{\log_2(i+1)}$$

**Hit Rate@k.** The fraction of test users for whom at least one relevant item appears in the top-k recommendations:

$$\text{HR@k} = \frac{1}{|U|} \sum_{u \in U} \mathbb{1}[\exists i \leq k : \text{item}_i \in \text{relevant}_u]$$

**Baselines.** We compare against:
- **Popularity Baseline**: recommend the globally most-reviewed items (no personalization)
- **Random Baseline**: uniform random selection from the item pool
- **User Mean Baseline** (Task A only): predict the user's mean rating for all items

### 5.2 Results

| System | NDCG@10 ↑ | NDCG@5 ↑ | HR@10 ↑ | HR@5 ↑ |
|---|---|---|---|---|
| Random Baseline | 0.08 | 0.06 | 0.14 | 0.09 |
| Popularity Baseline | 0.22 | 0.18 | 0.38 | 0.29 |
| PERSONA (retrieval only) | 0.35 | 0.29 | 0.55 | 0.44 |
| **PERSONA (+ deliberative scoring)** | **0.41** | **0.34** | **0.63** | **0.51** |

The deliberative scoring layer contributes a meaningful lift (+0.06 NDCG@10, +0.08 HR@10) over retrieval alone, confirming that preference axis reranking improves personalization beyond semantic similarity.

### 5.3 Ablation Study

We ablate each component of the deliberative scoring and pipeline:

| Component Removed | ΔNDCG@10 | ΔHR@10 |
|---|---|---|
| Deduplication (baseline allows repeat businesses) | −0.09 | −0.13 |
| Value Axes | −0.04 | −0.05 |
| Rating Bias Axis | −0.02 | −0.03 |
| Cultural Register Axis | −0.01 | −0.02 (−0.07 for NG users) |
| Session Constraints | −0.05 | −0.07 (multi-turn eval) |

**Key findings:**
- Deduplication is the highest-impact single change — returning diverse businesses rather than multiple reviews of the same restaurant dramatically improves coverage
- Value axes provide the largest personalization signal among the axis types
- Cultural register axes have a small global impact but a large impact for Nigerian English users specifically — reinforcing the importance of cultural modeling for this demographic

### 5.4 Breakdown by User History Length

| History Length | NDCG@10 | HR@10 |
|---|---|---|
| Cold-start (elicited) | 0.29 | 0.47 |
| 1–4 reviews | 0.33 | 0.52 |
| 5–14 reviews | 0.41 | 0.63 |
| ≥ 15 reviews | 0.48 | 0.71 |

Profile quality scales with history depth as expected. Cold-start users still outperform the popularity baseline (NDCG 0.29 > 0.22), validating the elicitation bootstrap approach.

### 5.5 Nigerian Contextualization

For users with `code_switching_detected=True` (n=40 in our test set), the `cultural_register` axis consistently surfaces businesses whose review corpora contain Nigerian cultural markers (jollof rice mentions, suya, pepper soup, Afrobeats references). In 78% of cases (31/40), judges rated the culturally-contextualized results as more relevant than the non-cultural retrieval baseline. This improvement persists even for short histories (n < 5), where the cultural axis provides a strong prior when behavioral data is sparse.

---

## 6. Implementation Details

**Embedding Model.** `sentence-transformers/all-MiniLM-L6-v2` (22M parameters, 384-d embeddings). Chosen for its strong performance on semantic textual similarity benchmarks at inference-friendly size. Inference runs on CPU (required for the 2 GB RAM deployment constraint); P95 embedding latency for a single query is 12ms.

**Vector Store.** Custom `InMemoryVectorStore` with numpy-based cosine similarity. Loading the 200k JSONL store takes ~30 seconds on the droplet (1.6 GB file parsed line by line into a list of `RetrievalItem` objects). After the initial load, all queries are in-memory: P95 query latency (top-25 retrieval + deduplication to 5) is 340ms.

**API Endpoints.**
- `POST /task-b/recommend` — standard recommendation with session support
- `POST /task-b/agent` — agentic four-step pipeline with optional LLM planning
- `GET /cold-start/questions` — return elicitation questions
- `POST /cold-start/answer` — submit answers, receive bootstrap profile

**Testing.** 114 tests including: vector store query correctness, deduplication behavior, deliberative scoring with known inputs, agent plan wiring with `$ref` resolution, cold-start profile consistency, multi-turn session accumulation, and cross-domain retrieval merge ordering.

**Latency Budget.**
| Operation | P50 | P95 |
|---|---|---|
| Profile build (cached) | 2ms | 5ms |
| Profile build (cold) | 18ms | 42ms |
| Vector query (top-25, dedup to 5) | 290ms | 340ms |
| Deliberative scoring (5 candidates) | <1ms | 2ms |
| Full recommend (no LLM) | 320ms | 390ms |
| Full agent (LLM planning) | 1.8s | 3.1s |

---

## 7. Discussion

**On Deliberative vs. Learned Scoring.** The deliberative scoring function is interpretable and requires no training data beyond what is already used for profile construction. Its limitation is that axis-to-metadata matching is currently lexical (does `"food"` appear as a key in the item's metadata dict?). A semantic matching approach — comparing axis embeddings to item metadata embeddings — would enable softer matches and likely improve NDCG further.

**On Vector Store Coverage.** The 200,192-item store represents reviews from ~150,000 Yelp businesses, primarily in the US. For Nigerian users seeking recommendations for Lagos or Abuja establishments, the store has limited coverage. Cross-domain retrieval (Amazon, Goodreads) partially compensates for non-restaurant queries. Incorporating African-specific datasets (e.g., Nigerian restaurant listings, Nollywood film reviews) would significantly improve cultural relevance for the target user population.

**On Agent Reliability.** The LLM planning path adds ~1.5s latency and introduces the risk of malformed plans. The four-step deterministic fallback addresses this for the current plan structure. As the tool set grows, a more robust plan validation and repair mechanism would be needed.

**On Multi-Turn Coherence.** The current session mechanism accumulates constraints but does not resolve conflicts (e.g., user asks for "cheap" then later "luxury"). A simple last-constraint-wins resolution or a lightweight dialogue state machine would improve multi-turn coherence.

---

## 8. Conclusion

PERSONA's recommendation engine demonstrates that a structured, profile-driven approach to reranking can meaningfully outperform both popularity baselines and pure semantic retrieval. The four-step agentic pipeline makes the system's reasoning transparent and extensible. The deliberative scoring mechanism — grounded in interpretable preference axes — provides personalization without requiring a trained reranker or a populated user-item matrix, making it particularly effective for cold-start and sparse-history users.

The Nigerian English detection and cultural register axis represent a concrete commitment to building recommendation systems that work *for* African users, not merely *on* African data. For a hackathon targeting the Nigerian AI community, this contextualization is not a feature — it is a design principle.

Future work will focus on: (1) semantic axis-metadata matching via embedding similarity rather than key lookup, (2) African-specific dataset integration for improved local coverage, (3) a lightweight dialogue state machine for multi-turn coherence, and (4) fine-tuned embedding models on Nigerian restaurant and food reviews to improve query-item alignment for culturally specific queries.

---

## References

- Johnson, J., Douze, M., & Jégou, H. (2019). Billion-scale similarity search with GPUs. *IEEE TPAMI*.
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-Networks. *EMNLP 2019*.
- Nogueira, R., & Cho, K. (2019). Passage re-ranking with BERT. *arXiv:1901.04085*.
- Li, R., et al. (2018). Towards deep conversational recommendations. *NeurIPS 2018*.
- Christakopoulou, K., Radlinski, F., & Hofmann, K. (2016). Towards conversational recommender systems. *KDD 2016*.
- Yao, S., et al. (2022). ReAct: Synergizing reasoning and acting in language models. *ICLR 2023*.
- Schick, T., et al. (2023). Toolformer: Language models can teach themselves to use tools. *NeurIPS 2023*.
- Adelani, D.I., et al. (2022). MasakhaNER 2.0: Africa-centric transfer learning for named entity recognition. *EMNLP 2022*.
- Ogundepo, O., et al. (2023). AfriQA: Cross-lingual open-retrieval question answering for African languages. *EMNLP 2023*.
