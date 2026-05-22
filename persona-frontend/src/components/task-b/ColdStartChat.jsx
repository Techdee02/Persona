import { useState, useEffect } from 'react';
import { getColdStartQuestions, answerColdStart } from '../../lib/api';
import { useToast } from '../layout/Toast';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export default function ColdStartChat({ onProfileBuilt }) {
  const { showToast } = useToast();
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    getColdStartQuestions()
      .then(data => setQuestions(data.questions ?? []))
      .catch(e => showToast(e.message, 'error'))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (option) => {
    if (selected !== null) return;
    setSelected(option);
    const newAnswers = [...answers, { question_id: questions[current].id, answer: option }];
    setAnswers(newAnswers);

    setTimeout(() => {
      if (current + 1 < questions.length) {
        setCurrent(c => c + 1);
        setSelected(null);
      } else {
        setBuilding(true);
        answerColdStart('cold_start_user', newAnswers)
          .then(profile => {
            setDone(true);
            setTimeout(() => onProfileBuilt(profile), 1000);
          })
          .catch(e => {
            showToast(e.message || 'Failed to build profile. Try again.', 'error');
            setBuilding(false);
          });
      }
    }, 400);
  };

  if (loading) {
    return (
      <div style={{ padding: 16 }}>
        {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 14, marginBottom: 10, borderRadius: 6 }} />)}
      </div>
    );
  }

  if (done) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
        <div style={{ color: '#22C55E', fontWeight: 700, fontSize: 16 }}>Profile built! ✓</div>
      </div>
    );
  }

  if (building) {
    return (
      <div style={{ padding: 16 }}>
        <div style={{ color: '#64748B', fontSize: 13, marginBottom: 12 }}>Building your profile...</div>
        {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 12, marginBottom: 8, borderRadius: 6 }} />)}
      </div>
    );
  }

  if (!questions.length) {
    return <div style={{ color: '#64748B', fontSize: 13, padding: 16 }}>No questions available.</div>;
  }

  const q = questions[current];
  const progress = ((current) / questions.length) * 100;

  return (
    <div style={{ padding: 4 }}>
      {/* Progress */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 11, color: '#64748B' }}>Question {current + 1} of {questions.length}</span>
        </div>
        <div style={{ height: 4, background: '#1E1E2E', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{
            height: '100%', background: '#6366F1', borderRadius: 2,
            width: `${progress}%`, transition: reduced ? 'none' : 'width 0.4s ease',
          }} />
        </div>
      </div>

      {/* Bot bubble */}
      <div style={{
        background: '#13131A', border: '1px solid #1E1E2E',
        borderRadius: '0 12px 12px 12px', padding: '12px 14px',
        fontSize: 14, color: '#F8FAFC', marginBottom: 14,
        animation: reduced ? 'none' : 'fadeSlideIn 0.3s ease',
      }}>
        {q.question}
      </div>

      {/* Options */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {q.options.map(opt => {
          const isSelected = selected === opt;
          return (
            <button
              key={opt}
              onClick={() => handleSelect(opt)}
              disabled={selected !== null}
              style={{
                borderRadius: 999, padding: '8px 16px', fontSize: 13,
                border: `1px solid ${isSelected ? '#6366F1' : '#1E1E2E'}`,
                background: isSelected ? '#6366F1' : 'transparent',
                color: isSelected ? '#fff' : '#F8FAFC',
                cursor: selected !== null ? 'default' : 'pointer',
                display: 'flex', alignItems: 'center', gap: 6,
                transition: reduced ? 'none' : 'all 0.2s',
              }}
            >
              {isSelected && <span>✓</span>}
              {opt}
            </button>
          );
        })}
      </div>
    </div>
  );
}
