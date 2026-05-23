import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { RotateCcw } from 'lucide-react';
import { useToast } from './Toast';

export default function AppShell() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const handleReset = () => {
    window.dispatchEvent(new CustomEvent('persona:reset'));
    navigate('/');
    showToast('Demo reset ✓', 'success');
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0A0A0F' }}>
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, height: 56, zIndex: 100,
        background: '#0A0A0F', borderBottom: '1px solid #1E1E2E',
        display: 'flex', alignItems: 'center', padding: '0 24px', gap: 24,
      }}>
        {/* Logo */}
        <button
          onClick={() => navigate('/')}
          aria-label="Go to home"
          style={{ background: 'none', border: 'none', display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}
        >
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <circle cx="14" cy="14" r="13" stroke="#F59E0B" strokeWidth="1.5" />
            <circle cx="14" cy="10" r="3" fill="#F59E0B" />
            <circle cx="8" cy="18" r="2" fill="#F59E0B" opacity="0.7" />
            <circle cx="20" cy="18" r="2" fill="#F59E0B" opacity="0.7" />
            <line x1="14" y1="13" x2="8" y2="18" stroke="#F59E0B" strokeWidth="1" opacity="0.5" />
            <line x1="14" y1="13" x2="20" y2="18" stroke="#F59E0B" strokeWidth="1" opacity="0.5" />
            <line x1="8" y1="18" x2="20" y2="18" stroke="#F59E0B" strokeWidth="1" opacity="0.3" />
          </svg>
          <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16, color: '#F8FAFC', letterSpacing: '0.08em' }}>
            PERSONA
          </span>
        </button>

        {/* Center nav */}
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: 8 }}>
          {[{ to: '/task-a', label: 'Task A' }, { to: '/task-b', label: 'Task B' }].map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                padding: '6px 18px', borderRadius: 999, fontSize: 14, fontWeight: 600,
                textDecoration: 'none',
                color: isActive ? '#F59E0B' : '#64748B',
                background: isActive ? 'rgba(245,158,11,0.08)' : 'transparent',
                boxShadow: isActive ? '0 2px 0 #F59E0B' : 'none',
                transition: 'all 0.2s',
              })}
            >
              {label}
            </NavLink>
          ))}
        </div>

        {/* Right */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <NavLink
            to="/about"
            style={({ isActive }) => ({
              fontSize: 14, textDecoration: 'none',
              color: isActive ? '#F8FAFC' : '#64748B',
              transition: 'color 0.2s',
            })}
          >
            About
          </NavLink>

          {/* Reset Demo button */}
          <button
            onClick={handleReset}
            aria-label="Reset demo"
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'none', border: '1px solid #1E1E2E', borderRadius: 8,
              color: '#64748B', fontSize: 12, padding: '6px 12px', cursor: 'pointer',
              transition: 'border-color 0.2s, color 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#6366F1'; e.currentTarget.style.color = '#F8FAFC'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#1E1E2E'; e.currentTarget.style.color = '#64748B'; }}
          >
            <RotateCcw size={12} />
            Reset Demo
          </button>

          <span style={{
            background: '#13131A', border: '1px solid #1E1E2E',
            borderRadius: 999, padding: '3px 10px',
            fontSize: 11, color: '#F59E0B', fontWeight: 600, letterSpacing: '0.04em',
          }}>
            DSN x BCT · Hackathon 3.0
          </span>
        </div>
      </nav>

      <div style={{ paddingTop: 56, minHeight: 'calc(100vh - 56px)' }}>
        <Outlet />
      </div>
    </div>
  );
}
