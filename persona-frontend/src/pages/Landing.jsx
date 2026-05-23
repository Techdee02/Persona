import { useNavigate } from 'react-router-dom';
import { Brain, Globe, Zap } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function FlowNode({ label, color = '#F8FAFC' }) {
  return (
    <div style={{
      background: '#13131A', border: '1px solid #1E1E2E',
      borderRadius: 999, padding: '6px 16px',
      fontSize: 12, color, fontWeight: 600,
    }}>
      {label}
    </div>
  );
}

function FlowArrow({ delay }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
      <div style={{
        width: 40, height: 1,
        background: 'linear-gradient(90deg, #1E1E2E, #6366F1)',
        opacity: 0.6,
        animation: reduced ? 'none' : `pulse-opacity 2s ease-in-out ${delay}ms infinite`,
      }} />
      <div style={{ color: '#6366F1', fontSize: 14, opacity: 0.6 }}>›</div>
    </div>
  );
}

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: 'calc(100vh - 56px)',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '48px 24px',
    }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', maxWidth: 680 }}>
        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: 700,
          letterSpacing: '-0.03em', lineHeight: 1.1, margin: '0 0 8px',
          color: '#F8FAFC',
        }}>
          Understand who your users are.
        </h1>
        <h1 style={{
          fontSize: 'clamp(32px, 5vw, 52px)', fontWeight: 700,
          letterSpacing: '-0.03em', lineHeight: 1.1, margin: '0 0 24px',
          color: '#F59E0B',
        }}>
          Before they tell you.
        </h1>
        <p style={{ fontSize: 17, color: '#64748B', lineHeight: 1.7, maxWidth: 560, margin: '0 auto' }}>
          Persona builds psychological profiles from review history — predicting ratings, generating authentic reviews, and recommending places that actually fit.
        </p>
      </div>

      {/* Cards */}
      <div style={{ display: 'flex', gap: 24, marginTop: 48, width: '100%', maxWidth: 760, flexWrap: 'wrap' }}>
        {/* Task A */}
        <div style={{
          flex: 1, minWidth: 280,
          background: '#13131A', border: '1px solid #1E1E2E',
          borderRadius: 16, padding: 32,
          display: 'flex', flexDirection: 'column', gap: 16,
        }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>Review Simulation</div>
            <div style={{ fontSize: 14, color: '#64748B', lineHeight: 1.6 }}>
              Predict how a user would rate and review any place based on their psychological profile.
            </div>
          </div>
          <button
            onClick={() => navigate('/task-a')}
            style={{
              width: '100%', background: '#F59E0B', color: '#0A0A0F',
              border: 'none', borderRadius: 8, padding: '11px 0',
              fontWeight: 700, fontSize: 14, cursor: 'pointer',
              marginTop: 'auto',
              transition: reduced ? 'none' : 'opacity 0.2s',
            }}
            onMouseEnter={e => { if (!reduced) e.target.style.opacity = '0.85'; }}
            onMouseLeave={e => { e.target.style.opacity = '1'; }}
          >
            Try Task A →
          </button>
        </div>

        {/* Task B */}
        <div style={{
          flex: 1, minWidth: 280,
          background: '#13131A', border: '1px solid #1E1E2E',
          borderRadius: 16, padding: 32,
          display: 'flex', flexDirection: 'column', gap: 16,
        }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, color: '#F8FAFC', marginBottom: 8 }}>Smart Recommendations</div>
            <div style={{ fontSize: 14, color: '#64748B', lineHeight: 1.6 }}>
              Find places that truly match a user's taste, writing style, and cultural context.
            </div>
          </div>
          <button
            onClick={() => navigate('/task-b')}
            style={{
              width: '100%', background: '#6366F1', color: '#fff',
              border: 'none', borderRadius: 8, padding: '11px 0',
              fontWeight: 700, fontSize: 14, cursor: 'pointer',
              marginTop: 'auto',
              transition: reduced ? 'none' : 'opacity 0.2s',
            }}
            onMouseEnter={e => { if (!reduced) e.target.style.opacity = '0.85'; }}
            onMouseLeave={e => { e.target.style.opacity = '1'; }}
          >
            Try Task B →
          </button>
        </div>
      </div>

      {/* Feature 10B: Why This Matters strip */}
      <div style={{ width: '100%', maxWidth: 800, marginTop: 32, display: 'flex', gap: 24, flexWrap: 'wrap', justifyContent: 'center' }}>
        {[
          { icon: <Brain size={22} color="#6366F1" />, title: 'Behaviour', body: 'We model how users rate, write, and decide', accent: '#6366F1' },
          { icon: <Globe size={22} color="#F59E0B" />, title: 'Context', body: 'We detect cultural register and linguistic identity', accent: '#F59E0B' },
          { icon: <Zap size={22} color="#6366F1" />, title: 'Prediction', body: 'We simulate what they\'d say before they say it', accent: '#6366F1' },
        ].map(({ icon, title, body, accent }) => (
          <div key={title} style={{
            flex: 1, minWidth: 200, textAlign: 'center',
            background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: '20px 16px',
          }}>
            <div style={{
              width: 44, height: 44, borderRadius: 10,
              background: `${accent}18`, border: `1px solid ${accent}30`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 12px',
            }}>
              {icon}
            </div>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#F8FAFC', marginBottom: 6 }}>{title}</div>
            <div style={{ fontSize: 13, color: '#64748B', lineHeight: 1.6 }}>"{body}"</div>
          </div>
        ))}
      </div>

      {/* Flow diagram */}
      <div style={{ marginTop: 48, display: 'flex', alignItems: 'center', gap: 0 }}>
        <FlowNode label="Your Reviews" color="#64748B" />
        <FlowArrow delay={0} />
        <FlowNode label="Persona Engine" color="#F59E0B" />
        <FlowArrow delay={300} />
        <FlowNode label="Predictions" color="#6366F1" />
      </div>
    </div>
  );
}
