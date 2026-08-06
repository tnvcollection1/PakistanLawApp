// API client for PakistanLawApp
const API_BASE = process.env.REACT_APP_API_URL || "/api";

export async function searchCases(query, page = 1, limit = 20) {
  const res = await fetch(`${API_BASE}/search/caselaws?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Search failed");
  return res.json();
}

export async function getCaseDetail(caseId) {
  const res = await fetch(`${API_BASE}/case/${caseId}`);
  if (!res.ok) throw new Error("Case not found");
  return res.json();
}

export async function getCaseReferences(caseId) {
  const res = await fetch(`${API_BASE}/case/${caseId}/references`);
  if (!res.ok) throw new Error("References not found");
  return res.json();
}

export async function searchWithinCase(caseId, query) {
  const res = await fetch(`${API_BASE}/case/${caseId}/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error("Search within case failed");
  return res.json();
}

export async function getCases(page = 1, limit = 20) {
  const res = await fetch(`${API_BASE}/cases/list?page=${page}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to load cases");
  return res.json();
}

export async function getAnalytics() {
  const res = await fetch(`${API_BASE}/analytics/overview`);
  if (!res.ok) throw new Error("Analytics failed");
  return res.json();
}

export async function getPopularSections(limit = 50) {
  const res = await fetch(`${API_BASE}/section/popular?limit=${limit}`);
  if (!res.ok) throw new Error("Sections failed");
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function getCurrentUser() {
  const token = localStorage.getItem("token");
  if (!token) return null;
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return null;
  return res.json();
}
