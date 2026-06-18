const viteEnv = import.meta.env ?? {};

export const API_BASE_URL = viteEnv.VITE_API_BASE_URL ?? "";
export const BACKEND_ORIGIN = viteEnv.VITE_BACKEND_ORIGIN ?? "http://127.0.0.1:5000";

const TOKEN_KEY = "glitchrecon_token";

const withId = (basePath, id) => `${basePath}${encodeURIComponent(id)}`;

export const apiRoutes = {
  root: "/",
  docs: "/docs",
  openapi: "/openapi.json",
  redoc: "/redoc",
  auth: {
    register: "/auth/register",
    login: "/auth/login",
  },
  project: {
    list: "/project/",
    create: "/project/",
    detail: (projectId) => withId("/project/", projectId),
  },
  target: {
    list: "/target/",
    create: "/target/",
    detail: (targetId) => withId("/target/", targetId),
  },
  scan: {
    list: "/scan/",
    create: "/scan/",
    plan: "/scan/plan",
    detail: (scanId) => withId("/scan/", scanId),
    approve: (scanId) => `${withId("/scan/", scanId)}/approve`,
    run: (scanId) => `${withId("/scan/", scanId)}/run`,
    children: (scanId) => `${withId("/scan/", scanId)}/children`,
    status: (scanId) => `${withId("/scan/", scanId)}/status`,
    logs: (scanId) => `${withId("/scan/", scanId)}/logs`,
    cancel: (scanId) => `${withId("/scan/", scanId)}/cancel`,
  },
  report: {
    list: "/report/",
    create: "/report/",
    detail: (reportId) => withId("/report/", reportId),
  },
  finding: {
    list: "/finding/",
    create: "/finding/",
    detail: (findingId) => withId("/finding/", findingId),
  },
};

export function getBackendUrl(path) {
  return `${BACKEND_ORIGIN}${path}`;
}

export function getApiUrl(path) {
  return `${API_BASE_URL}${path}`;
}

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

export function getAuthTokenFromPayload(payload) {
  return (
    payload?.access_token ||
    payload?.token ||
    payload?.data?.access_token ||
    payload?.data?.token ||
    ""
  );
}

async function request(path, options = {}) {
  const token = options.token ?? getStoredToken();
  const response = await fetch(getApiUrl(path), {
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
  health: () => request(apiRoutes.root, { token: "" }),
  getOpenApi: () => request(apiRoutes.openapi, { token: "" }),

  register: (body) => request(apiRoutes.auth.register, { method: "POST", body, token: "" }),
  login: (body) => request(apiRoutes.auth.login, { method: "POST", body, token: "" }),

  listProjects: () => request(apiRoutes.project.list),
  createProject: (body) => request(apiRoutes.project.create, { method: "POST", body }),
  getProject: (id) => request(apiRoutes.project.detail(id)),
  updateProject: (id, body) => request(apiRoutes.project.detail(id), { method: "PUT", body }),
  deleteProject: (id) => request(apiRoutes.project.detail(id), { method: "DELETE" }),

  listTargets: () => request(apiRoutes.target.list),
  createTarget: (body) => request(apiRoutes.target.create, { method: "POST", body }),
  getTarget: (id) => request(apiRoutes.target.detail(id)),
  updateTarget: (id, body) => request(apiRoutes.target.detail(id), { method: "PUT", body }),
  deleteTarget: (id) => request(apiRoutes.target.detail(id), { method: "DELETE" }),

  listScans: () => request(apiRoutes.scan.list),
  createScan: (body) => request(apiRoutes.scan.create, { method: "POST", body }),
  createScanPlan: (body) => request(apiRoutes.scan.plan, { method: "POST", body }),
  getScan: (id) => request(apiRoutes.scan.detail(id)),
  updateScan: (id, body) => request(apiRoutes.scan.detail(id), { method: "PUT", body }),
  approveScan: (id) => request(apiRoutes.scan.approve(id), { method: "POST" }),
  runScan: (id) => request(apiRoutes.scan.run(id), { method: "POST" }),
  getScanChildren: (id) => request(apiRoutes.scan.children(id)),
  getScanStatus: (id) => request(apiRoutes.scan.status(id)),
  getScanLogs: (id) => request(apiRoutes.scan.logs(id)),
  cancelScan: (id) => request(apiRoutes.scan.cancel(id), { method: "POST" }),
  deleteScan: (id) => request(apiRoutes.scan.detail(id), { method: "DELETE" }),

  listReports: () => request(apiRoutes.report.list),
  createReport: (body) => request(apiRoutes.report.create, { method: "POST", body }),
  getReport: (id) => request(apiRoutes.report.detail(id)),
  updateReport: (id, body) => request(apiRoutes.report.detail(id), { method: "PUT", body }),
  deleteReport: (id) => request(apiRoutes.report.detail(id), { method: "DELETE" }),

  listFindings: () => request(apiRoutes.finding.list),
  createFinding: (body) => request(apiRoutes.finding.create, { method: "POST", body }),
  getFinding: (id) => request(apiRoutes.finding.detail(id)),
  updateFinding: (id, body) => request(apiRoutes.finding.detail(id), { method: "PUT", body }),
  deleteFinding: (id) => request(apiRoutes.finding.detail(id), { method: "DELETE" }),
};
