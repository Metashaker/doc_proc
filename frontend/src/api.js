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

export async function getDocumentsByTag(tag) {
  const response = await fetch(`${API_BASE}/documents?tag=${encodeURIComponent(tag)}`);
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

export async function getTags() {
  const response = await fetch(`${API_BASE}/tags`);
  return handleJsonResponse(response);
}

export async function addTag(documentId, name) {
  const response = await fetch(`${API_BASE}/documents/${documentId}/tags`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name }),
  });
  return handleJsonResponse(response);
}

export async function removeTag(documentId, tagId) {
  const response = await fetch(`${API_BASE}/documents/${documentId}/tags/${tagId}`, {
    method: 'DELETE',
  });
  return handleJsonResponse(response);
}
