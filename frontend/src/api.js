const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function handleJsonResponse(response) {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail || data?.message || 'Request failed';
    throw new Error(message);
  }
  return data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/documents`, {
    method: 'POST',
    body: formData,
  });
  return handleJsonResponse(response);
}

export async function getDocuments() {
  const response = await fetch(`${API_BASE}/documents`);
  return handleJsonResponse(response);
}

export async function getDocument(id) {
  const response = await fetch(`${API_BASE}/documents/${id}`);
  return handleJsonResponse(response);
}

export async function deleteDocument(id) {
  const response = await fetch(`${API_BASE}/documents/${id}`, {
    method: 'DELETE',
  });
  return handleJsonResponse(response);
}

export async function searchDocuments(query) {
  const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
  return handleJsonResponse(response);
}
