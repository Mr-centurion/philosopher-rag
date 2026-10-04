const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Health check failed:', err);
    return { status: 'offline' };
  }
}

export async function fetchThinkers() {
  const res = await fetch(`${API_BASE}/thinkers`);
  if (!res.ok) {
    throw new Error(`Failed to fetch thinkers: ${res.statusText}`);
  }
  return await res.json();
}

export async function sendQuery({ question, thinkers, sessionId }) {
  const res = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      thinkers: thinkers && thinkers.length > 0 ? thinkers : null,
      session_id: sessionId || 'default_session',
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to process query' }));
    throw new Error(errorData.detail || `Server error (${res.status})`);
  }

  return await res.json();
}

export async function fetchSessionHistory(sessionId) {
  const res = await fetch(`${API_BASE}/session/${sessionId}/history`);
  if (!res.ok) {
    throw new Error(`Failed to fetch history: ${res.statusText}`);
  }
  return await res.json();
}

export async function runEvaluation() {
  const res = await fetch(`${API_BASE}/evaluate`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to run evaluation: ${res.statusText}`);
  }
  return await res.json();
}
