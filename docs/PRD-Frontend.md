# Persona Frontend PRD

Owner: Frontend Developer  
Backend owner: AI/ML Team  
Last updated: 2026-05-22  
Competition deadline: 24 May 2026

---

## 1. Goal

Build a production-quality web app that demonstrates Persona's psychological profile engine,
reasoning trace, and recommendation outputs for Task A and Task B. The UI must be compelling
enough to impress hackathon judges while being stable enough for a live demo.

---

## 2. Deployment Topology

```
User → Vercel (Next.js frontend)
              ↓ HTTPS REST API
         DigitalOcean Droplet (FastAPI backend)
              ↓
         50k Yelp vector store (loaded into memory)
```

**Base URL:** Set via environment variable.

```
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

All API calls are `fetch(process.env.NEXT_PUBLIC_API_URL + "/endpoint", ...)`.

**CORS:** The backend allows requests from the Vercel origin only (configured in `ALLOWED_ORIGINS`).
No proxy layer is needed — call the API directly from the browser.

---

## 3. Competition Context (Affects Submission)

The competition has **two separate submission forms** — one for Task A and one for Task B.
Each form asks for a live URL, code repo, and solution paper. Both tasks share one codebase
and one deployed backend. The frontend must expose **two distinct flows** so they can be
demonstrated and linked independently:

| Submission | Live URL | What the judge sees |
|---|---|---|
| Task A | `https://yourapp.vercel.app/task-a` | Review simulation flow |
| Task B | `https://yourapp.vercel.app/task-b` | Recommendation / agent flow |

The landing page (`/`) is a mode selector that links to both.

---

## 4. Success Criteria

- Task A and Task B can each be demonstrated end-to-end in under 3 minutes by a judge
  who has never seen the app.
- The psychological profile and reasoning trace are legible without explanation.
- Cold-start chat works live — profile updates in real time as each answer is submitted.
- The Nigerian cultural signal is surfaced visibly when present (not hidden in raw JSON).
- No blank screens or unhandled errors during a standard demo flow.
- All key screens load in under 2 seconds on a broadband connection.

---

## 5. Target Users

- Hackathon judges — 3–5 minutes of engagement, want to see the AI reasoning.
- Demo operators (team members) — need quick reset and reproducible demo paths.

---

## 6. Routes

| Route | Purpose |
|---|---|
| `/` | Landing — mode selector + brief pitch |
| `/task-a` | Review simulation flow |
| `/task-b` | Recommendation / agentic flow |
| `/about` | Method overview and architecture |

---

## 7. Global UI Components

- **App shell** — top nav with mode switcher (Task A / Task B), competition branding.
- **Profile panel** — persistent once a profile is built; collapsed on mobile.
- **Trace panel** — displays the reasoning trace from the last API call.
- **Toast / error bar** — non-blocking error display for API failures.
- **Loading states** — skeleton screens, not spinners (better perceived performance).

---

## 8. UX Principles

- Show reasoning **before** the final output — emphasise the agentic, explainable workflow.
- Make the profile feel like a **living character** (animated build, labelled signal bars).
- Nigerian context cues (pidgin phrases, cultural index) should be **visible but not caricatured**.
- Keep outputs grounded in evidence: every rating, review, and recommendation links back to
  a profile signal or preference axis.

---

## 9. Task A Flow — Review Simulation

### 9.1 Steps

1. User enters their review history (paste raw reviews, or use a pre-seeded demo user).
2. Hit **Build Profile** → calls `POST /profile/build`. Profile panel populates.
3. User enters a target item (name + optional description).
4. Hit **Simulate** → calls `POST /task-a/simulate`. Reasoning trace appears first.
5. Predicted rating badge animates in (1–5 stars).
6. Generated review appears with a type-out animation.
7. Optional: toggle **LLM mode** (`use_llm=true`) to generate a richer review.
8. Optional: show real review side-by-side for comparison.

### 9.2 Required UI Elements

- **History input** — textarea or structured form (item_id, rating, review_text, timestamp).
  Accept `review_text` OR `text` — backend handles both.
- **Demo user selector** — dropdown with 3–5 pre-seeded users (vary history size,
  cultural signal strength, rating bias).
