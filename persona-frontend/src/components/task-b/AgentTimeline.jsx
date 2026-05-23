import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export default function AgentTimeline({ steps, loading }) {
  const [openIdx, setOpenIdx] = useState(null);

  if (loading) {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
        <div className="skeleton h-3.5 w-2/5 mb-4" />
        {[0, 1, 2, 3].map(i => (
          <div key={i} className="pl-7 mb-4">
            <div className="skeleton h-3.5 w-3/5 mb-1.5" />
            <div className="skeleton h-2.5 w-4/5" />
          </div>
        ))}
      </div>
    );
  }

  if (!steps.length) return null;

  return (
    <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5 mb-4">
      <div className="text-sm font-semibold text-[#F8FAFC] mb-4">Agent Pipeline</div>
      <div className="relative pl-6">
        <div className="absolute left-[7px] top-0 bottom-0 w-0.5 bg-[#6366F1] opacity-35" />
        {steps.map((step, i) => (
          <div
            key={i}
            className="relative mb-4"
            style={{
              opacity: 0,
              animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease forwards',
              animationDelay: reduced ? '0ms' : `${i * 300}ms`,
            }}
          >
            <div className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-[#6366F1] flex items-center justify-center">
              <span className="text-white text-[8px] font-bold">✓</span>
            </div>
            <button
              onClick={() => setOpenIdx(openIdx === i ? null : i)}
              aria-label={`Toggle step ${i + 1}`}
              className="bg-transparent border-none p-0 text-left w-full cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm text-[#F8FAFC]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  Step {i + 1} — {step.tool}
                </span>
                <span className="text-[11px] text-[#22C55E]">✓</span>
                <ChevronDown size={12} color="#64748B" style={{
                  marginLeft: 'auto',
                  transform: openIdx === i ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.2s',
                }} />
              </div>
            </button>
            <div className="text-xs text-[#64748B] mt-0.5">{step.thought}</div>
            {openIdx === i && (
              <div className="bg-[#0A0A0F] rounded-lg px-3 py-2.5 text-[11px] max-h-48 overflow-auto mt-2"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                {JSON.stringify(step.result, null, 2).split('\n').map((line, li) => {
                  const km = line.match(/^(\s*)("[\w\s]+")\s*:/);
                  const vm = line.match(/:\s*(".*"|[\d.]+|true|false|null)/);
                  return (
                    <div key={li}>
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
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
