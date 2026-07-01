// Thin wrapper around the backend HTTP API. All calls go through the Vite /api proxy.

const API = "/api";

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail);
  }
  return res.json();
}

export function getReports() {
  return fetch(`${API}/reports`).then(handle);
}

export function uploadPdf(file) {
  const form = new FormData();
  form.append("file", file);
  return fetch(`${API}/upload`, { method: "POST", body: form }).then(handle);
}

export function analyzeReport(reportId) {
  return fetch(`${API}/analyze/${reportId}`, { method: "POST" }).then(handle);
}

// --- Day 2: insights + Q&A ---

export function buildInsights() {
  return fetch(`${API}/insights/build`, { method: "POST" }).then(handle);
}

export function getInsights() {
  return fetch(`${API}/insights`).then(handle);
}

export function getExecutiveSummary() {
  return fetch(`${API}/insights/summary`, { method: "POST" }).then(handle);
}

export function askQuestion(question) {
  return fetch(`${API}/qa`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  }).then(handle);
}
