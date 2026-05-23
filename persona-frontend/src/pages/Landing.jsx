import { useNavigate } from 'react-router-dom';
import { Brain, Globe, Zap } from 'lucide-react';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function FlowNode({ label, color = '#F8FAFC' }) {
  return (
    <div className="bg-[#13131A] border border-[#1E1E2E] rounded-full px-4 py-1.5 text-xs font-semibold" style={{ color }}>
      {label}
    </div>
  );
}

function FlowArrow({ delay }) {
  return (
    <div className="flex items-center">
      <div
        className="w-10 h-px opacity-60"
        style={{
          background: 'linear-gradient(90deg, #1E1E2E, #6366F1)',
          animation: reduced ? 'none' : `pulse-opacity 2s ease-in-out ${delay}ms infinite`,
        }}
      />
      <div className="text-[#6366F1] text-sm opacity-60">›</div>
    </div>
  );
}

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-56px)] flex flex-col items-center justify-center px-4 sm:px-6 py-12">

      {/* Hero */}
      <div className="text-center max-w-2xl w-full px-2">
        <h1 className="font-bold tracking-tight leading-tight mb-2 text-[#F8FAFC]" style={{ fontSize: 'clamp(28px, 5vw, 52px)' }}>
          Understand who your users are.
        </h1>
        <h1 className="font-bold tracking-tight leading-tight mb-6 text-[#F59E0B]" style={{ fontSize: 'clamp(28px, 5vw, 52px)' }}>
          Before they tell you.
        </h1>
        <p className="text-[#64748B] leading-relaxed max-w-xl mx-auto text-sm sm:text-base md:text-lg">
          Persona builds psychological profiles from review history — predicting ratings, generating authentic reviews, and recommending places that actually fit.
        </p>
      </div>

      {/* Task cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-12 w-full max-w-3xl">
        {/* Task A */}
        <div className="bg-[#13131A] border border-[#1E1E2E] rounded-2xl p-6 md:p-8 flex flex-col gap-4">
          <div>
            <div className="text-lg md:text-xl font-bold text-[#F8FAFC] mb-2">Review Simulation</div>
            <div className="text-sm text-[#64748B] leading-relaxed">
              Predict how a user would rate and review any place based on their psychological profile.
            </div>
          </div>
          <button
            onClick={() => navigate('/task-a')}
            className="w-full mt-auto bg-[#F59E0B] text-[#0A0A0F] border-none rounded-lg py-3 font-bold text-sm cursor-pointer transition-opacity duration-200 hover:opacity-85"
          >
            Try Task A →
          </button>
        </div>

        {/* Task B */}
        <div className="bg-[#13131A] border border-[#1E1E2E] rounded-2xl p-6 md:p-8 flex flex-col gap-4">
          <div>
            <div className="text-lg md:text-xl font-bold text-[#F8FAFC] mb-2">Smart Recommendations</div>
            <div className="text-sm text-[#64748B] leading-relaxed">
              Find places that truly match a user's taste, writing style, and cultural context.
            </div>
          </div>
          <button
            onClick={() => navigate('/task-b')}
            className="w-full mt-auto bg-[#6366F1] text-white border-none rounded-lg py-3 font-bold text-sm cursor-pointer transition-opacity duration-200 hover:opacity-85"
          >
            Try Task B →
          </button>
        </div>
      </div>

      {/* Why This Matters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 w-full max-w-3xl">
        {[
          { icon: <Brain size={20} color="#6366F1" />, title: 'Behaviour', body: 'We model how users rate, write, and decide', accent: '#6366F1' },
          { icon: <Globe size={20} color="#F59E0B" />, title: 'Context', body: 'We detect cultural register and linguistic identity', accent: '#F59E0B' },
          { icon: <Zap size={20} color="#6366F1" />, title: 'Prediction', body: "We simulate what they'd say before they say it", accent: '#6366F1' },
        ].map(({ icon, title, body, accent }) => (
          <div key={title} className="text-center bg-[#13131A] border border-[#1E1E2E] rounded-xl p-4 md:p-5">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3"
              style={{ background: `${accent}18`, border: `1px solid ${accent}30` }}
            >
              {icon}
            </div>
            <div className="text-sm font-bold text-[#F8FAFC] mb-1">{title}</div>
            <div className="text-xs text-[#64748B] leading-relaxed">"{body}"</div>
          </div>
        ))}
      </div>

      {/* Flow diagram */}
      <div className="mt-12 flex items-center flex-wrap justify-center gap-0">
        <FlowNode label="Your Reviews" color="#64748B" />
        <FlowArrow delay={0} />
        <FlowNode label="Persona Engine" color="#F59E0B" />
        <FlowArrow delay={300} />
        <FlowNode label="Predictions" color="#6366F1" />
      </div>
    </div>
  );
}