- **Profile panel** (see §11).
- **Target item form** — at minimum: name field. Optional: description, category.
- **LLM toggle** — checkbox or pill toggle for `use_llm`. Show a latency warning (~3s).
- **Reasoning trace panel** (see §12).
- **Output panel** — rating badge (stars + numeric), generated review text, copy button.
- **Side-by-side drawer** — optional real review (if you have it for a demo user).

### 9.3 API Call

```
POST /task-a/simulate
Content-Type: application/json

{
  "user_id": "demo_u1",
  "records": [
    {
      "item_id": "biz_01",
      "rating": 4.0,
      "review_text": "The jollof rice was excellent. Service was quick.",
      "timestamp": "2023-06-15",
      "source": "yelp"
    }
  ],
  "target_item": {
    "name": "Kilimanjaro Restaurant",
    "description": "Nigerian cuisine in Lagos"
  },
  "use_llm": false
}
```

**Note:** `source` defaults to `"yelp"` if omitted. `timestamp` can be omitted.

### 9.4 Response

```json
{
  "user_id": "demo_u1",
  "target_item": { "name": "Kilimanjaro Restaurant", "description": "..." },
  "predicted_rating": 3.9,
  "reasoning": "User mean rating is 4.20 (σ=0.50, n=12); calibrated downward to 3.90 against population mean 3.50. Top preference axes: food (w=0.62). Review style: ~80 words, vocab richness 0.62. Nigerian English detected (index=0.04, pidgin hits=2); cultural register applied.",
  "review_text": "Really enjoyed this. The food was the highlight. Kilimanjaro Restaurant delivered. Abeg, try am yourself and see."
}
```

---

## 10. Task B Flow — Recommendation + Agent

### 10.1 Steps

1. User enters review history OR starts cold-start chat.
2. Profile is built (history path: `POST /profile/build`; cold-start: `GET /cold-start/questions` → `POST /cold-start/answer`).
3. User types a natural-language query (e.g. *"spicy grilled food, cheap, Lagos vibe"*).
4. Hit **Find Recommendations** → calls `POST /task-b/recommend`. Preference axes appear.
5. Recommendation cards appear ranked, each with an explanation accordion.
6. User can refine: add a constraint, request more results. Each refinement call passes the `session_id` back to maintain state (no previously-seen items are re-shown).
7. Optional: **Agent Mode** — toggle calls `POST /task-b/agent` instead and shows the 4-step agent execution trace.

### 10.2 Cold-Start Chat Sub-Flow

This is the entry path for new users with no history.

1. Call `GET /cold-start/questions` → display 4 questions one at a time in a chat-style UI.
2. User picks an option for each question.
3. Call `POST /cold-start/answer` with all 4 answers → profile is returned immediately.
4. Profile panel populates and the recommendation flow continues.

### 10.3 Required UI Elements

- **History input** OR **cold-start chat** (tab switcher or route-level choice).
- **Cold-start chat panel** — progress indicator (question 1 of 4), option chips (not free text).
- **Query input** — freeform text. Placeholder: *"e.g. spicy grilled food, budget-friendly"*.
- **Profile panel** (see §11).
- **Preference axes list** — name, rationale, weight bar for each axis.
- **Recommendation card grid** — rank badge, item name, category, score bar, explanation accordion.
- **Constraints input** — optional tag input that adds to session constraints on next call.
- **Agent Mode toggle** — pill toggle. When active, show 4-step agent trace before cards.
- **Session continue button** — "Show more recommendations" that re-calls with the same `session_id`.

### 10.4 API Call — Recommend

```
POST /task-b/recommend
Content-Type: application/json

{
  "user_id": "demo_u1",
  "records": [ ... ],
  "query_text": "spicy grilled food Lagos",
  "top_k": 10,
  "session_id": "sess-abc123"
}
```

`session_id` is optional on the first call (backend creates a new session). Echo it back
on every subsequent call in the same conversation to exclude already-shown items.

### 10.5 Response — Recommend

```json
{
  "user_id": "demo_u1",
  "session_id": "sess-abc123",
  "axes": [
    { "name": "food",        "rationale": "Mentions food in 4 reviews", "weight": 0.80 },
    { "name": "rating_bias", "rationale": "Average rating 4.2 — generous rater",  "weight": 0.60 },
    { "name": "cultural_register", "rationale": "Nigerian English detected", "weight": 0.40 }
  ],
  "recommendations": [
    {
      "item_id": "biz_789",
      "score": 1.62,
      "explanation": "Similarity score 0.82; Matched axes: food",
      "metadata": {
        "name": "Chicken Republic",
        "categories": "fast food, Nigerian",
        "stars": 4.1
      }
    }
  ]
}
```

