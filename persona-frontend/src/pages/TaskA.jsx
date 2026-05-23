import { useState, useEffect, useRef } from 'react';
import { Copy, Check, Star } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import ProfilePanel from '../components/profile/ProfilePanel';
import TracePanel from '../components/trace/TracePanel';
import FidelityDashboard from '../components/task-a/FidelityDashboard';
import Tooltip from '../components/ui/Tooltip';
import { buildProfile, simulateTaskA } from '../lib/api';
import { DEMO_USERS, DEMO_REAL_REVIEWS, DEMO_EXPLANATIONS } from '../lib/demo-users';
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

function wordOverlapScore(a, b) {
  const setA = new Set(a.toLowerCase().split(/\s+/));
  const setB = new Set(b.toLowerCase().split(/\s+/));
  const intersection = [...setA].filter(w => setB.has(w)).length;
  return Math.round((intersection / Math.max(setA.size, setB.size)) * 100);
}

function HighlightedReview({ text, userId }) {
  const explanations = DEMO_EXPLANATIONS[userId];
  if (!explanations || !text) return <span>{text}</span>;

  const entries = Object.entries(explanations).sort((a, b) => b[0].length - a[0].length);
  const parts = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    let matched = false;
    for (const [phrase, explanation] of entries) {
      const idx = remaining.toLowerCase().indexOf(phrase.toLowerCase());
      if (idx === 0) {
        parts.push(
          <Tooltip key={key++} text={explanation}>
            <span style={{ textDecoration: 'underline dotted #F59E0B', cursor: 'help' }}>
              {remaining.slice(0, phrase.length)}
            </span>
          </Tooltip>
        );
        remaining = remaining.slice(phrase.length);
        matched = true;
        break;
      }
    }
    if (!matched) {
      let nextMatch = remaining.length;
      for (const [phrase] of entries) {
        const idx = remaining.toLowerCase().indexOf(phrase.toLowerCase());
        if (idx > 0 && idx < nextMatch) nextMatch = idx;
      }
      parts.push(<span key={key++}>{remaining.slice(0, nextMatch)}</span>);
      remaining = remaining.slice(nextMatch);
    }
  }

  return <>{parts}</>;
}

function TypewriterText({ text, userId }) {
  const [displayed, setDisplayed] = useState('');
  const [done, setDone] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!text) return;
    setDone(false);
    if (reduced) { setDisplayed(text); setDone(true); return; }
    setDisplayed('');
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(iv); setDone(true); }
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
        {done
          ? <HighlightedReview text={displayed} userId={userId} />
          : <>{displayed}{displayed.length < text.length && <span style={{ opacity: 0.5 }}>|</span>}</>
        }
      </div>
    </div>
  );
}

function ConfidenceBand({ predictedRating, profile }) {
  if (!profile) return null;
  const std = profile.rating_stats?.std_dev ?? 0;
  const count = profile.rating_stats?.count ?? 0;
  if (!std && !count) return null;

  const lower = Math.max(1, predictedRating - std).toFixed(1);
  const upper = Math.min(5, predictedRating + std).toFixed(1);
  const confidence = count >= 10 ? 'High' : count >= 5 ? 'Medium' : 'Low';
  const confidenceColor = count >= 10 ? '#22C55E' : count >= 5 ? '#F59E0B' : '#EF4444';

  const lowerPct = ((parseFloat(lower) - 1) / 4) * 100;
  const upperPct = ((parseFloat(upper) - 1) / 4) * 100;

  return (
    <div style={{ marginTop: 12, padding: '10px 14px', background: '#0A0A0F', borderRadius: 8, border: '1px solid #1E1E2E' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#64748B' }}>
          Range: {lower} — {upper}
        </span>
        <span
          title={`Based on ${count} reviews. More history = narrower range.`}
          style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: confidenceColor, cursor: 'default' }}
        >
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: confidenceColor, display: 'inline-block' }} />
          Confidence: {confidence}
        </span>
      </div>
      <div style={{ height: 4, background: '#1E1E2E', borderRadius: 2, position: 'relative' }}>
        <div style={{
          position: 'absolute', left: `${lowerPct}%`, width: `${upperPct - lowerPct}%`,
          height: '100%', background: '#F59E0B', borderRadius: 2,
          transition: reduced ? 'none' : 'width 0.4s ease',
        }} />
      </div>
    </div>
  );
}

