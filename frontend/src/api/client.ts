import {
  ChatMessage,
  StrategySummary,
  EvaluationResults,
  DocumentInfo,
  TraceEvent,
} from '../types';

// In Docker (nginx) and local `vite dev`, the backend is reverse-proxied onto
// the same origin at /api, so a relative path works with zero configuration.
// For a split deployment (e.g. frontend on Vercel, backend on Render/a VM),
// there is no same-origin proxy, so the frontend needs the backend's full
// URL. Set VITE_API_BASE_URL (e.g. https://your-backend.onrender.com) as a
// Vercel project environment variable to point at it; leave it unset for
// Docker/local dev and this falls back to the old relative '/api' behavior.
const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, '')}/api`
  : '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function sendChatMessage(
  query: string,
  onTraceEvent?: (event: TraceEvent) => void
): Promise<any> {
  // Use SSE streaming endpoint for real-time trace events
  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder('utf-8');
  let finalResult: any = null;

  if (reader) {
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.type === 'trace_event' && onTraceEvent) {
              onTraceEvent(data.event);
            } else if (data.type === 'completed') {
              finalResult = data;
            }
          } catch (e) {
            console.error('Error parsing SSE event', e);
          }
        }
      }
    }
  }

  if (!finalResult) {
    // Fallback to sync endpoint
    const fallback = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    return fallback.json();
  }

  return finalResult;
}

export async function submitUserFeedback(
  runId: string,
  rating: number,
  comments?: string,
  query?: string,
  finalAnswer?: string
) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      run_id: runId,
      rating,
      comments,
      query,
      final_answer: finalAnswer,
    }),
  });
  return res.json();
}

export async function getStrategySummary(): Promise<StrategySummary> {
  const res = await fetch(`${API_BASE}/strategy/summary`);
  return res.json();
}

export async function getEvaluationResults(): Promise<EvaluationResults> {
  const res = await fetch(`${API_BASE}/evaluation/results`);
  return res.json();
}

export async function runBenchmarkEvaluation(maxQuestions: number = 5): Promise<EvaluationResults> {
  const res = await fetch(`${API_BASE}/evaluation/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ max_questions: maxQuestions }),
  });
  return res.json();
}

export async function getRetrievalAblations() {
  const res = await fetch(`${API_BASE}/evaluation/ablations`);
  return res.json();
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/documents`);
  return res.json();
}

export async function uploadDocument(file: File, title?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (title) formData.append('title', title);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}
