const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function pad(n) { return String(n).padStart(2, '0'); }
function fmt(d) { return `${pad(d.getHours())}:${pad(d.getMinutes())}`; }

export default function ConversationLog({ turns, onClear }) {
  if (!turns.length) return null;

  return (
    <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20, marginBottom: 16 }}>
      <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 14 }}>
        Conversation
      </div>

      <div style={{ position: 'relative' }}>
        <div style={{ position: 'absolute', left: 5, top: 8, bottom: 24, width: 2, background: '#1E1E2E', borderRadius: 1 }} />

        {turns.map((turn, i) => {
          const isLatest = i === turns.length - 1;
          return (
            <div
              key={turn.id}
              style={{
                paddingLeft: 22, marginBottom: 12, position: 'relative',
                opacity: 0,
                animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
                animationDelay: reduced ? '0ms' : `${i * 60}ms`,
                background: isLatest ? '#1A1A2E' : 'transparent',
                borderLeft: isLatest ? '2px solid #6366F1' : 'none',
                borderRadius: isLatest ? '0 6px 6px 0' : 0,
                padding: isLatest ? '8px 8px 8px 22px' : '0 0 0 22px',
              }}
            >
              <div style={{
                position: 'absolute', left: 0, top: 6,
                width: 12, height: 12, borderRadius: '50%',
                background: isLatest ? '#6366F1' : '#1E1E2E',
                border: isLatest ? 'none' : '2px solid #6366F1',
                flexShrink: 0,
              }} />

              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
                <span style={{
                  fontSize: 13, color: '#F8FAFC',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  maxWidth: 160,
                }}>
                  "{turn.query.length > 40 ? turn.query.slice(0, 40) + '…' : turn.query}"
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', flexShrink: 0 }}>
                  <span style={{ fontSize: 11, color: '#64748B' }}>{turn.resultCount} results</span>
                  <span style={{ fontSize: 11, color: '#64748B' }}>{fmt(turn.timestamp)}</span>
                </div>
              </div>

              {turn.constraintsApplied.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                  {turn.constraintsApplied.map((c, j) => (
                    <span key={j} style={{
                      background: '#0A0A0F', border: '1px solid #1E1E2E',
                      borderRadius: 999, padding: '1px 8px', fontSize: 10, color: '#64748B',
                    }}>{c}</span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <button
        onClick={onClear}
        aria-label="Clear session"
        style={{
          marginTop: 8, background: 'none', border: '1px solid #1E1E2E',
          borderRadius: 6, color: '#64748B', fontSize: 11, padding: '4px 12px',
          cursor: 'pointer', width: '100%',
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.color = '#F8FAFC'; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = '#1E1E2E'; e.currentTarget.style.color = '#64748B'; }}
      >
        Clear session
      </button>
    </div>
  );
}