**Key notes:**
- Always store `session_id` from the response and send it back on the next call.
- `metadata` fields vary — always use optional chaining (`metadata?.name`).
- `score` is a composite float; display as a normalised bar, not a raw number.

### 10.6 API Call — Agent

```
POST /task-b/agent
Content-Type: application/json

{
  "user_id": "demo_u1",
  "records": [ ... ],
  "query_vectors": [[0.12, -0.34, ...]],
  "candidates": [
    { "item_id": "c1", "vector": [...], "metadata": { "name": "Buka Stop" } }
  ],
  "top_k": 5,
  "use_llm": false
}
```

**Note:** `/task-b/agent` does not accept `query_text` — it requires pre-computed
`query_vectors` and a `candidates` array. In the UI, agent mode is best demonstrated
with pre-built demo payloads rather than live user input, unless you add a client-side
embedding step.

### 10.7 Response — Agent

```json
{
  "user_id": "demo_u1",
  "steps": [
    { "thought": "Calling build_profile",        "tool": "build_profile",        "result": { ... } },
    { "thought": "Calling extract_axes",         "tool": "extract_axes",         "result": { ... } },
    { "thought": "Calling retrieve_candidates",  "tool": "retrieve_candidates",  "result": { ... } },
    { "thought": "Calling score_candidates",     "tool": "score_candidates",     "result": { ... } }
  ],
  "final": {
    "tool_results": [ {...}, {...}, {...}, {...} ]
  }
}
```

Render `steps` as an animated timeline — each step expands to show the tool name and
result summary. The final scored items are inside `final.tool_results[3].scored`.

---

## 11. Profile Panel

Displayed as a persistent side/bottom panel once a profile is available from any source
(history build, cold-start, profile update).

### 11.1 Data source

All profile endpoints return the same `PsychologicalProfile` schema:

```json
{
  "user_id": "demo_u1",
  "rating_stats": {
    "count": 12,
    "mean": 4.20,
    "std_dev": 0.50,
    "min_rating": 3.0,
    "max_rating": 5.0
  },
  "stylometry": {
    "avg_review_length": 210.0,
    "avg_word_count": 42.0,
    "vocab_richness": 0.62,
    "avg_sentence_length": 8.4
  },
  "value_keywords": {
    "food": 4,
    "service": 2,
    "price": 1,
    "atmosphere": 0
  },
  "trajectory": {
    "early_mean_rating": 3.80,
    "recent_mean_rating": 4.20,
    "delta_rating": 0.40,
    "early_avg_review_length": 180.0,
    "recent_avg_review_length": 240.0,
    "delta_review_length": 60.0
  },
  "cultural_signals": {
    "nigerian_english_index": 0.04,
    "code_switching_detected": true,
    "pidgin_term_hits": 3
  }
}
```

`rating_stats.count == 0` means this is a cold-start bootstrapped profile — show a
**"Cold-start profile"** badge. All downstream endpoints handle this correctly.

### 11.2 Visualisation

| Signal | Suggested display |
|---|---|
| `rating_stats.mean` | Star rating badge + "generous / neutral / harsh rater" label |
| `rating_stats.count` | "Based on N reviews" sub-label |
| `value_keywords` | Horizontal bar chart with 4 categories (food / service / price / atmosphere) |
| `stylometry.vocab_richness` | Labelled gauge (0–1) |
| `stylometry.avg_word_count` | "Writes ~N words per review" |
| `trajectory.delta_rating` | Trend arrow: ↑ improving, ↓ declining, → stable (|delta| < 0.2) |
| `trajectory.delta_review_length` | "Reviews getting longer / shorter" |
| `cultural_signals.code_switching_detected` | 🇳🇬 badge or "Nigerian English detected" chip (show when `true`) |
| `cultural_signals.nigerian_english_index` | Density bar (0–1 scale, show only when > 0) |

---

## 12. Reasoning Trace Panel

The reasoning trace is a plain string from the API:

