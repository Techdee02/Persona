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

- Frontend: React + TypeScript + Tailwind CSS
- Backend API: FastAPI (Python)
- LLM: Claude (Sonnet) or equivalent LLM API
- Embeddings: sentence-transformers or OpenAI embeddings
- Vector Store: ChromaDB
- Containerization: Docker Compose

## UI Experience

Task A UI flow:
- Select user profile
- Input item description
- View rating prediction reasoning and generated review
- Compare against real review

Task B UI flow:
- Select user or start cold-start conversation
- See the reasoning trace before recommendations appear
- View ranked recommendation cards with explanations
- Refine via multi-turn conversation (constraints update live)

## Repo Layout (Planned)

- frontend/        React app
- backend/         FastAPI app
- data/            Dataset loaders and preprocessing
- models/          Profile engine and LLM prompts
- evaluation/      Metrics and ablation scripts
- docker-compose.yml

## Next Steps

1. Scaffold the frontend and backend folders
2. Implement signal extraction and profile construction
3. Build Task A rating and review pipeline
4. Build Task B retrieval and reasoning pipeline
5. Run evaluations and ablation studies
6. Finalize solution paper and submission

## License

TBD