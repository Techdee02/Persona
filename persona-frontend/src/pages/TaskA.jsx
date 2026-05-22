import { useState, useEffect, useRef } from 'react';
import { Copy, Check, Star } from 'lucide-react';
import ProfilePanel from '../components/profile/ProfilePanel';
import TracePanel from '../components/trace/TracePanel';
import { buildProfile, simulateTaskA } from '../lib/api';
import { DEMO_USERS } from '../lib/demo-users';
import { useToast } from '../components/layout/Toast';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function SectionHeader({ num, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
      <div style={{ width: 4, height: 20, background: '#F59E0B', borderRadius: 2 }} />
      <span style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.12em', fontWeight: 600 }}>
        {num} — {label}
      </span>
    </div>
  );
}

function Toggle({ on, onToggle, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <span style={{ fontSize: 13, color: '#F8FAFC' }}>{label}</span>
      <button
        role="switch"
        aria-checked={on}
        aria-label={label}
        onClick={onToggle}
        style={{
          width: 40, height: 22, borderRadius: 11, border: 'none', cursor: 'pointer',
          background: on ? '#6366F1' : '#1E1E2E',
          position: 'relative', transition: reduced ? 'none' : 'background 0.2s',
        }}
      >
        <div style={{
          position: 'absolute', top: 3, left: on ? 21 : 3,
          width: 16, height: 16, borderRadius: '50%', background: '#F8FAFC',
          transition: reduced ? 'none' : 'left 0.2s',
        }} />
      </button>
    </div>
  );
}

function TypewriterText({ text }) {
  const [displayed, setDisplayed] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!text) return;
    if (reduced) { setDisplayed(text); return; }
    setDisplayed('');
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) clearInterval(iv);
    }, 30);
    return () => clearInterval(iv);
  }, [text]);

  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={copy}
        aria-label="Copy review text"
        style={{
          position: 'absolute', top: 8, right: 8,
          background: 'none', border: 'none', cursor: 'pointer',
          color: copied ? '#22C55E' : '#64748B',
        }}
      >
        {copied ? <Check size={14} /> : <Copy size={14} />}
      </button>
      <div style={{
        background: '#0A0A0F', border: '1px solid #1E1E2E', borderRadius: 8,
        padding: '12px 36px 12px 12px',
        fontFamily: 'JetBrains Mono, monospace', fontSize: 13, color: '#F8FAFC',
        lineHeight: 1.6, minHeight: 80,
      }}>
        {displayed}
        {displayed.length < text.length && <span style={{ opacity: 0.5 }}>|</span>}
      </div>
    </div>
  );
}

function OutputPanel({ output, loading }) {
  if (loading) {
    return (
      <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
        <div className="skeleton" style={{ width: 80, height: 80, borderRadius: '50%', margin: '0 auto 16px' }} />
        {[1, 2, 3, 4].map(i => <div key={i} className="skeleton" style={{ height: 12, marginBottom: 8 }} />)}
      </div>
    );
  }

  if (!output) {
    return (
      <div style={{
        background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        minHeight: 160, gap: 10,
      }}>
        <Star size={28} color="#1E1E2E" />
        <span style={{ color: '#64748B', fontSize: 13 }}>Simulation output will appear here.</span>
      </div>
    );
  }

  const rating = output.predicted_rating ?? 0;

  return (
    <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
      {/* Rating badge */}
      <div style={{ textAlign: 'center', marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 4, marginBottom: 8 }}>
          {[1, 2, 3, 4, 5].map(i => (
            <span
              key={i}
              style={{
                fontSize: 24, color: i <= Math.round(rating) ? '#F59E0B' : '#1E1E2E',
                opacity: 0, animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
                animationDelay: reduced ? '0ms' : `${(i - 1) * 100}ms`,
              }}
            >★</span>
          ))}
        </div>
        <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 28, fontWeight: 700, color: '#F8FAFC' }}>
          {rating.toFixed(1)} / 5.0
        </div>
        <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 4 }}>
          Predicted Rating
        </div>
      </div>

      <div style={{ height: 1, background: '#1E1E2E', margin: '16px 0' }} />

      <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>
        Generated Review
      </div>
      <TypewriterText text={output.review_text ?? ''} />
    </div>
  );
}

