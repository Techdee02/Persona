import { useState } from 'react';

export default function Tooltip({ text, children }) {
  const [visible, setVisible] = useState(false);
  return (
    <span
      style={{ position: 'relative', display: 'inline' }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span style={{
          position: 'absolute', bottom: '100%', left: '50%', transform: 'translateX(-50%)',
          marginBottom: 6, zIndex: 50, whiteSpace: 'nowrap',
          background: '#13131A', border: '1px solid #1E1E2E', borderRadius: 8,
          padding: '4px 8px', fontFamily: 'JetBrains Mono, monospace',
          fontSize: 11, color: '#F8FAFC', pointerEvents: 'none',
        }}>
          {text}
        </span>
      )}
    </span>
  );
}
