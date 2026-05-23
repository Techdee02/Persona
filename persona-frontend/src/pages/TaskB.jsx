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
    <div className="flex items-center gap-2.5 mb-3.5">
      <div className="w-1 h-5 bg-[#F59E0B] rounded-sm" />
      <span className="text-[10px] text-[#64748B] uppercase tracking-widest font-semibold">{num} — {label}</span>
    </div>
  );
}

function Toggle({ on, onToggle, label }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-[#F8FAFC]">{label}</span>
      <button
        role="switch" aria-checked={on} aria-label={label} onClick={onToggle}
        className="relative border-none cursor-pointer rounded-full"
        style={{
          width: 40, height: 22,
          background: on ? '#6366F1' : '#1E1E2E',
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
  const [turns, setTurns] = useState([]);
  const chipTimer = useRef(null);
  const autoBuilt = useRef(false);

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

  useEffect(() => {
    const onReset = () => {
      setRecords([]); setSelectedDemo(''); setProfile(null);
      setRecommendations([]); setAxes([]); setSessionId(null);
      setTurns([]); setQueryText(''); setConstraints([]);
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
        user_id: selectedDemo || 'custom_user', records,
        query_text: queryText, top_k: 5,
        session_id: sessionId ?? undefined,
      });
      setSessionId(result.session_id);
      setAxes(result.axes ?? []);
      const newRecs = result.recommendations ?? [];
      setRecommendations(prev => append ? [...prev, ...newRecs] : newRecs);
      setTurns(prev => [...prev, {
        id: uuid(), query: queryText,
        constraintsApplied: [...constraints],
        resultCount: newRecs.length, timestamp: new Date(),
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
    setTurns([]); setSessionId(null); setRecommendations([]); setAxes([]);
  };

  const addConstraint = (e) => {
    if (e.key === 'Enter' && constraintInput.trim()) {
      setConstraints(c => [...c, constraintInput.trim()]);
      setConstraintInput('');
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 md:p-6 min-h-[calc(100vh-56px)]">

      {/* Left col — inputs */}
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
        {/* Tab switcher */}
        <div className="flex gap-1 mb-5 bg-[#0A0A0F] rounded-lg p-1">
          {[['history', 'Review History'], ['coldstart', 'Cold Start Chat']].map(([mode, label]) => (
            <button
              key={mode}
              onClick={() => setEntryMode(mode)}
              className="flex-1 py-1.5 rounded-md border-none text-xs font-semibold cursor-pointer"
              style={{
                background: entryMode === mode ? '#6366F1' : 'transparent',
                color: entryMode === mode ? '#fff' : '#64748B',
                transition: reduced ? 'none' : 'all 0.2s',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {entryMode === 'history' ? (
          <>
            <SectionHeader num="01" label="Build Profile" />
            <div className="mb-3">
              <label htmlFor="demo-select-b" className="text-xs text-[#64748B] block mb-1.5">Demo User</label>
              <select id="demo-select-b" value={selectedDemo} onChange={handleDemoSelect}>
                <option value="">Select a demo user</option>
                {Object.entries(DEMO_USERS).map(([k, v]) => (
                  <option key={k} value={k}>{v.label}</option>
                ))}
              </select>
              {demoChip && (
                <div className="mt-1.5 inline-flex items-center gap-1 bg-[rgba(34,197,94,0.1)] border border-[#22C55E] rounded-full px-2.5 py-0.5 text-[11px] text-[#22C55E]">
                  Demo data loaded ✓
                </div>
              )}
            </div>
            <div className="mb-3">
              <label htmlFor="records-b" className="text-xs text-[#64748B] block mb-1.5">Review Records (JSON)</label>
              <textarea
                id="records-b" rows={4}
                placeholder="Paste JSON review records here, or select a demo user above."
                value={records.length ? JSON.stringify(records, null, 2) : ''}
                onChange={e => { try { setRecords(JSON.parse(e.target.value)); } catch { } }}
                style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, resize: 'vertical', minHeight: 90 }}
              />
            </div>
            <button
              onClick={() => handleBuildProfile(selectedDemo || 'custom_user', records)}
              disabled={profileLoading}
              className="w-full bg-[#6366F1] text-white border-none rounded-lg py-2.5 font-semibold text-sm mb-5 cursor-pointer disabled:cursor-not-allowed"
            >
              {profileLoading
                ? <div className="skeleton h-4 w-3/5 mx-auto rounded" />
                : 'Build Profile'}
            </button>
          </>
        ) : (
          <ColdStartChat onProfileBuilt={(p) => setProfile(p)} />
        )}

        <div className="h-px bg-[#1E1E2E] mb-5" />
        <SectionHeader num="03" label="Your Query" />

        <div className="mb-2.5">
          <label htmlFor="query-input" className="text-xs text-[#64748B] block mb-1.5">What are you looking for?</label>
          <input id="query-input" type="text"
            placeholder="e.g. spicy grilled food, budget-friendly, Lagos vibe"
            value={queryText} onChange={e => setQueryText(e.target.value)} />
        </div>

        <ConversationLog turns={turns} onClear={handleClearSession} />

        <div className="mb-3.5">
          <label htmlFor="constraint-input" className="text-xs text-[#64748B] block mb-1.5">Constraints (press Enter to add)</label>
          <input id="constraint-input" type="text" placeholder="e.g. outdoor seating"
            value={constraintInput} onChange={e => setConstraintInput(e.target.value)} onKeyDown={addConstraint} />
          {constraints.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {constraints.map((c, i) => (
                <span key={i} className="bg-[#0A0A0F] border border-[#6366F1] rounded-full px-2.5 py-0.5 text-[11px] text-[#F8FAFC] flex items-center gap-1.5">
                  {c}
                  <button
                    onClick={() => setConstraints(cs => cs.filter((_, j) => j !== i))}
                    aria-label={`Remove constraint ${c}`}
                    className="bg-transparent border-none text-[#64748B] cursor-pointer p-0 text-xs"
                  >×</button>
                </span>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={() => handleRecommend(false)}
          disabled={recsLoading || !queryText.trim()}
          className="w-full border-none rounded-lg py-2.5 font-semibold text-sm mb-3 cursor-pointer disabled:cursor-not-allowed"
          style={{
            background: queryText.trim() ? '#6366F1' : '#1E1E2E',
            color: queryText.trim() ? '#fff' : '#64748B',
          }}
        >
          {recsLoading
            ? <div className="skeleton h-4 w-3/5 mx-auto rounded" />
            : 'Find Recommendations'}
        </button>

        <Toggle on={agentMode} onToggle={() => setAgentMode(v => !v)} label="Agent Mode" />
        {agentMode && (
          <div className="mt-2 bg-[rgba(245,158,11,0.08)] border border-[rgba(245,158,11,0.3)] rounded-lg px-2.5 py-1.5 text-xs text-[#F59E0B]"
            style={{ animation: reduced ? 'none' : 'fadeSlideIn 0.2s ease' }}>
            Shows the 4-step AI reasoning pipeline
          </div>
        )}
      </div>

      {/* Center col — profile + axes */}
      <div className="flex flex-col gap-4">
        <ProfilePanel
          profile={profile} loading={profileLoading}
          primaryDomain={primaryDomain} queryText={queryText} pageContext="task-b"
        />

        {axes.length > 0 && (
          <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
            <div className="text-[10px] text-[#64748B] uppercase tracking-widest mb-3.5">Detected Preference Axes</div>
            {axes.map((axis, i) => (
              <div key={axis.name} style={{
                marginBottom: 14, opacity: 0,
                animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
                animationDelay: reduced ? '0ms' : `${i * 80}ms`,
              }}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-[#F8FAFC]">{axis.name}</span>
                  <div className="w-28 h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
                    <div style={{
                      height: '100%', background: '#F59E0B', borderRadius: 3,
                      width: `${(axis.weight ?? 0) * 100}%`,
                      transition: reduced ? 'none' : 'width 0.6s ease',
                    }} />
                  </div>
                </div>
                <div className="text-xs text-[#64748B]">{axis.rationale}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right col — agent + recommendations */}
      <div className="flex flex-col gap-4">
        {agentMode && <AgentTimeline steps={agentSteps} loading={agentLoading} />}

        <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold text-[#F8FAFC]">
              {recommendations.length > 0
                ? `${recommendations.length} results${queryText ? ` for "${queryText}"` : ''}`
                : 'Recommendations'}
            </span>
            {recommendations.length > 0 && (
              <button
                onClick={() => handleRecommend(true)}
                disabled={recsLoading}
                className="bg-transparent border border-[#1E1E2E] rounded-md text-[#64748B] text-xs px-2.5 py-1 cursor-pointer"
              >
                Show more
              </button>
            )}
          </div>

          {recsLoading && recommendations.length === 0 ? (
            <div className="flex flex-col gap-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-[#0A0A0F] rounded-lg p-4">
                  <div className="skeleton h-3.5 w-3/4 mb-2" />
                  <div className="skeleton h-2.5 w-1/2 mb-1.5" />
                  <div className="skeleton h-2.5 w-4/5" />
                </div>
              ))}
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-8 text-[#64748B] text-sm">
              Enter a query and click Find Recommendations.
            </div>
          ) : (
            <div className="flex flex-col gap-3">
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