export default function TaskA() {
  const { showToast } = useToast();
  const [records, setRecords] = useState([]);
  const [selectedDemo, setSelectedDemo] = useState('');
  const [demoChip, setDemoChip] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [targetItem, setTargetItem] = useState({ name: '', description: '' });
  const [useLLM, setUseLLM] = useState(false);
  const [output, setOutput] = useState(null);
  const [outputLoading, setOutputLoading] = useState(false);
  const [traceLoading, setTraceLoading] = useState(false);
  const chipTimer = useRef(null);

  const handleDemoSelect = (e) => {
    const key = e.target.value;
    setSelectedDemo(key);
    if (!key) { setRecords([]); return; }
    const r = DEMO_USERS[key]?.records ?? [];
    setRecords(r);
    setDemoChip(true);
    clearTimeout(chipTimer.current);
    chipTimer.current = setTimeout(() => setDemoChip(false), 2000);
  };

  useEffect(() => () => clearTimeout(chipTimer.current), []);

  const handleBuildProfile = async () => {
    setProfileLoading(true);
    try {
      const p = await buildProfile(selectedDemo || 'custom_user', records);
      setProfile(p);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setProfileLoading(false);
    }
  };

  const handleSimulate = async () => {
    setOutputLoading(true);
    setTraceLoading(true);
    try {
      const result = await simulateTaskA({
        user_id: selectedDemo || 'custom_user',
        records,
        target_item: targetItem,
        use_llm: useLLM,
      });
      setOutput(result);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setOutputLoading(false);
      setTraceLoading(false);
    }
  };

  const canSimulate = profile !== null && targetItem.name.trim() !== '';

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)',
      gap: 16, padding: 24, minHeight: 'calc(100vh - 56px)',
    }}>
      {/* Left col */}
      <div style={{ gridColumn: 'span 4' }}>
        <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
          <SectionHeader num="01" label="Build Profile" />

          {/* Demo selector */}
          <div style={{ marginBottom: 12 }}>
            <label htmlFor="demo-select" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Demo User</label>
            <select id="demo-select" value={selectedDemo} onChange={handleDemoSelect}>
              <option value="">Select a demo user</option>
              {Object.entries(DEMO_USERS).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
            {demoChip && (
              <div style={{
                marginTop: 6, display: 'inline-flex', alignItems: 'center', gap: 4,
                background: 'rgba(34,197,94,0.1)', border: '1px solid #22C55E',
                borderRadius: 999, padding: '2px 10px', fontSize: 11, color: '#22C55E',
              }}>
                Demo data loaded ✓
              </div>
            )}
          </div>

          {/* Textarea */}
          <div style={{ marginBottom: 12 }}>
            <label htmlFor="records-input" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Review Records (JSON)</label>
            <textarea
              id="records-input"
              rows={7}
              placeholder='Paste JSON review records here, or select a demo user above.'
              value={records.length ? JSON.stringify(records, null, 2) : ''}
              onChange={e => {
                try { setRecords(JSON.parse(e.target.value)); } catch { /* ignore */ }
              }}
              style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, resize: 'vertical', minHeight: 140 }}
            />
          </div>

          <button
            onClick={handleBuildProfile}
            disabled={profileLoading}
            style={{
              width: '100%', background: '#6366F1', color: '#fff', border: 'none',
              borderRadius: 8, padding: '10px 0', fontWeight: 600, fontSize: 14,
              cursor: profileLoading ? 'not-allowed' : 'pointer', marginBottom: 20,
              position: 'relative', overflow: 'hidden',
            }}
          >
            {profileLoading
              ? <div className="skeleton" style={{ height: 18, width: '60%', margin: '0 auto', borderRadius: 4 }} />
              : 'Build Profile'}
          </button>

          <div style={{ height: 1, background: '#1E1E2E', marginBottom: 20 }} />

          <SectionHeader num="02" label="Target Item" />

          <div style={{ marginBottom: 10 }}>
            <label htmlFor="item-name" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Place Name</label>
            <input
              id="item-name"
              type="text"
              placeholder="e.g. Chicken Republic Lekki"
              value={targetItem.name}
              onChange={e => setTargetItem(t => ({ ...t, name: e.target.value }))}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <label htmlFor="item-desc" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Description (optional)</label>
            <input
              id="item-desc"
              type="text"
              placeholder="e.g. Fast food, Nigerian cuisine"
              value={targetItem.description}
              onChange={e => setTargetItem(t => ({ ...t, description: e.target.value }))}
            />
          </div>

          <div style={{ marginBottom: 14 }}>
            <Toggle on={useLLM} onToggle={() => setUseLLM(v => !v)} label="Use LLM" />
            {useLLM && (
              <div style={{
                marginTop: 8, background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.3)',
                borderRadius: 8, padding: '6px 10px', fontSize: 12, color: '#F59E0B',
                animation: reduced ? 'none' : 'fadeSlideIn 0.2s ease',
              }}>
                ⚡ LLM mode adds ~3s latency
              </div>
            )}
          </div>

          <div style={{ position: 'relative' }}>
            <button
              onClick={handleSimulate}
              disabled={!canSimulate || outputLoading}
              title={!canSimulate ? 'Build a profile first' : ''}
              style={{
                width: '100%', background: canSimulate ? '#F59E0B' : '#1E1E2E',
                color: canSimulate ? '#0A0A0F' : '#64748B',
                border: 'none', borderRadius: 8, padding: '10px 0',
                fontWeight: 600, fontSize: 14,
                cursor: !canSimulate || outputLoading ? 'not-allowed' : 'pointer',
              }}
            >
              {outputLoading
                ? <div className="skeleton" style={{ height: 18, width: '60%', margin: '0 auto', borderRadius: 4 }} />
                : 'Simulate Review'}
            </button>
          </div>
        </div>
      </div>

      {/* Center col */}
      <div style={{ gridColumn: 'span 4' }}>
        <ProfilePanel profile={profile} loading={profileLoading} />
      </div>

      {/* Right col */}
      <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <TracePanel trace={output?.reasoning ?? null} mode="text" loading={traceLoading} />
        <OutputPanel output={output} loading={outputLoading} />
      </div>
    </div>
  );
}
