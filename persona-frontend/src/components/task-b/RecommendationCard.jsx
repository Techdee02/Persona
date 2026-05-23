import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function StarRow({ stars }) {
  if (!stars) return null;
  const full  = Math.round(stars);
  const color = full >= 4 ? '#22C55E' : full >= 3 ? '#F59E0B' : '#EF4444';
  return (
    <div className="flex items-center gap-1 mb-2">
      <span style={{ color, fontSize: 13 }}>
        {'★'.repeat(full)}{'☆'.repeat(Math.max(0, 5 - full))}
      </span>
      <span className="text-xs" style={{ color, fontFamily: 'JetBrains Mono, monospace' }}>
        {Number(stars).toFixed(1)}
      </span>
    </div>
  );
}

export default function RecommendationCard({ item, rank, animationDelay }) {
  const [open, setOpen] = useState(false);

  const rawName      = item.metadata?.name;
  const categories   = item.metadata?.categories?.split(', ').filter(Boolean) ?? [];
  const stars        = item.metadata?.stars ?? 0;
  const reviewCount  = item.metadata?.review_count;
  const scorePct     = Math.round(Math.min(1, Math.max(0, item.score)) * 100);

  // Name: use metadata.name (review snippet after enrichment) or a clean fallback
  const isPreview = rawName && rawName.length > 20;
  const displayName = rawName ?? `Yelp Business · ${item.item_id.slice(0, 8)}`;

  return (
    <div
      className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-4"
      style={{
        opacity: 0,
        animation: reduced ? 'none' : 'fadeSlideIn 0.35s ease forwards',
        animationDelay: reduced ? '0ms' : `${animationDelay}ms`,
      }}
    >
      {/* Rank + score bar */}
      <div className="flex items-center gap-2.5 mb-3">
        <div className="w-6 h-6 rounded-full bg-[#F59E0B] flex items-center justify-center text-[11px] font-bold text-[#0A0A0F] shrink-0">
          #{rank}
        </div>
        <div className="flex-1 h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
          <div
            className="h-full bg-[#6366F1] rounded-sm"
            style={{
              width: `${scorePct}%`,
              transition: reduced ? 'none' : 'width 0.6s ease',
            }}
          />
        </div>
        <span
          className="text-[11px] shrink-0"
          style={{ fontFamily: 'JetBrains Mono, monospace', color: '#6366F1' }}
        >
          {scorePct}%
        </span>
      </div>

      {/* Business name / review preview */}
      {isPreview ? (
        <>
          <div className="text-[10px] text-[#64748B] uppercase tracking-widest mb-1">Review Preview</div>
          <div
            className="text-sm text-[#F8FAFC] leading-relaxed mb-2 italic"
            style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}
          >
            "{displayName}"
          </div>
        </>
      ) : (
        <div className="text-base font-semibold text-[#F8FAFC] mb-2">{displayName}</div>
      )}

      {/* Stars */}
      <StarRow stars={stars} />

      {/* Categories */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {categories.map(cat => (
            <span key={cat} className="bg-[#0A0A0F] border border-[#1E1E2E] rounded-full px-2 py-0.5 text-[11px] text-[#64748B]">
              {cat}
            </span>
          ))}
        </div>
      )}

      {/* Review count */}
      {reviewCount > 0 && (
        <div className="text-[11px] text-[#64748B] mb-2.5">
          {reviewCount} review{reviewCount !== 1 ? 's' : ''} in dataset
        </div>
      )}

      {/* Explanation */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Toggle explanation"
        className="w-full bg-transparent border-none pt-1.5 flex items-center justify-between cursor-pointer border-t border-[#1E1E2E]"
      >
        <span className="text-xs text-[#64748B]">Explanation</span>
        <ChevronDown
          size={14} color="#64748B"
          style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
        />
      </button>

      {open && (
        <div
          className="bg-[#0A0A0F] rounded-b-lg px-3 py-2.5 border-l-4 border-[#6366F1] mt-1 text-[11px] text-[#64748B]"
          style={{ fontFamily: 'JetBrains Mono, monospace' }}
        >
          {item.explanation}
        </div>
      )}
    </div>
  );
}
