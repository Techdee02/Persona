import { createContext, useContext, useState, useCallback } from 'react';
import { X } from 'lucide-react';

const Ctx = createContext({ showToast: () => {} });

const BORDER = { error: '#EF4444', success: '#22C55E', warning: '#F59E0B' };
let _id = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => setToasts(t => t.filter(x => x.id !== id)), []);

  const showToast = useCallback((message, type) => {
    const id = ++_id;
    setToasts(t => [...t, { id, message, type }]);
    setTimeout(() => remove(id), 5000);
  }, [remove]);

  return (
    <Ctx.Provider value={{ showToast }}>
      {children}
      <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {toasts.map(toast => (
          <div
            key={toast.id}
            className="animate-fade-slide"
            style={{
              background: '#13131A', border: '1px solid #1E1E2E',
              borderLeft: `4px solid ${BORDER[toast.type]}`,
              borderRadius: 8, padding: '12px 16px',
              display: 'flex', alignItems: 'center', gap: 12,
              minWidth: 280, maxWidth: 380,
              boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
            }}
          >
            <span style={{ flex: 1, fontSize: 14, color: '#F8FAFC' }}>{toast.message}</span>
            <button
              aria-label="Close notification"
              onClick={() => remove(toast.id)}
              style={{ background: 'none', border: 'none', color: '#64748B', padding: 2, display: 'flex', cursor: 'pointer' }}
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>
    </Ctx.Provider>
  );
}

export function useToast() {
  return useContext(Ctx);
}
