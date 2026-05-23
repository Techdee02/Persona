import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ProfilePanel from '../components/profile/ProfilePanel';
import RecommendationCard from '../components/task-b/RecommendationCard';
import AgentTimeline from '../components/task-b/AgentTimeline';
import ColdStartChat from '../components/task-b/ColdStartChat';
import ConversationLog from '../components/task-b/ConversationLog';
import { buildProfile, recommend, runAgent } from '../lib/api';
import { DEMO_USERS, DEMO_AGENT_PAYLOAD } from '../lib/demo-users';
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
        role="switch" aria-checked={on} aria-label={label} onClick={onToggle}
        style={{
          width: 40, height: 22, borderRadius: 11, border: 'none', cursor: 'pointer',
          background: on ? '#6366F1' : '#1E1E2E', position: 'relative',
          transition: reduced ? 'none' : 'background 0.2s',
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

function uuid() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);
}

export default function TaskB() {
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const [entryMode, setEntryMode] = useState('history');
  const [records, setRecords] = useState([]);
  const [selectedDemo, setSelectedDemo] = useState('');
  const [demoChip, setDemoChip] = useState(false);
  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [axes, setAxes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [agentMode, setAgentMode] = useState(false);
  const [agentSteps, setAgentSteps] = useState([]);
  const [agentLoading, setAgentLoading] = useState(false);
  const [constraintInput, setConstraintInput] = useState('');
  const [constraints, setConstraints] = useState([]);
  // Feature 5: Conversation log
  const [turns, setTurns] = useState([]);
  const chipTimer = useRef(null);
  const autoBuilt = useRef(false);

  // Feature 6: primaryDomain from top value_keyword
  const primaryDomain = profile
    ? (Object.entries(profile.value_keywords ?? {}).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null)
    : null;

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

  // Feature 8: Shareable URL
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
      setRecommendations([]);
      setAxes([]);
      setSessionId(null);
      setTurns([]);
      setQueryText('');
      setConstraints([]);
      autoBuilt.current = false;
    };
    window.addEventListener('persona:reset', onReset);
    return () => window.removeEventListener('persona:reset', onReset);
  }, []);

  const handleDemoSelect = (e) => {
    const key = e.target.value;
    setSelectedDemo(key);
    if (!key) { setRecords([]); return; }
    setRecords(DEMO_USERS[key]?.records ?? []);
    setDemoChip(true);
    clearTimeout(chipTimer.current);
    chipTimer.current = setTimeout(() => setDemoChip(false), 2000);
  };

  useEffect(() => () => clearTimeout(chipTimer.current), []);

  const handleRecommend = async (append = false) => {
    setRecsLoading(true);
    try {
      const result = await recommend({
        user_id: selectedDemo || 'custom_user',
        records,
        query_text: queryText,
        top_k: 5,
        session_id: sessionId ?? undefined,
      });
      setSessionId(result.session_id);
      setAxes(result.axes ?? []);
      const newRecs = result.recommendations ?? [];
      setRecommendations(prev => append ? [...prev, ...newRecs] : newRecs);

      // Feature 5: append turn
      setTurns(prev => [...prev, {
        id: uuid(),
        query: queryText,
        constraintsApplied: [...constraints],
        resultCount: newRecs.length,
        timestamp: new Date(),
      }]);

      if (agentMode) {
        setAgentLoading(true);
        try {
          const agentResult = await runAgent({ ...DEMO_AGENT_PAYLOAD, user_id: selectedDemo || 'demo_generous' });
          setAgentSteps(agentResult.steps ?? []);
        } catch (e) {
          showToast(e.message, 'error');
        } finally {
          setAgentLoading(false);
        }
      }
    } catch (e) {
      showToast(e.message, 'error');
    } finally {
      setRecsLoading(false);
    }
  };

  const handleClearSession = () => {
    setTurns([]);
    setSessionId(null);
    setRecommendations([]);
    setAxes([]);
  };

  const addConstraint = (e) => {
    if (e.key === 'Enter' && constraintInput.trim()) {
      setConstraints(c => [...c, constraintInput.trim()]);
      setConstraintInput('');
    }
  };

  return (
    <div style={{
      display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)',
      gap: 16, padding: 24, minHeight: 'calc(100vh - 56px)',
    }}>
      {/* Left col */}
      <div style={{ gridColumn: 'span 4' }}>
        <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
          {/* Tab switcher */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 20, background: '#0A0A0F', borderRadius: 8, padding: 4 }}>
            {[['history', 'Review History'], ['coldstart', 'Cold Start Chat']].map(([mode, label]) => (
              <button
                key={mode}
                onClick={() => setEntryMode(mode)}
                style={{
                  flex: 1, padding: '7px 0', borderRadius: 6, border: 'none', fontSize: 12, fontWeight: 600,
                  background: entryMode === mode ? '#6366F1' : 'transparent',
                  color: entryMode === mode ? '#fff' : '#64748B',
                  cursor: 'pointer', transition: reduced ? 'none' : 'all 0.2s',
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {entryMode === 'history' ? (
            <>
              <SectionHeader num="01" label="Build Profile" />
              <div style={{ marginBottom: 12 }}>
                <label htmlFor="demo-select-b" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Demo User</label>
                <select id="demo-select-b" value={selectedDemo} onChange={handleDemoSelect}>
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
                <label htmlFor="records-b" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Review Records (JSON)</label>
                <textarea
                  id="records-b"
                  rows={5}
                  placeholder='Paste JSON review records here, or select a demo user above.'
                  value={records.length ? JSON.stringify(records, null, 2) : ''}
                  onChange={e => { try { setRecords(JSON.parse(e.target.value)); } catch { /* ignore */ } }}
                  style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, resize: 'vertical', minHeight: 100 }}
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
            </>
          ) : (
            <ColdStartChat onProfileBuilt={(p) => setProfile(p)} />
          )}

          <div style={{ height: 1, background: '#1E1E2E', marginBottom: 20 }} />

          <SectionHeader num="03" label="Your Query" />

          <div style={{ marginBottom: 10 }}>
            <label htmlFor="query-input" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>What are you looking for?</label>
            <input
              id="query-input"
              type="text"
              placeholder="e.g. spicy grilled food, budget-friendly, Lagos vibe"
              value={queryText}
              onChange={e => setQueryText(e.target.value)}
            />
          </div>

          {/* Feature 5: Conversation Log — below query, above constraints */}
          <ConversationLog turns={turns} onClear={handleClearSession} />

          {/* Constraints */}
          <div style={{ marginBottom: 14 }}>
            <label htmlFor="constraint-input" style={{ fontSize: 12, color: '#64748B', display: 'block', marginBottom: 6 }}>Constraints (press Enter to add)</label>
            <input
              id="constraint-input"
              type="text"
              placeholder="e.g. outdoor seating"
              value={constraintInput}
              onChange={e => setConstraintInput(e.target.value)}
              onKeyDown={addConstraint}
            />
            {constraints.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                {constraints.map((c, i) => (
                  <span key={i} style={{
                    background: '#0A0A0F', border: '1px solid #6366F1',
                    borderRadius: 999, padding: '3px 10px', fontSize: 11, color: '#F8FAFC',
                    display: 'flex', alignItems: 'center', gap: 6,
                  }}>
                    {c}
                    <button
                      onClick={() => setConstraints(cs => cs.filter((_, j) => j !== i))}
                      aria-label={`Remove constraint ${c}`}
                      style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer', padding: 0, fontSize: 12 }}
                    >×</button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => handleRecommend(false)}
            disabled={recsLoading || !queryText.trim()}
            style={{
              width: '100%', background: queryText.trim() ? '#6366F1' : '#1E1E2E',
              color: queryText.trim() ? '#fff' : '#64748B',
              border: 'none', borderRadius: 8, padding: '10px 0',
              fontWeight: 600, fontSize: 14,
              cursor: recsLoading || !queryText.trim() ? 'not-allowed' : 'pointer',
              marginBottom: 12,
            }}
          >
            {recsLoading
              ? <div className="skeleton" style={{ height: 18, width: '60%', margin: '0 auto', borderRadius: 4 }} />
              : 'Find Recommendations'}
          </button>

          <Toggle on={agentMode} onToggle={() => setAgentMode(v => !v)} label="Agent Mode" />
          {agentMode && (
            <div style={{
              marginTop: 8, background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.3)',
              borderRadius: 8, padding: '6px 10px', fontSize: 12, color: '#F59E0B',
              animation: reduced ? 'none' : 'fadeSlideIn 0.2s ease',
            }}>
              Shows the 4-step AI reasoning pipeline
            </div>
          )}
        </div>
      </div>

      {/* Center col */}
      <div style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* Feature 6: pass primaryDomain + queryText to ProfilePanel */}
        <ProfilePanel
          profile={profile}
          loading={profileLoading}
          primaryDomain={primaryDomain}
          queryText={queryText}
          pageContext="task-b"
        />

        {axes.length > 0 && (
          <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
            <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 14 }}>
              Detected Preference Axes
            </div>
            {axes.map((axis, i) => (
              <div
                key={axis.name}
                style={{
                  marginBottom: 14, opacity: 0,
                  animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
                  animationDelay: reduced ? '0ms' : `${i * 80}ms`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC' }}>{axis.name}</span>
                  <div style={{ width: 120, height: 6, background: '#1E1E2E', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', background: '#F59E0B', borderRadius: 3,
                      width: `${(axis.weight ?? 0) * 100}%`,
                      transition: reduced ? 'none' : 'width 0.6s ease',
                    }} />
                  </div>
                </div>
                <div style={{ fontSize: 12, color: '#64748B' }}>{axis.rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right col */}
      <div style={{ gridColumn: 'span 4' }}>
        {agentMode && <AgentTimeline steps={agentSteps} loading={agentLoading} />}

        <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC' }}>
              {recommendations.length > 0
                ? `${recommendations.length} results${queryText ? ` for "${queryText}"` : ''}`
                : 'Recommendations'}
            </span>
            {recommendations.length > 0 && (
              <button
                onClick={() => handleRecommend(true)}
                disabled={recsLoading}
                style={{
                  background: 'none', border: '1px solid #1E1E2E', borderRadius: 6,
                  color: '#64748B', fontSize: 12, padding: '4px 10px', cursor: 'pointer',
                }}
              >
                Show more
              </button>
            )}
          </div>

          {recsLoading && recommendations.length === 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {[1, 2, 3].map(i => (
                <div key={i} style={{ background: '#0A0A0F', borderRadius: 10, padding: 16 }}>
                  <div className="skeleton" style={{ height: 14, width: '70%', marginBottom: 8 }} />
                  <div className="skeleton" style={{ height: 10, width: '50%', marginBottom: 6 }} />
                  <div className="skeleton" style={{ height: 10, width: '80%' }} />
                </div>
              ))}
            </div>
          ) : recommendations.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px 0', color: '#64748B', fontSize: 13 }}>
              Enter a query and click Find Recommendations.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {recommendations.map((item, i) => (
                <RecommendationCard key={`${item.item_id}-${i}`} item={item} rank={i + 1} animationDelay={i * 60} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
