import { useState } from 'react';
import { Terminal, ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function Skeleton({ h = 14, w = '100%' }) {
  return <div className="skeleton" style={{ height: h, width: w, borderRadius: 6, marginBottom: 8 }} />;
}

function JsonBox({ data }) {
  const str = JSON.stringify(data, null, 2);
  const lines = str.split('\n').map((line, i) => {
    const keyMatch = line.match(/^(\s*)("[\w\s]+")\s*:/);
    const valMatch = line.match(/:\s*(".*"|[\d.]+|true|false|null)/);
    return (
      <div key={i}>
        {keyMatch ? (
          <>
            <span style={{ color: '#64748B' }}>{keyMatch[1]}</span>
            <span style={{ color: '#6366F1' }}>{keyMatch[2]}</span>
            <span style={{ color: '#64748B' }}>: </span>
            {valMatch && <span style={{ color: '#F59E0B' }}>{valMatch[1]}</span>}
            {!valMatch && <span style={{ color: '#64748B' }}>{line.slice(keyMatch[0].length)}</span>}
          </>
        ) : (
          <span style={{ color: '#64748B' }}>{line}</span>
        )}
      </div>
    );
  });
  return (
    <div style={{
      background: '#0A0A0F', borderRadius: 8, padding: '10px 12px',
      fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
      maxHeight: 200, overflow: 'auto', marginTop: 8,
    }}>
      {lines}
    </div>
  );
}

function AgentStep({ step, index }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={{
      paddingLeft: 28, position: 'relative', marginBottom: 16,
      opacity: 0, animation: reduced ? 'none' : `fadeSlideIn 0.3s ease forwards`,
      animationDelay: reduced ? '0ms' : `${index * 300}ms`,
    }}>
      <div style={{
        position: 'absolute', left: 0, top: 2,
        width: 16, height: 16, borderRadius: '50%',
        background: '#6366F1', display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <span style={{ color: '#fff', fontSize: 8, fontWeight: 700 }}>✓</span>
      </div>
      <button
        onClick={() => setOpen(o => !o)}
        style={{ background: 'none', border: 'none', padding: 0, textAlign: 'left', width: '100%', cursor: 'pointer' }}
        aria-label={`Toggle step ${index + 1} details`}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 13, color: '#F8FAFC' }}>
            Step {index + 1} — {step.tool}
          </span>
          <span style={{ color: '#22C55E', fontSize: 11 }}>✓</span>
          <ChevronDown size={12} color="#64748B" style={{ marginLeft: 'auto', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
        </div>
      </button>
      <div style={{ color: '#64748B', fontSize: 12, marginTop: 2 }}>{step.thought}</div>
      {open && <JsonBox data={step.result} />}
    </div>
  );
}

export default function TracePanel({ trace, mode, steps = [], loading }) {
  const [raw, setRaw] = useState(false);

  if (loading) {
    return (
      <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
        <Skeleton w="50%" h={14} />
        <Skeleton h={12} />
        <Skeleton h={12} w="80%" />
        <Skeleton h={12} w="60%" />
      </div>
    );
  }

  const isEmpty = mode === 'text' ? !trace : steps.length === 0;
  if (isEmpty) {
    return (
      <div style={{
        background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        minHeight: 140, gap: 10,
      }}>
        <Terminal size={24} color="#1E1E2E" />
        <span style={{ color: '#64748B', fontSize: 13 }}>Reasoning trace will appear after simulation.</span>
      </div>
    );
  }

  if (mode === 'agent') {
    return (
      <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC', marginBottom: 16 }}>Agent Trace</div>
        <div style={{ position: 'relative' }}>
          <div style={{ position: 'absolute', left: 7, top: 0, bottom: 0, width: 2, background: '#6366F1', opacity: 0.4 }} />
          {steps.map((step, i) => <AgentStep key={i} step={step} index={i} />)}
        </div>
      </div>
    );
  }

  const clauses = trace ? trace.split('; ').filter(Boolean) : [];

  return (
    <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC' }}>Reasoning Trace</span>
        <button
          onClick={() => setRaw(r => !r)}
          aria-label="Toggle raw trace view"
          style={{
            background: 'none', border: '1px solid #1E1E2E', borderRadius: 6,
            color: '#64748B', fontSize: 11, padding: '2px 8px', cursor: 'pointer',
          }}
        >
          {raw ? 'bullets' : '[raw]'}
        </button>
      </div>
      {raw ? (
        <pre style={{
          fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#64748B',
          background: '#0A0A0F', borderRadius: 8, padding: 12, overflow: 'auto',
          whiteSpace: 'pre-wrap', wordBreak: 'break-word', margin: 0,
        }}>
          {trace}
        </pre>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {clauses.map((clause, i) => (
            <div
              key={i}
              style={{
                borderLeft: '4px solid #6366F1', paddingLeft: 12,
                fontFamily: 'JetBrains Mono, monospace', fontSize: 12, color: '#F8FAFC',
                opacity: 0, animation: reduced ? 'none' : 'fadeSlideX 0.3s ease forwards',
                animationDelay: reduced ? '0ms' : `${i * 120}ms`,
              }}
            >
              {clause}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
