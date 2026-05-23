import { useState } from 'react';
import { Terminal, ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function JsonBox({ data }) {
  const str = JSON.stringify(data, null, 2);
  return (
    <div className="bg-[#0A0A0F] rounded-lg px-3 py-2.5 text-[11px] max-h-48 overflow-auto mt-2"
      style={{ fontFamily: 'JetBrains Mono, monospace' }}>
      {str.split('\n').map((line, i) => {
        const km = line.match(/^(\s*)("[\w\s]+")\s*:/);
        const vm = line.match(/:\s*(".*"|[\d.]+|true|false|null)/);
        return (
          <div key={i}>
            {km ? (
              <>
                <span className="text-[#64748B]">{km[1]}</span>
                <span className="text-[#6366F1]">{km[2]}</span>
                <span className="text-[#64748B]">: </span>
                {vm ? <span className="text-[#F59E0B]">{vm[1]}</span>
                  : <span className="text-[#64748B]">{line.slice(km[0].length)}</span>}
              </>
            ) : <span className="text-[#64748B]">{line}</span>}
          </div>
        );
      })}
    </div>
  );
}

function AgentStep({ step, index }) {
  const [open, setOpen] = useState(false);
  return (
    <div
      className="pl-7 relative mb-4"
      style={{
        opacity: 0,
        animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
        animationDelay: reduced ? '0ms' : `${index * 300}ms`,
      }}
    >
      <div className="absolute left-0 top-0.5 w-4 h-4 rounded-full bg-[#6366F1] flex items-center justify-center">
        <span className="text-white text-[8px] font-bold">✓</span>
      </div>
      <button
        onClick={() => setOpen(o => !o)}
        className="bg-transparent border-none p-0 text-left w-full cursor-pointer"
        aria-label={`Toggle step ${index + 1} details`}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#F8FAFC]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            Step {index + 1} — {step.tool}
          </span>
          <span className="text-[11px] text-[#22C55E]">✓</span>
          <ChevronDown size={12} color="#64748B" style={{ marginLeft: 'auto', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
        </div>
      </button>
      <div className="text-xs text-[#64748B] mt-0.5">{step.thought}</div>
      {open && <JsonBox data={step.result} />}
    </div>
  );
}

export default function TracePanel({ trace, mode, steps = [], loading }) {
  const [raw, setRaw] = useState(false);

  if (loading) {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
        <div className="skeleton h-3.5 w-1/2 mb-3" />
        <div className="skeleton h-3 mb-2" />
        <div className="skeleton h-3 w-4/5 mb-2" />
        <div className="skeleton h-3 w-3/5" />
      </div>
    );
  }

  const isEmpty = mode === 'text' ? !trace : steps.length === 0;
  if (isEmpty) {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5 flex flex-col items-center justify-center min-h-[140px] gap-2.5">
        <Terminal size={24} color="#1E1E2E" />
        <span className="text-[#64748B] text-sm">Reasoning trace will appear after simulation.</span>
      </div>
    );
  }

  if (mode === 'agent') {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
        <div className="text-sm font-semibold text-[#F8FAFC] mb-4">Agent Trace</div>
        <div className="relative">
          <div className="absolute left-[7px] top-0 bottom-0 w-0.5 bg-[#6366F1] opacity-40" />
          {steps.map((step, i) => <AgentStep key={i} step={step} index={i} />)}
        </div>
      </div>
    );
  }

  const clauses = trace ? trace.split('; ').filter(Boolean) : [];

  return (
    <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
      <div className="flex items-center justify-between mb-3.5">
        <span className="text-sm font-semibold text-[#F8FAFC]">Reasoning Trace</span>
        <button
          onClick={() => setRaw(r => !r)}
          aria-label="Toggle raw trace view"
          className="bg-transparent border border-[#1E1E2E] rounded-md text-[#64748B] text-[11px] px-2 py-0.5 cursor-pointer"
        >
          {raw ? 'bullets' : '[raw]'}
        </button>
      </div>
      {raw ? (
        <pre className="text-[11px] text-[#64748B] bg-[#0A0A0F] rounded-lg p-3 overflow-auto whitespace-pre-wrap break-words m-0"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          {trace}
        </pre>
      ) : (
        <div className="flex flex-col gap-2">
          {clauses.map((clause, i) => (
            <div
              key={i}
              className="border-l-4 border-[#6366F1] pl-3 text-xs text-[#F8FAFC]"
              style={{
                fontFamily: 'JetBrains Mono, monospace',
                opacity: 0,
                animation: reduced ? 'none' : 'fadeSlideX 0.3s ease forwards',
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
