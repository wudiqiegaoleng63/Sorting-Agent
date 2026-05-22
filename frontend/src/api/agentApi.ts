import type { UploadResponse, AgentRunRequest, AgentRunResponse } from '../types/agent';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function uploadExcel(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/api/files/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Upload failed: ${res.status}`);
  }

  return res.json();
}

export async function runAgent(params: AgentRunRequest): Promise<AgentRunResponse> {
  const res = await fetch(`${BASE_URL}/api/agent/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `Agent run failed: ${res.status}`);
  }

  return res.json();
}
