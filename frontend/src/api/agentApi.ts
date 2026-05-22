import type { UploadResponse, AgentRunRequest, AgentRunResponse } from '../types/agent';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function uploadExcel(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/files/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.text().catch(() => '');
    throw new Error(err || `上传失败: ${res.status}`);
  }

  return res.json();
}

export async function runAgent(payload: AgentRunRequest): Promise<AgentRunResponse> {
  const res = await fetch(`${API_BASE_URL}/api/agent/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.text().catch(() => '');
    throw new Error(err || `Agent 运行失败: ${res.status}`);
  }

  return res.json();
}

export function getDownloadUrl(downloadUrl: string): string {
  if (downloadUrl.startsWith('http')) return downloadUrl;
  return `${API_BASE_URL}${downloadUrl}`;
}
