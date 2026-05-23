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
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
      <span style={{ fontSize: 12, color: '#64748B', width: 130, flexShrink: 0 }}>{label}</span>
      <div style={{ flex: 1, height: 6, background: '#1E1E2E', borderRadius: 3, overflow: 'hidden' }}>
        <div
          ref={barRef}
          style={{
            height: '100%', borderRadius: 3, background: color,
            width: reduced ? `${value}%` : '0%',
            transition: reduced ? 'none' : 'width 0.6s ease-out',
          }}
        />
      </div>
      <span style={{ fontSize: 12, fontFamily: 'JetBrains Mono, monospace', color, width: 32, textAlign: 'right' }}>{value}</span>
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

  const culturalAccuracy = cultural_signals?.code_switching_detected
    ? 95
    : (cultural_signals?.nigerian_english_index ?? 0) > 0
    ? 70
    : 50;

  const avgWords = stylometry?.avg_word_count ?? 1;
  const reviewWords = reviewText.split(' ').filter(Boolean).length;
  const lengthFidelity = Math.max(0, Math.round(100 - (Math.abs(reviewWords - avgWords) / (avgWords || 1)) * 100));

  const overall = Math.round((toneMatch + ratingConsistency + culturalAccuracy + lengthFidelity) / 4);
  const overallColor = overall >= 80 ? '#22C55E' : overall >= 60 ? '#F59E0B' : '#EF4444';

  const metrics = [
    { label: 'Tone Match', value: toneMatch },
    { label: 'Rating Consistency', value: ratingConsistency },
    { label: 'Cultural Accuracy', value: culturalAccuracy },
    { label: 'Length Fidelity', value: lengthFidelity },
  ];

  return (
    <div style={{ background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 12, padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#F8FAFC' }}>Behavioural Fidelity</span>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
          <span style={{ fontSize: 28, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', color: overallColor }}>{overall}</span>
          <span style={{ fontSize: 13, color: '#64748B' }}>/100</span>
        </div>
      </div>

      {metrics.map((m, i) => (
        <MetricBar key={m.label} label={m.label} value={m.value} delay={i * 100} />
      ))}

      <div style={{ fontSize: 11, color: '#64748B', marginTop: 8, fontStyle: 'italic' }}>
        Computed against user's psychological profile
      </div>
    </div>
  );
}