```
"User mean rating is 4.20 (σ=0.50, n=12); calibrated downward to 3.90 against
population mean 3.50. Top preference axes: food (w=0.62). Review style: ~80 words,
vocab richness 0.62. Nigerian English detected (index=0.04, pidgin hits=2); cultural
register applied."
```

Parse and render as structured bullets. The string uses semicolons to separate clauses.
Split on `"; "` and render each clause as a list item with a coloured left border.

For the agent flow, render `steps[]` as a sequential timeline instead:

```
Step 1 — build_profile     [✓ completed]   ← click to expand result
Step 2 — extract_axes      [✓ completed]
Step 3 — retrieve_candidates [✓ completed]
Step 4 — score_candidates  [✓ completed]
```

---

## 13. Cold-Start API Contracts

### GET /cold-start/questions

```json
{
  "questions": [
    {
      "id": "rating_tendency",
      "question": "When you enjoy something, do you give it full marks or reserve top ratings for the absolute best?",
      "options": ["top_marks", "reserve_top"]
    },
    {
      "id": "value_priority",
      "question": "What do you care most about when reviewing a place?",
      "options": ["food_quality", "service", "price_value", "atmosphere"]
    },
    {
      "id": "review_style",
      "question": "How do you typically write reviews?",
      "options": ["brief_and_direct", "detailed_and_thorough"]
    },
    {
      "id": "cultural_register",
      "question": "Do you use Nigerian English or Pidgin in your reviews?",
      "options": ["yes_often", "sometimes", "rarely"]
    }
  ]
}
```

Display each question one at a time with option chips (not dropdowns). Show a progress
bar (1 of 4, 2 of 4, …).

### POST /cold-start/answer

```json
{
  "user_id": "new_user_temp_id",
  "answers": [
    { "question_id": "rating_tendency",   "answer": "top_marks" },
    { "question_id": "value_priority",    "answer": "food_quality" },
    { "question_id": "review_style",      "answer": "detailed_and_thorough" },
    { "question_id": "cultural_register", "answer": "sometimes" }
  ]
}
```

Response is a full `PsychologicalProfile` (same schema as `/profile/build`).
The profile panel should animate in after this call.

**Error cases:**
- 400: `user_id` is empty.
- 400: `answers` is empty.
- Unknown `question_id` or `answer` values are silently ignored — safe to send partial answers.

---

## 14. Profile Build & Update

### POST /profile/build

Builds a profile from a user's full review history.

**Request:**
```json
{
  "user_id": "demo_u1",
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

**Field notes:**
- `review_text` is the canonical field. The backend also accepts `text` as a fallback.
  Use `review_text` in all frontend-generated payloads to avoid ambiguity.
- `timestamp` is optional but improves trajectory calculation. ISO date strings (`YYYY-MM-DD`) work.
- `source` is optional (defaults to `"yelp"`).
- `item_id` must be non-empty — skip any records without one.

**Response:** `PsychologicalProfile` (see §11.1).

**Error cases:**
- 400: `user_id` is empty.

### POST /profile/update

Appends new records to an existing history and returns a freshly computed profile.

**Request:**
```json
{
  "user_id": "demo_u1",
  "existing_records": [ { "item_id": "biz_01", "rating": 4.0, ... } ],
  "new_records":      [ { "item_id": "biz_02", "rating": 3.5, ... } ]
}
```

**Response:**
```json
{
  "updated": true,
  "profile": { ... }
}
```

**Error cases:**
- 400: `user_id` is empty.
- 400: `new_records` is empty.

---

## 15. Error Handling

| HTTP status | Meaning | UI action |
|---|---|---|
| 400 | Bad request (missing field, empty user_id) | Show inline form error |
| 422 | Pydantic validation error | Show generic "Invalid input" toast |
| 500 | Backend crash | Show "Something went wrong. Try again." toast |
| Network error | Backend unreachable | Show "API unavailable" banner |

Never show raw API error bodies to judges. Map them to user-facing messages.

---

## 16. Request Headers

Include on every API call:

```
Content-Type: application/json
X-Trace-Id: <uuid>   // optional but recommended — lets you correlate frontend actions with backend logs
```

The backend echoes `X-Trace-Id` in the response. Log it to the browser console for
debugging during the demo.

---

## 17. Demo Users (Seeded Data)

Prepare at least 3 pre-seeded demo users with hardcoded review records in the frontend
so judges can demo instantly without typing:

| Demo user | History size | Cultural signal | Rating bias | Narrative |
|---|---|---|---|---|
| `demo_generous` | 15 reviews | Nigerian English present | Mean 4.5 — generous rater | Loves food, writes detailed reviews |
| `demo_critic`   | 10 reviews | None | Mean 2.8 — harsh rater | Values service + price, short reviews |
| `demo_newuser`  | 0 reviews  | — | — | Cold-start path, no history |

Store these as static JSON arrays in the frontend (e.g. `lib/demo-users.ts`). On
"Load demo user" selection, populate the `records` array and call `/profile/build`.

---

## 18. Information Architecture

```
/
├── / (Landing — mode selector)
├── /task-a
│   ├── Left: history input + demo selector + target item form
│   ├── Center: profile panel
│   └── Right: reasoning trace + output (rating + review)
├── /task-b
│   ├── Left: history input OR cold-start chat + query input
│   ├── Center: profile panel + preference axes
│   └── Right: reasoning trace + recommendation cards
└── /about
    └── Architecture diagram + method summary
