import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export default function RecommendationCard({ item, rank, animationDelay }) {
  const [open, setOpen] = useState(false);
  const categories = item.metadata?.categories?.split(', ').filter(Boolean) ?? [];
  const stars = item.metadata?.stars ?? 0;
  const name = item.metadata?.name ?? item.item_id;

  return (
    <div
      className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-4"
      style={{
        opacity: 0,
        animation: reduced ? 'none' : 'fadeSlideIn 0.35s ease forwards',
        animationDelay: reduced ? '0ms' : `${animationDelay}ms`,
      }}
    >
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-6 h-6 rounded-full bg-[#F59E0B] flex items-center justify-center text-[11px] font-bold text-[#0A0A0F] shrink-0">
          #{rank}
        </div>
        <div className="flex-1 h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
          <div
            className="h-full bg-[#6366F1] rounded-sm"
            style={{
              width: `${Math.min(1, Math.max(0, item.score)) * 100}%`,
              transition: reduced ? 'none' : 'width 0.6s ease',
            }}
          />
        </div>
      </div>

      <div className="text-base font-semibold text-[#F8FAFC] mb-1.5">{name}</div>

      {categories.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {categories.map(cat => (
            <span key={cat} className="bg-[#0A0A0F] border border-[#1E1E2E] rounded-full px-2 py-0.5 text-[11px] text-[#64748B]">
              {cat}
            </span>
          ))}
        </div>
      )}

      {stars > 0 && (
        <div className="text-sm text-[#F59E0B] mb-2.5">
          {'★'.repeat(Math.round(stars))}{'☆'.repeat(5 - Math.round(stars))} {stars.toFixed(1)}
        </div>
      )}

      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Toggle explanation"
        className="w-full bg-transparent border-none pt-1.5 flex items-center justify-between cursor-pointer border-t border-[#1E1E2E]"
      >
        <span className="text-xs text-[#64748B]">Explanation</span>
        <ChevronDown size={14} color="#64748B" style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
      </button>

      {open && (
        <div className="bg-[#0A0A0F] rounded-b-lg px-3 py-2.5 border-l-4 border-[#6366F1] mt-1 text-[11px] text-[#64748B]"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}>
          {item.explanation}
        </div>
      )}
    </div>
  );
}
