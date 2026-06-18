export const API_BASE_URL = "http://127.0.0.1:5000";

const TOKEN_KEY = "glitchrecon_token";

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_KEY) || "";
}

export function setStoredToken(token) {
  if (token) {
    window.localStorage.setItem(TOKEN_KEY, token);
    return;
  }

  window.localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const token = options.token ?? getStoredToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || "GET",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  const payload = await readJson(response);

  if (!response.ok) {
    const message = payload?.detail || payload?.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return payload ?? { message: "", data: null };
}

async function readJson(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error("Backend returned a non-JSON response");
  }
}

export const api = {
  health: () => request("/", { token: "" }),
  listProjects: () => request("/project/"),
  createProject: (body) => request("/project/", { method: "POST", body }),
  updateProject: (id, body) => request(`/project/${id}`, { method: "PUT", body }),
  listTargets: () => request("/target/"),
  createTarget: (body) => request("/target/", { method: "POST", body }),
  listScans: () => request("/scan/"),
  createScanPlan: (body) => request("/scan/plan", { method: "POST", body }),
  approveScan: (id) => request(`/scan/${id}/approve`, { method: "POST" }),
  runScan: (id) => request(`/scan/${id}/run`, { method: "POST" }),
  cancelScan: (id) => request(`/scan/${id}/cancel`, { method: "POST" }),
  getScanLogs: (id) => request(`/scan/${id}/logs`),
  getScanStatus: (id) => request(`/scan/${id}/status`),
  getScanChildren: (id) => request(`/scan/${id}/children`),
  listFindings: () => request("/finding/"),
  listReports: () => request("/report/"),
};
