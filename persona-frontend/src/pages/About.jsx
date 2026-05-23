function ArchBox({ title, sub, accent }) {
  return (
    <div style={{
      background: '#13131A', border: `1px solid ${accent ?? '#1E1E2E'}`,
      borderRadius: 10, padding: '12px 18px', textAlign: 'center', minWidth: 100,
    }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#F8FAFC' }}>{title}</div>
      {sub && <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function Arrow() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', color: '#1E1E2E', fontSize: 20, padding: '0 4px' }}>→</div>
  );
}

function MethodCard({ title, body }) {
  return (
    <div style={{
      flex: 1, minWidth: 260,
      background: '#13131A', border: '1px solid #1E1E2E',
      borderRadius: 12, padding: 24,
    }}>
      <div style={{ fontSize: 16, fontWeight: 700, color: '#F8FAFC', marginBottom: 10 }}>{title}</div>
      <div style={{ fontSize: 14, color: '#64748B', lineHeight: 1.7 }}>{body}</div>
    </div>
  );
}

const STACK = [
  { icon: '⚛️', label: 'React' },
  { icon: '🟨', label: 'JavaScript' },
  { icon: '🎨', label: 'Tailwind CSS' },
  { icon: '🐍', label: 'FastAPI' },
  { icon: '🤗', label: 'sentence-transformers' },
  { icon: '📊', label: 'Recharts' },
];

const TASK_A_CRITERIA = [
  { name: 'Review Text Quality', method: 'ROUGE / BERTScore' },
  { name: 'Rating Accuracy', method: 'RMSE' },
  { name: 'Behavioural Fidelity', method: 'Human evaluation' },
  { name: 'Solution Paper', method: 'Written submission' },
  { name: 'Code Reproducibility', method: 'Reproducibility audit' },
];

const TASK_B_CRITERIA = [
  { name: 'Ranking Quality', method: 'NDCG@10 / Hit Rate', pts: 30 },
  { name: 'Cold-Start & Cross-Domain', method: 'Held-out evaluation', pts: 25 },
  { name: 'Contextual Relevance', method: 'Human eval', pts: 20 },
  { name: 'Solution Paper', method: 'Written submission', pts: 15 },
  { name: 'Code Reproducibility', method: 'Reproducibility audit', pts: 10 },
];

export default function About() {
  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '48px 24px' }}>
      <h1 style={{ fontSize: 'clamp(28px, 4vw, 40px)', fontWeight: 700, color: '#F8FAFC', textAlign: 'center', marginBottom: 48, letterSpacing: '-0.02em' }}>
        How Persona Works
      </h1>

      {/* Architecture */}
      <div style={{ marginBottom: 48 }}>
        <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 20 }}>
          Architecture
        </div>
        <div style={{
          background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 24,
          display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 4, justifyContent: 'center',
        }}>
          <ArchBox title="Browser" sub="React + Vite" accent="#6366F1" />
          <Arrow />
          <ArchBox title="Nginx" sub="Reverse Proxy" />
          <Arrow />
          <ArchBox title="FastAPI" sub="Port 8000" accent="#F59E0B" />
          <Arrow />
          <ArchBox title="Vector Store" sub="50k Yelp businesses" accent="#22C55E" />
        </div>
      </div>

      {/* Method cards */}
      <div style={{ display: 'flex', gap: 20, marginBottom: 48, flexWrap: 'wrap' }}>
        <MethodCard
          title="Review Simulation"
          body="Persona builds a psychological profile from a user's review history — extracting rating statistics, writing style, value keywords, and cultural signals. It then calibrates a predicted rating against the population mean and generates a culturally-aware review that mirrors the user's authentic voice."
        />
        <MethodCard
          title="Smart Recommendations"
          body="For users with history, Persona extracts preference axes and runs vector similarity search against 50k Yelp businesses. For new users, a cold-start chat collects preferences. A 4-step agent loop — profile → embed → search → rank — refines results using LLM reasoning."
        />
      </div>

      {/* Feature 12: Scoring Rubric */}
      <div style={{ marginBottom: 48 }}>
        <div style={{ fontSize: 24, fontWeight: 700, color: '#F8FAFC', marginBottom: 24 }}>Evaluation Criteria</div>

        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', marginBottom: 24 }}>
          {/* Task A card */}
          <div style={{
            flex: 1, minWidth: 280,
            background: '#13131A', border: '1px solid #1E1E2E',
            borderTop: '3px solid #6366F1', borderRadius: 12, padding: 24,
          }}>
            <div style={{ fontSize: 11, color: '#6366F1', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600, marginBottom: 16 }}>
              Task A · User Modeling
            </div>
            {TASK_A_CRITERIA.map(({ name, method }) => (
              <div key={name} style={{ marginBottom: 14, paddingBottom: 14, borderBottom: '1px solid #1E1E2E' }}>
                <div style={{ fontSize: 14, color: '#F8FAFC' }}>{name}</div>
                <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{method}</div>
              </div>
            ))}
          </div>

          {/* Task B card */}
          <div style={{
            flex: 1, minWidth: 280,
            background: '#13131A', border: '1px solid #1E1E2E',
            borderTop: '3px solid #F59E0B', borderRadius: 12, padding: 24,
          }}>
            <div style={{ fontSize: 11, color: '#F59E0B', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: 600, marginBottom: 16 }}>
              Task B · Recommendation
            </div>
            {TASK_B_CRITERIA.map(({ name, method, pts }) => (
              <div key={name} style={{ marginBottom: 14, paddingBottom: 14, borderBottom: '1px solid #1E1E2E', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
                <div>
                  <div style={{ fontSize: 14, color: '#F8FAFC' }}>{name}</div>
                  <div style={{ fontSize: 11, color: '#64748B', marginTop: 2 }}>{method}</div>
                </div>
                <span style={{ color: '#F59E0B', fontWeight: 700, fontSize: 13, fontFamily: 'JetBrains Mono, monospace', flexShrink: 0 }}>{pts}pts</span>
              </div>
            ))}
            <div style={{ textAlign: 'right', fontSize: 13, color: '#F8FAFC', fontWeight: 600, marginTop: 4 }}>
              100 pts total
            </div>
          </div>
        </div>

        {/* Pull-quote */}
        <div style={{ textAlign: 'center', padding: '0 24px' }}>
          <p style={{ fontSize: 14, color: '#64748B', fontStyle: 'italic', lineHeight: 1.7, margin: 0 }}>
            "A model score reflects what your machine did. A solution paper reveals what you understood. Both matter."
          </p>
          <p style={{ fontSize: 12, color: '#64748B', marginTop: 6 }}>— DSN x BCT Judging Panel</p>
        </div>
      </div>

      {/* Tech stack */}
      <div>
        <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 16 }}>
          Tech Stack
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {STACK.map(({ icon, label }) => (
            <span key={label} style={{
              background: '#13131A', border: '1px solid #1E1E2E',
              borderRadius: 999, padding: '6px 14px',
              fontSize: 12, color: '#64748B',
              display: 'flex', alignItems: 'center', gap: 6,
            }}>
              {icon} {label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
