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
