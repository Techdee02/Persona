import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function Skeleton() {
  return (
    <div style={{ paddingLeft: 28, marginBottom: 16 }}>
      <div className="skeleton" style={{ height: 14, width: '60%', marginBottom: 6 }} />
      <div className="skeleton" style={{ height: 10, width: '80%' }} />
    </div>
  );
}

export default function AgentTimeline({ steps, loading }) {
  const [openIdx, setOpenIdx] = useState(null);

  if (loading) {
    return (
      <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
        <div className="skeleton" style={{ height: 14, width: '40%', marginBottom: 16 }} />
        {[0, 1, 2, 3].map(i => <Skeleton key={i} />)}
      </div>
    );
  }

  if (!steps.length) return null;

  return (
    <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20, marginBottom: 16 }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC', marginBottom: 16 }}>Agent Pipeline</div>
      <div style={{ position: 'relative', paddingLeft: 24 }}>
        <div style={{ position: 'absolute', left: 7, top: 0, bottom: 0, width: 2, background: '#6366F1', opacity: 0.35 }} />
        {steps.map((step, i) => (
          <div
            key={i}
            style={{
              position: 'relative', marginBottom: 16,
              opacity: 0, animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
              animationDelay: reduced ? '0ms' : `${i * 300}ms`,
            }}
          >
            <div style={{
              position: 'absolute', left: -24, top: 2,
              width: 16, height: 16, borderRadius: '50%', background: '#6366F1',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{ color: '#fff', fontSize: 8, fontWeight: 700 }}>✓</span>
            </div>
            <button
              onClick={() => setOpenIdx(openIdx === i ? null : i)}
              aria-label={`Toggle step ${i + 1}`}
              style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', width: '100%', cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, color: '#F8FAFC' }}>
                  Step {i + 1} — {step.tool}
                </span>
                <span style={{ color: '#22C55E', fontSize: 11 }}>✓</span>
                <ChevronDown size={12} color="#64748B" style={{
                  marginLeft: 'auto',
                  transform: openIdx === i ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.2s',
                }} />
              </div>
            </button>
            <div style={{ color: '#64748B', fontSize: 12, marginTop: 2 }}>{step.thought}</div>
            {openIdx === i && (
              <div style={{
                background: '#0A0A0F', borderRadius: 8, padding: '10px 12px',
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                maxHeight: 200, overflow: 'auto', marginTop: 8,
              }}>
                {JSON.stringify(step.result, null, 2).split('\n').map((line, li) => {
                  const km = line.match(/^(\s*)("[\w\s]+")\s*:/);
                  const vm = line.match(/:\s*(".*"|[\d.]+|true|false|null)/);
                  return (
                    <div key={li}>
                      {km ? (
                        <>
                          <span style={{ color: '#64748B' }}>{km[1]}</span>
                          <span style={{ color: '#6366F1' }}>{km[2]}</span>
                          <span style={{ color: '#64748B' }}>: </span>
                          {vm ? <span style={{ color: '#F59E0B' }}>{vm[1]}</span>
                            : <span style={{ color: '#64748B' }}>{line.slice(km[0].length)}</span>}
                        </>
                      ) : <span style={{ color: '#64748B' }}>{line}</span>}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
