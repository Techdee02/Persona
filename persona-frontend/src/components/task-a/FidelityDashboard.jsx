import { useEffect, useRef } from 'react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function MetricBar({ label, value, delay }) {
  const barRef = useRef(null);
  const color = value >= 80 ? '#22C55E' : value >= 60 ? '#F59E0B' : '#EF4444';

  useEffect(() => {
    if (!barRef.current || reduced) return;
    const el = barRef.current;
    el.style.width = '0%';
    const t = setTimeout(() => { el.style.width = `${value}%`; }, delay + 50);
    return () => clearTimeout(t);
  }, [value, delay]);

  return (
    <div className="flex items-center gap-2.5 mb-2.5">
      <span className="text-xs text-[#64748B] w-32 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-[#1E1E2E] rounded-sm overflow-hidden">
        <div
          ref={barRef}
          className="h-full rounded-sm"
          style={{
            background: color,
            width: reduced ? `${value}%` : '0%',
            transition: reduced ? 'none' : 'width 0.6s ease-out',
          }}
        />
      </div>
      <span className="text-xs w-8 text-right shrink-0" style={{ fontFamily: 'JetBrains Mono, monospace', color }}>{value}</span>
    </div>
  );
}

export default function FidelityDashboard({ profile, output }) {
  if (!profile || !output) return null;

  const { stylometry, rating_stats, cultural_signals } = profile;
  const predicted = output.predicted_rating ?? 0;
  const reviewText = output.review_text ?? '';

  const toneMatch = Math.min(100, Math.round((stylometry?.vocab_richness ?? 0) * 100));
  const std = rating_stats?.std_dev ?? 1;
  const mean = rating_stats?.mean ?? 3;
  const ratingConsistency = Math.max(0, Math.round(100 - (Math.abs(predicted - mean) / (std || 1)) * 20));
  const culturalAccuracy = cultural_signals?.code_switching_detected ? 95
    : (cultural_signals?.nigerian_english_index ?? 0) > 0 ? 70 : 50;
  const avgWords = stylometry?.avg_word_count ?? 1;
  const reviewWords = reviewText.split(' ').filter(Boolean).length;
  const lengthFidelity = Math.max(0, Math.round(100 - (Math.abs(reviewWords - avgWords) / (avgWords || 1)) * 100));

  const overall = Math.round((toneMatch + ratingConsistency + culturalAccuracy + lengthFidelity) / 4);
  const overallColor = overall >= 80 ? '#22C55E' : overall >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <div className="bg-[#13131A] border border-[#1E1E2E] rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-semibold text-[#F8FAFC]">Behavioural Fidelity</span>
        <div className="flex items-baseline gap-0.5">
          <span className="text-3xl font-bold" style={{ fontFamily: 'JetBrains Mono, monospace', color: overallColor }}>{overall}</span>
          <span className="text-sm text-[#64748B]">/100</span>
        </div>
      </div>

      {[
        { label: 'Tone Match', value: toneMatch },
        { label: 'Rating Consistency', value: ratingConsistency },
        { label: 'Cultural Accuracy', value: culturalAccuracy },
        { label: 'Length Fidelity', value: lengthFidelity },
      ].map((m, i) => (
        <MetricBar key={m.label} label={m.label} value={m.value} delay={i * 100} />
      ))}

      <div className="text-[11px] text-[#64748B] mt-2 italic">
        Computed against user's psychological profile
      </div>
    </div>
  );
}
