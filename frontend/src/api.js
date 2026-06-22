const BASE = "/api";

async function asJson(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export function listIndustries() {
  return fetch(`${BASE}/industries`).then(asJson);
}

export function uploadAndValidate(industry, files) {
  const form = new FormData();
  for (const [name, file] of Object.entries(files)) {
    if (file) form.append(name, file);
  }
  return fetch(`${BASE}/pipeline/upload?industry=${encodeURIComponent(industry)}`, {
    method: "POST",
    body: form,
  }).then(asJson);
}

export function startTraining(runId) {
  return fetch(`${BASE}/pipeline/train/${runId}`, { method: "POST" }).then(asJson);
}

export function getRunStatus(runId) {
  return fetch(`${BASE}/pipeline/status/${runId}`).then(asJson);
}

export function getMetrics(runId) {
  return fetch(`${BASE}/pipeline/metrics/${runId}`).then(asJson);
}

export function getEda(runId) {
  const q = runId ? `?run_id=${runId}` : "";
  return fetch(`${BASE}/pipeline/eda${q}`).then(asJson);
}

export function getPersonalized(customerId, runId) {
  const q = runId ? `?run_id=${runId}` : "";
  return fetch(`${BASE}/recommendations/personalized/${encodeURIComponent(customerId)}${q}`).then(asJson);
}

export function getFrequentlyBoughtTogether(productId, runId) {
  const q = runId ? `?run_id=${runId}` : "";
  return fetch(`${BASE}/recommendations/frequently-bought-together/${encodeURIComponent(productId)}${q}`).then(
    asJson
  );
}

export function getPopular(segment, runId) {
  const params = new URLSearchParams();
  if (segment) params.set("segment", segment);
  if (runId) params.set("run_id", runId);
  const q = params.toString() ? `?${params.toString()}` : "";
  return fetch(`${BASE}/recommendations/popular${q}`).then(asJson);
}

export function excelExportUrl(runId) {
  return `${BASE}/export/excel/${runId}`;
}
