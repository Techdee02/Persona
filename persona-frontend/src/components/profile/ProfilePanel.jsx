import { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, User, Share2 } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function Skeleton({ w = '100%', h = 16, style = {} }) {
  return <div className="skeleton" style={{ width: w, height: h, borderRadius: 6, ...style }} />;
}

function Stars({ value }) {
  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {[1, 2, 3, 4, 5].map(i => {
        const fill = Math.min(1, Math.max(0, value - (i - 1)));
        return (
          <div key={i} style={{ position: 'relative', width: 16, height: 16 }}>
            <span style={{ color: '#1E1E2E', fontSize: 16, lineHeight: 1 }}>★</span>
            <span style={{
              position: 'absolute', top: 0, left: 0, overflow: 'hidden',
              width: `${fill * 100}%`, color: '#F59E0B', fontSize: 16, lineHeight: 1,
            }}>★</span>
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
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 12, color: '#64748B', textTransform: 'capitalize' }}>{label}</span>
        <span style={{ fontSize: 12, color: '#64748B' }}>{value}</span>
      </div>
      <div style={{ height: 6, background: '#1E1E2E', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 3,
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
  const trajectory = delta > 0.1
    ? 'has become increasingly positive over time'
    : delta < -0.1
    ? 'has become more critical over time'
    : 'has been consistent over time';
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
      <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 20 }}>
          <Skeleton w={60} h={60} style={{ borderRadius: '50%' }} />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Skeleton w="60%" h={28} />
            <Skeleton w="40%" h={14} />
          </div>
        </div>
        {[1, 2, 3, 4].map(i => <Skeleton key={i} h={12} style={{ marginBottom: 10 }} />)}
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{
        background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20,
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        minHeight: 200, gap: 12,
      }}>
        <User size={32} color="#1E1E2E" />
        <span style={{ color: '#64748B', fontSize: 14, textAlign: 'center' }}>Profile will appear here after building.</span>
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
    <div key={user_id} style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20, display: 'flex', flexDirection: 'column', gap: 20, position: 'relative' }}>

      {/* Share button */}
      <div style={{ position: 'absolute', top: 16, right: 16 }}>
        <div style={{ position: 'relative' }}>
          <button
            onClick={handleShare}
            aria-label="Copy shareable profile link"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748B', display: 'flex', alignItems: 'center' }}
          >
            <Share2 size={14} />
          </button>
          {shareCopied && (
            <span style={{
              position: 'absolute', top: -28, right: 0, whiteSpace: 'nowrap',
              background: '#13131A', border: '1px solid #22C55E', borderRadius: 6,
              padding: '2px 8px', fontSize: 11, color: '#22C55E',
            }}>
              Link copied! ✓
            </span>
          )}
        </div>
      </div>

      {/* Feature 1: Persona Identity Card */}
      <div style={{
        background: '#1A1A2E', borderLeft: '4px solid #F59E0B', borderRadius: '0 8px 8px 0',
        padding: '10px 14px', display: 'flex', gap: 10, alignItems: 'flex-start',
        opacity: 0,
        animation: reduced ? 'none' : 'fadeSlideIn 0.4s ease forwards',
      }}>
        <User size={16} color="#F59E0B" style={{ flexShrink: 0, marginTop: 2 }} />
        <div>
          <div style={{ fontSize: 9, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 4 }}>Persona</div>
          <p style={{ margin: 0, fontSize: 12, color: '#F8FAFC', fontFamily: "'Space Grotesk', sans-serif", fontStyle: 'italic', lineHeight: 1.5 }}>
            {narrative}
          </p>
        </div>
      </div>

      {/* Identity */}
      <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
        <div style={{
          width: 60, height: 60, borderRadius: '50%', background: avatarBg,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 20, fontWeight: 700, color: '#0A0A0F', flexShrink: 0,
        }}>
          {initials}
        </div>
        <div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#F8FAFC', lineHeight: 1 }}>{mean.toFixed(1)}</div>
          <Stars value={mean} />
          <div style={{ display: 'flex', gap: 8, marginTop: 6, flexWrap: 'wrap' }}>
            <span style={{ background: `${raterColor}20`, color: raterColor, borderRadius: 999, padding: '2px 10px', fontSize: 11, fontWeight: 600 }}>
              {raterLabel}
            </span>
            {isColdStart
              ? <span style={{ background: 'rgba(99,102,241,0.15)', color: '#6366F1', borderRadius: 999, padding: '2px 10px', fontSize: 11, fontWeight: 600 }}>Cold-start profile</span>
              : <span style={{ color: '#64748B', fontSize: 12 }}>Based on {rating_stats.count} reviews</span>
            }
          </div>
          {/* Feature 6: Cross-Domain Badge */}
          {isCrossDomain && (
            <div style={{ marginTop: 6 }}>
              <span
                title={`Transferring ${primaryDomain} preference axes to new domain`}
                style={{
                  background: 'rgba(245,158,11,0.1)', border: '1px solid #F59E0B',
                  borderRadius: 999, padding: '2px 10px', fontSize: 11, color: '#F59E0B',
                  cursor: 'default',
                }}
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
          <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>What they care about</div>
          {keywords.map(([kw, val], i) => (
            <ValueBar key={kw} label={kw} value={val} max={maxKw} dominant={kw === dominantKw} delay={i * 100} />
          ))}
        </div>
      )}

      {/* Writing Style */}
      <div>
        <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Writing Style</div>
        <div style={{ display: 'flex', gap: 10 }}>
          <div style={{ flex: 1, background: '#0A0A0F', borderRadius: 8, padding: '10px 12px', border: '1px solid #1E1E2E' }}>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#F8FAFC', fontFamily: 'JetBrains Mono, monospace' }}>
              ~{Math.round(stylometry?.avg_word_count ?? 0)}
            </div>
            <div style={{ fontSize: 11, color: '#64748B' }}>avg per review</div>
          </div>
          <div style={{ flex: 1, background: '#0A0A0F', borderRadius: 8, padding: '10px 12px', border: '1px solid #1E1E2E', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <ArcGauge value={stylometry?.vocab_richness ?? 0} />
            <div style={{ fontSize: 18, fontWeight: 700, color: '#F8FAFC', fontFamily: 'JetBrains Mono, monospace', marginTop: -4 }}>
              {(stylometry?.vocab_richness ?? 0).toFixed(2)}
            </div>
            <div style={{ fontSize: 11, color: '#64748B' }}>vocab richness</div>
          </div>
        </div>
      </div>

      {/* Trajectory */}
      {trajectory && (
        <div>
          <div style={{ fontSize: 10, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Trajectory</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <TrendIcon size={16} color={trendColor} />
            <span style={{ color: trendColor, fontWeight: 600, fontSize: 14, fontFamily: 'JetBrains Mono, monospace' }}>
              {delta > 0 ? '+' : ''}{delta.toFixed(2)}
            </span>
            <span style={{ color: '#64748B', fontSize: 13 }}>rating trend</span>
          </div>
          <div style={{ color: '#64748B', fontSize: 12, marginTop: 4 }}>
            {(trajectory.delta_review_length ?? 0) > 0 ? 'Reviews getting longer' : 'Reviews getting shorter'}
          </div>
        </div>
      )}

      {/* Cultural Signals — Feature 11: Nigerian Bonus Callout */}
      {showCultural && (
        <div style={{
          border: '1px solid #22C55E', borderRadius: 10, padding: '12px 14px',
          background: '#0D1F12',
          boxShadow: reduced ? '0 0 12px rgba(34,197,94,0.15)' : undefined,
          animation: reduced ? 'none' : 'pulse-glow 2s ease-in-out infinite',
          display: 'flex', gap: 12, alignItems: 'flex-start', position: 'relative',
        }}>
          {cultural_signals?.code_switching_detected && (
            <span style={{
              position: 'absolute', top: 10, right: 10,
              background: 'transparent', border: '1px solid #22C55E',
              borderRadius: 999, padding: '1px 8px', fontSize: 10, color: '#22C55E',
            }}>
              +Bonus Signal
            </span>
          )}
          <span style={{ fontSize: 24 }}>🇳🇬</span>
          <div style={{ flex: 1 }}>
            <div style={{ color: '#22C55E', fontWeight: 700, fontSize: 13 }}>Nigerian English detected</div>
            <div style={{ color: '#64748B', fontSize: 12, marginBottom: 8 }}>
              Pidgin hits: {cultural_signals.pidgin_term_hits}
            </div>
            <div style={{ fontSize: 11, color: '#64748B', marginBottom: 4 }}>
              Nigerian English Index
            </div>
            <div style={{ height: 6, background: '#1E1E2E', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{
                height: '100%', background: '#22C55E', borderRadius: 3,
                width: `${(cultural_signals.nigerian_english_index ?? 0) * 100}%`,
                transition: reduced ? 'none' : 'width 0.6s ease',
              }} />
            </div>
            {cultural_signals?.code_switching_detected && (
              <div style={{ fontSize: 11, color: '#22C55E', fontStyle: 'italic', marginTop: 8 }}>
                "Nigerian cultural context will be applied to all outputs"
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
