import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import AppShell from './components/layout/AppShell';
import { ToastProvider } from './components/layout/Toast';
import Landing from './pages/Landing';

const TaskA = lazy(() => import('./pages/TaskA'));
const TaskB = lazy(() => import('./pages/TaskB'));
const About = lazy(() => import('./pages/About'));

function PageLoader() {
  return (
    <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 12 }}>
      {[1, 2, 3].map(i => (
        <div key={i} className="skeleton" style={{ height: 16, borderRadius: 6, width: i === 2 ? '70%' : '100%' }} />
      ))}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<Landing />} />
            <Route path="/task-a" element={<Suspense fallback={<PageLoader />}><TaskA /></Suspense>} />
            <Route path="/task-b" element={<Suspense fallback={<PageLoader />}><TaskB /></Suspense>} />
            <Route path="/about" element={<Suspense fallback={<PageLoader />}><About /></Suspense>} />
          </Route>
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}