function ComparisonDrawer({ generatedText, userId }) {
  const [open, setOpen] = useState(false);
  if (!userId?.startsWith('demo_')) return null;

  const realReview = DEMO_REAL_REVIEWS[userId] ?? '';
  const score = generatedText && realReview ? wordOverlapScore(generatedText, realReview) : 0;
  const scoreColor = score >= 60 ? '#22C55E' : score >= 40 ? '#F59E0B' : '#EF4444';

  return (
    <div style={{ marginTop: 12 }}>
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Compare with real review"
        style={{
          width: '100%', background: 'none', border: '1px solid #1E1E2E',
          borderRadius: 8, color: '#64748B', fontSize: 12, padding: '8px 0',
          cursor: 'pointer', transition: 'border-color 0.2s, color 0.2s',
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.color = '#F8FAFC'; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = '#1E1E2E'; e.currentTarget.style.color = '#64748B'; }}
      >
        {open ? 'Hide comparison' : 'Compare with real review'}
      </button>

      <div style={{
        overflow: 'hidden',
        maxHeight: open ? 400 : 0,
        transition: reduced ? 'none' : 'max-height 0.35s ease',
      }}>
        <div style={{ paddingTop: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <div style={{ flex: 1, fontSize: 11, color: '#6366F1', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>AI Generated</div>
            <span style={{
              background: `${scoreColor}20`, border: `1px solid ${scoreColor}`,
              borderRadius: 999, padding: '2px 10px', fontSize: 11, color: scoreColor, fontWeight: 600,
            }}>
              Similarity: {score}%
            </span>
            <div style={{ flex: 1, fontSize: 11, color: '#F59E0B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', textAlign: 'right' }}>Real Review</div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {[generatedText, realReview].map((txt, i) => (
              <div key={i} style={{
                flex: 1, background: '#0A0A0F', border: '1px solid #1E1E2E', borderRadius: 8,
                padding: 12, fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
                color: '#F8FAFC', lineHeight: 1.6, maxHeight: 200, overflowY: 'auto',
              }}>
                {txt}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function OutputPanel({ output, loading, profile, userId }) {
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

      {/* Feature 2: Confidence Band */}
      <ConfidenceBand predictedRating={rating} profile={profile} />

      <div style={{ height: 1, background: '#1E1E2E', margin: '16px 0' }} />

      <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>
        Generated Review
      </div>
      <TypewriterText text={output.review_text ?? ''} userId={userId} />

      {/* Feature 3: Comparison Drawer */}
      <ComparisonDrawer generatedText={output.review_text ?? ''} userId={userId} />
    </div>
  );
}

export default function TaskA() {
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
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
  const autoBuilt = useRef(false);

  const handleBuildProfile = async (uid, recs) => {
    setProfileLoading(true);
    try {
      const p = await buildProfile(uid, recs);
      setProfile(p);
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setProfileLoading(false);
    }
  };

  // Feature 8: Shareable URL — auto-load demo on mount
  useEffect(() => {
    const demoParam = searchParams.get('demo');
    if (demoParam && DEMO_USERS[demoParam] && !autoBuilt.current) {
      autoBuilt.current = true;
      const demoUser = DEMO_USERS[demoParam];
      setRecords(demoUser.records);
      setSelectedDemo(demoParam);
      handleBuildProfile(demoParam, demoUser.records);
    }
  }, []);

  // Feature 9: Reset listener
  useEffect(() => {
    const onReset = () => {
      setRecords([]);
      setSelectedDemo('');
      setProfile(null);
      setOutput(null);
      setTargetItem({ name: '', description: '' });
      setUseLLM(false);
      autoBuilt.current = false;
    };
    window.addEventListener('persona:reset', onReset);
    return () => window.removeEventListener('persona:reset', onReset);
  }, []);

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
            onClick={() => handleBuildProfile(selectedDemo || 'custom_user', records)}
            disabled={profileLoading}
            style={{
              width: '100%', background: '#6366F1', color: '#fff', border: 'none',
              borderRadius: 8, padding: '10px 0', fontWeight: 600, fontSize: 14,
              cursor: profileLoading ? 'not-allowed' : 'pointer', marginBottom: 20,
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

      {/* Center col */}
      <div style={{ gridColumn: 'span 4' }}>
        <ProfilePanel profile={profile} loading={profileLoading} pageContext="task-a" />
      </div>

      {/* Right col */}
      <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <TracePanel trace={output?.reasoning ?? null} mode="text" loading={traceLoading} />
        {/* Feature 4: Fidelity Dashboard */}
        <FidelityDashboard profile={profile} output={output} />
        <OutputPanel
          output={output}
          loading={outputLoading}
          profile={profile}
          userId={selectedDemo || 'custom_user'}
        />
      </div>
    </div>
  );
}