```

---

## 19. Visual Design Direction

- **Aesthetic:** Research-lab / AI tool. High contrast. Dark mode preferred.
- **Typography:** Avoid system defaults. Inter or Space Grotesk for UI; a mono font for
  reasoning trace and code-like outputs.
- **Colour:** Warm neutrals + a single accent (amber or indigo). Nigerian flag green
  accent on cultural signal badges.
- **Motion:** Animate profile panel build (bars grow in), reasoning trace (clauses appear
  one by one), recommendation cards (stagger in). All animations must respect
  `prefers-reduced-motion`.
- **Rating badge:** Prominent, emoji-style stars. Show both stars and numeric value.

---

## 20. Accessibility

- All interactive elements keyboard-navigable (Tab + Enter/Space).
- Contrast ratio ≥ 4.5:1 for body text.
- ARIA labels on icon-only buttons.
- `prefers-reduced-motion` disables all transitions/animations.

---

## 21. Performance

- Code-split by route (Next.js default — do not bundle Task A into Task B chunk).
- Virtualise recommendation card lists if > 20 items (use `react-virtual` or equivalent).
- Lazy-load charts (radar chart, bar chart) — import dynamically.
- Skeleton screens on all API-dependent panels (not empty divs).

---

## 22. Tech Stack

| Concern | Choice |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS |
| Charts | Recharts or Nivo (lightweight, tree-shakeable) |
| State | React useState / useReducer — no global store needed for MVP |
| API calls | Native `fetch` — no Axios required |
| Deployment | Vercel (auto from GitHub push to `main`) |

---

## 23. Environment Variables

```bash
# .env.local (Vercel project settings)
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

No other env vars are required on the frontend. The backend handles all secrets.

---

## 24. Open Questions for the Team

1. What is the final DigitalOcean domain? (Needed for `NEXT_PUBLIC_API_URL` and CORS config.)
2. Which 3–5 demo users and target items should be pre-seeded? Share the records JSON.
3. Should the frontend handle the `/task-b/agent` endpoint live (requires pre-computed
   vectors) or only via pre-built demo payloads?
4. Should `/about` include a live architecture diagram or a static image?

---

## 25. Architecture Diagram

```
Browser (Vercel)
      │
      │  HTTPS REST
      ▼
DigitalOcean Droplet
  ┌── Nginx (SSL termination, port 443) ──┐
  │                                       │
  ▼                                       │
FastAPI (port 8000, internal)             │
  ├── GET  /health                        │
  ├── GET  /cold-start/questions          │
  ├── POST /cold-start/answer  ──► ColdStartEngine → PsychologicalProfile
  ├── POST /profile/build      ──► ProfileService (TTL+LRU cache)
  ├── POST /profile/update     ──► ProfileService (append + rebuild)
  ├── POST /task-a/simulate    ──► TaskAService (rating calibration + review gen)
  ├── POST /task-b/recommend   ──► TaskBService + SessionStore (multi-turn)
  └── POST /task-b/agent       ──► TaskBAgentService (4-step agent loop)
              │
              ▼
    50k Yelp vector store (in-memory, 408MB JSONL)
    sentence-transformers all-MiniLM-L6-v2 (384-dim, baked into Docker image)
```
