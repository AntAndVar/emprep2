import type { Application, DocumentStatus, Draft } from '../types';

export class ApiError extends Error {
  constructor(message: string, public status: number, public currentApplication?: Application) { super(message); }
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } }); }
  catch { throw new ApiError('Could not reach the local API. Check that both servers are running and try again.', 0); }
  let body;
  try { body = await response.json(); }
  catch { throw new ApiError('The local API did not return data. Check the Python server and try again.', response.status); }
  if (!response.ok) throw new ApiError(body.error?.message ?? 'This change could not be saved.', response.status, body.currentApplication);
  return body;
}

export const api = {
  applications: (fail = false) => request<{ applications: Application[] }>(`/api/applications${fail ? '?fail=1' : ''}`),
  saveDraft: (id: string, draft: Draft, expectedVersion: number) => request<{ application: Application }>(`/api/applications/${encodeURIComponent(id)}/draft`, { method: 'PUT', body: JSON.stringify({ draft, expectedVersion }) }),
  reviewDocument: (id: string, documentId: string, status: DocumentStatus, comment: string, expectedVersion: number) => request<{ application: Application }>(`/api/applications/${encodeURIComponent(id)}/documents/${encodeURIComponent(documentId)}`, { method: 'PATCH', body: JSON.stringify({ status, comment, expectedVersion }) }),
  submit: (id: string, expectedVersion: number) => request<{ application: Application }>(`/api/applications/${encodeURIComponent(id)}/submit`, { method: 'POST', body: JSON.stringify({ expectedVersion }) }),
};
