import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export default function RecommendationCard({ item, rank, animationDelay }) {
  const [open, setOpen] = useState(false);
  const categories = item.metadata?.categories?.split(', ').filter(Boolean) ?? [];
  const stars = item.metadata?.stars ?? 0;
  const name = item.metadata?.name ?? item.item_id;

  return (
    <div style={{
      background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 16,
      opacity: 0, animation: reduced ? 'none' : 'fadeSlideIn 0.35s ease forwards',
      animationDelay: reduced ? '0ms' : `${animationDelay}ms`,
    }}>
      {/* Top row */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <div style={{
          width: 26, height: 26, borderRadius: '50%', background: '#F59E0B',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700, color: '#0A0A0F', flexShrink: 0,
        }}>
          #{rank}
        </div>
        <div style={{ flex: 1, height: 6, background: '#1E1E2E', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{
            height: '100%', background: '#6366F1', borderRadius: 3,
            width: `${Math.min(1, Math.max(0, item.score)) * 100}%`,
            transition: reduced ? 'none' : 'width 0.6s ease',
          }} />
        </div>
      </div>

      {/* Name */}
      <div style={{ fontSize: 16, fontWeight: 600, color: '#F8FAFC', marginBottom: 6 }}>{name}</div>

      {/* Categories */}
      {categories.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 8 }}>
          {categories.map(cat => (
            <span key={cat} style={{
              background: '#0A0A0F', border: '1px solid #1E1E2E',
              borderRadius: 999, padding: '2px 8px', fontSize: 11, color: '#64748B',
            }}>
              {cat}
            </span>
          ))}
        </div>
      )}

      {/* Stars */}
      {stars > 0 && (
        <div style={{ fontSize: 13, color: '#F59E0B', marginBottom: 10 }}>
          {'★'.repeat(Math.round(stars))}{'☆'.repeat(5 - Math.round(stars))} {stars.toFixed(1)}
        </div>
      )}

      {/* Explanation accordion */}
      <button
        onClick={() => setOpen(o => !o)}
        aria-label="Toggle explanation"
        style={{
          width: '100%', background: 'none', border: 'none', padding: '6px 0 0',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          cursor: 'pointer', borderTop: '1px solid #1E1E2E',
        }}
      >
        <span style={{ fontSize: 12, color: '#64748B' }}>Explanation</span>
        <ChevronDown size={14} color="#64748B" style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
      </button>
      {open && (
        <div style={{
          background: '#0A0A0F', borderRadius: '0 0 8px 8px', padding: '10px 12px',
          borderLeft: '4px solid #6366F1', marginTop: 4,
          fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#64748B',
        }}>
          {item.explanation}
        </div>
      )}
    </div>
  );
}
