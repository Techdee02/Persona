const BASE = import.meta.env.VITE_API_URL;

const ERROR_MAP = {
  400: 'Missing required fields. Please check your input.',
  422: 'Invalid input format.',
  500: 'Something went wrong. Please try again.',
};

function uuid() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);
}

async function request(path, init = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Trace-Id': uuid(),
    ...(init.headers ?? {}),
  };
  let res;
  try {
    res = await fetch(`${BASE}${path}`, { ...init, headers });
  } catch {
    throw new Error('API unavailable. Check your connection.');
  }
  if (!res.ok) {
    throw new Error(ERROR_MAP[res.status] ?? 'Something went wrong. Please try again.');
  }
  return res.json();
}

export function buildProfile(userId, records) {
  return request('/profile/build', { method: 'POST', body: JSON.stringify({ user_id: userId, records }) });
}

export function simulateTaskA(payload) {
  return request('/task-a/simulate', { method: 'POST', body: JSON.stringify(payload) });
}

export function getColdStartQuestions() {
  return request('/cold-start/questions');
}

export function answerColdStart(userId, answers) {
  return request('/cold-start/answer', { method: 'POST', body: JSON.stringify({ user_id: userId, answers }) });
}

export function recommend(payload) {
  return request('/task-b/recommend', { method: 'POST', body: JSON.stringify(payload) });
}

export function runAgent(payload) {
  return request('/task-b/agent', { method: 'POST', body: JSON.stringify(payload) });
}
