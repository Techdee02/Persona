# Backend AI/ML Phases

Owner: Backend AI/ML Developer
Last updated: 2026-05-20

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

## Phase 3: Full-Grade Refinement

Goal: maximize scoring and polish with additional features and deeper modeling.

Deliverables:
- Living trajectory features (early vs recent behavior)
- Nigerian English detection and code-switching preservation
- Enhanced preference axis extraction
- Deliberative scoring improvements with conflict resolution
- Ablation study automation
- Cross-domain transfer logic in retrieval
- Demo-friendly explanation quality improvements

Acceptance criteria:
- Clear lift over Phase 2 baselines in key metrics
- Outputs show culturally grounded explanations
- Ablation study results ready for the solution paper

## Phase Risks and Mitigations

- LLM instability: add deterministic mode, caching, and trace snapshots
- Data sparsity: rely on bootstrapped profile priors for cold-start
- Latency: restrict prompt size and add retrieval caching

## Open Questions

- Which LLM is final for demo and judging?
- How large should the reasoning trace be before truncation?
- What features are mandatory for final scoring vs optional polish?
