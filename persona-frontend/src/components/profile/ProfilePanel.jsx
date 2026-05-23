import { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, User, Share2 } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function Stars({ value }) {
  return (
    <div className="flex gap-0.5">
      {[1, 2, 3, 4, 5].map(i => {
        const fill = Math.min(1, Math.max(0, value - (i - 1)));
        return (
          <div key={i} className="relative w-4 h-4">
            <span className="text-[#1E1E2E] text-base leading-none">★</span>
            <span className="absolute top-0 left-0 overflow-hidden text-[#F59E0B] text-base leading-none" style={{ width: `${fill * 100}%` }}>★</span>
          </div>
        );
      })}
    </div>
  );
}

function ArcGauge({ value }) {
  const r = 28, cx = 36, cy = 36, stroke = 8;
  const circ = Math.PI * r;
  const dash = value * circ;
  return (
    <svg width="72" height="40" viewBox="0 0 72 40">
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke="#1E1E2E" strokeWidth={stroke} strokeLinecap="round" />
      <path d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`} fill="none" stroke="#F59E0B" strokeWidth={stroke} strokeLinecap="round"
        strokeDasharray={`${dash} ${circ}`} style={{ transition: reduced ? 'none' : 'stroke-dasharray 0.6s ease' }} />
    </svg>
  );
}

function ValueBar({ label, value, max, dominant, delay }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="mb-2">
      <div className="flex justify-between mb-1">
        <span className="text-xs text-[#64748B] capitalize">{label}</span>
        <span className="text-xs text-[#64748B]">{value}</span>
      </div>
      <div className="h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
        <div
          className="h-full rounded-sm"
          style={{
            background: dominant ? '#F59E0B' : 'rgba(99,102,241,0.6)',
            width: reduced ? `${pct}%` : '0%',
            transition: reduced ? 'none' : `width 0.6s ease ${delay}ms`,
          }}
          ref={el => { if (el && !reduced) setTimeout(() => { el.style.width = `${pct}%`; }, 50); }}
        />
      </div>
    </div>
  );
}

function buildPersonaNarrative(profile) {
  const name = profile.user_id.replace(/_/g, ' ');
  const mean = profile.rating_stats?.mean ?? 3;
  const raterType = mean >= 4.0 ? 'a generous rater' : mean >= 3.0 ? 'a neutral rater' : 'a critical rater';
  const keywords = Object.entries(profile.value_keywords ?? {}).sort((a, b) => b[1] - a[1]);
  const topKeyword = keywords[0]?.[0] ?? 'quality';
  const delta = profile.trajectory?.delta_rating ?? 0;
  const trajectory = delta > 0.1 ? 'has become increasingly positive over time'
    : delta < -0.1 ? 'has become more critical over time' : 'has been consistent over time';
  const cultural = profile.cultural_signals?.code_switching_detected ? ' who writes in Nigerian English' : '';
  const detail = (profile.stylometry?.avg_word_count ?? 0) > 50 ? 'detailed' : 'concise';
  return `${name} is ${raterType}${cultural} who cares deeply about ${topKeyword} quality. They write ${detail} reviews and ${trajectory}.`;
}

const NON_FOOD_KEYWORDS = ['movie', 'film', 'gym', 'hotel', 'shop', 'book', 'activity', 'park', 'spa'];

export default function ProfilePanel({ profile, loading, primaryDomain = null, queryText = '', pageContext = 'task-a' }) {
  const [shareCopied, setShareCopied] = useState(false);

  const handleShare = () => {
    const url = `${window.location.origin}${window.location.pathname}?demo=${profile.user_id}`;
    navigator.clipboard.writeText(url);
    setShareCopied(true);
    setTimeout(() => setShareCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
        <div className="flex gap-3 items-center mb-5">
          <div className="skeleton w-14 h-14 rounded-full shrink-0" />
          <div className="flex-1 flex flex-col gap-2">
            <div className="skeleton h-7 w-3/5" />
            <div className="skeleton h-3.5 w-2/5" />
          </div>
        </div>
        {[1, 2, 3, 4].map(i => <div key={i} className="skeleton h-3 mb-2.5" />)}
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5 flex flex-col items-center justify-center min-h-[200px] gap-3">
        <User size={32} color="#1E1E2E" />
        <span className="text-[#64748B] text-sm text-center">Profile will appear here after building.</span>
      </div>
    );
  }

  const { rating_stats, stylometry, value_keywords, trajectory, cultural_signals, user_id } = profile;
  const mean = rating_stats?.mean ?? 0;
  const isColdStart = rating_stats?.count === 0;
  const avatarBg = mean >= 4.0 ? '#22C55E' : mean >= 3.0 ? '#F59E0B' : '#EF4444';
  const raterLabel = mean >= 4.0 ? 'Generous Rater' : mean >= 3.0 ? 'Neutral Rater' : 'Harsh Rater';
  const raterColor = mean >= 4.0 ? '#22C55E' : mean >= 3.0 ? '#F59E0B' : '#EF4444';
  const initials = user_id ? user_id.slice(0, 2).toUpperCase() : 'U';
  const keywords = Object.entries(value_keywords ?? {}).slice(0, 4);
  const maxKw = Math.max(...keywords.map(([, v]) => v), 1);
  const dominantKw = keywords.reduce((a, b) => (b[1] > a[1] ? b : a), ['', 0])[0];
  const delta = trajectory?.delta_rating ?? 0;
  const TrendIcon = delta > 0.1 ? TrendingUp : delta < -0.1 ? TrendingDown : Minus;
  const trendColor = delta > 0.1 ? '#22C55E' : delta < -0.1 ? '#EF4444' : '#F59E0B';
  const showCultural = cultural_signals?.code_switching_detected || (cultural_signals?.nigerian_english_index ?? 0) > 0;
  const narrative = buildPersonaNarrative(profile);
  const isCrossDomain = pageContext === 'task-b' && primaryDomain
    && NON_FOOD_KEYWORDS.some(k => queryText.toLowerCase().includes(k));

  return (
    <div key={user_id} className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5 flex flex-col gap-5 relative">

      {/* Share button */}
      <div className="absolute top-4 right-4">
        <div className="relative">
          <button onClick={handleShare} aria-label="Copy shareable profile link"
            className="bg-transparent border-none cursor-pointer text-[#64748B] flex items-center">
            <Share2 size={14} />
          </button>
          {shareCopied && (
            <span className="absolute -top-7 right-0 whitespace-nowrap bg-[#13131A] border border-[#22C55E] rounded-md px-2 py-0.5 text-[11px] text-[#22C55E]">
              Link copied! ✓
            </span>
          )}
        </div>
      </div>

      {/* Persona Identity Card */}
      <div
        className="bg-[#1A1A2E] rounded-r-lg flex gap-2.5 items-start p-2.5"
        style={{
          borderLeft: '4px solid #F59E0B',
          opacity: 0,
          animation: reduced ? 'none' : 'fadeSlideIn 0.4s ease forwards',
        }}
      >
        <User size={16} color="#F59E0B" className="shrink-0 mt-0.5" />
        <div>
          <div className="text-[9px] text-[#64748B] uppercase tracking-widest mb-1">Persona</div>
          <p className="m-0 text-xs text-[#F8FAFC] italic leading-relaxed" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>
            {narrative}
          </p>
        </div>
      </div>

      {/* Identity */}
      <div className="flex gap-3.5 items-center">
        <div
          className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold text-[#0A0A0F] shrink-0"
          style={{ background: avatarBg }}
        >
          {initials}
        </div>
        <div>
          <div className="text-3xl font-bold text-[#F8FAFC] leading-none">{mean.toFixed(1)}</div>
          <Stars value={mean} />
          <div className="flex gap-2 mt-1.5 flex-wrap">
            <span className="rounded-full px-2.5 py-0.5 text-[11px] font-semibold" style={{ background: `${raterColor}20`, color: raterColor }}>
              {raterLabel}
            </span>
            {isColdStart
              ? <span className="bg-[rgba(99,102,241,0.15)] text-[#6366F1] rounded-full px-2.5 py-0.5 text-[11px] font-semibold">Cold-start profile</span>
              : <span className="text-[#64748B] text-xs">Based on {rating_stats.count} reviews</span>
            }
          </div>
          {isCrossDomain && (
            <div className="mt-1.5">
              <span
                title={`Transferring ${primaryDomain} preference axes to new domain`}
                className="bg-[rgba(245,158,11,0.1)] border border-[#F59E0B] rounded-full px-2.5 py-0.5 text-[11px] text-[#F59E0B] cursor-default"
              >
                ⚡ Cross-domain inference
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Value Keywords */}
      {keywords.length > 0 && (
        <div>
          <div className="text-[10px] text-[#64748B] uppercase tracking-widest mb-2.5">What they care about</div>
          {keywords.map(([kw, val], i) => (
            <ValueBar key={kw} label={kw} value={val} max={maxKw} dominant={kw === dominantKw} delay={i * 100} />
          ))}
        </div>
      )}

      {/* Writing Style */}
      <div>
        <div className="text-[10px] text-[#64748B] uppercase tracking-widest mb-2.5">Writing Style</div>
        <div className="flex gap-2.5">
          <div className="flex-1 bg-[#0A0A0F] rounded-lg p-2.5 border border-[#1E1E2E]">
            <div className="text-lg font-bold text-[#F8FAFC]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              ~{Math.round(stylometry?.avg_word_count ?? 0)}
            </div>
            <div className="text-[11px] text-[#64748B]">avg per review</div>
          </div>
          <div className="flex-1 bg-[#0A0A0F] rounded-lg p-2.5 border border-[#1E1E2E] flex flex-col items-center">
            <ArcGauge value={stylometry?.vocab_richness ?? 0} />
            <div className="text-lg font-bold text-[#F8FAFC] -mt-1" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
              {(stylometry?.vocab_richness ?? 0).toFixed(2)}
            </div>
            <div className="text-[11px] text-[#64748B]">vocab richness</div>
          </div>
        </div>
      </div>

      {/* Trajectory */}
      {trajectory && (
        <div>
          <div className="text-[10px] text-[#64748B] uppercase tracking-widest mb-2.5">Trajectory</div>
          <div className="flex items-center gap-2">
            <TrendIcon size={16} color={trendColor} />
            <span className="font-semibold text-sm" style={{ color: trendColor, fontFamily: 'JetBrains Mono, monospace' }}>
              {delta > 0 ? '+' : ''}{delta.toFixed(2)}
            </span>
            <span className="text-[#64748B] text-sm">rating trend</span>
          </div>
          <div className="text-[#64748B] text-xs mt-1">
            {(trajectory.delta_review_length ?? 0) > 0 ? 'Reviews getting longer' : 'Reviews getting shorter'}
          </div>
        </div>
      )}

      {/* Cultural Signals */}
      {showCultural && (
        <div
          className="border border-[#22C55E] rounded-xl p-3.5 bg-[#0D1F12] flex gap-3 items-start relative"
          style={{ animation: reduced ? 'none' : 'pulse-glow 2s ease-in-out infinite' }}
        >
          {cultural_signals?.code_switching_detected && (
            <span className="absolute top-2.5 right-2.5 border border-[#22C55E] rounded-full px-2 py-0.5 text-[10px] text-[#22C55E]">
              +Bonus Signal
            </span>
          )}
          <span className="text-2xl">🇳🇬</span>
          <div className="flex-1">
            <div className="text-[#22C55E] font-bold text-sm">Nigerian English detected</div>
            <div className="text-[#64748B] text-xs mb-2">Pidgin hits: {cultural_signals.pidgin_term_hits}</div>
            <div className="text-[11px] text-[#64748B] mb-1">Nigerian English Index</div>
            <div className="h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
              <div
                className="h-full bg-[#22C55E] rounded-sm"
                style={{
                  width: `${(cultural_signals.nigerian_english_index ?? 0) * 100}%`,
                  transition: reduced ? 'none' : 'width 0.6s ease',
                }}
              />
            </div>
            {cultural_signals?.code_switching_detected && (
              <div className="text-[11px] text-[#22C55E] italic mt-2">
                "Nigerian cultural context will be applied to all outputs"
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
