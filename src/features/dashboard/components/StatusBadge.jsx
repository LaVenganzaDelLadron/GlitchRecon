const statusClassMap = {
  approved: "success",
  completed: "success",
  done: "success",
  running: "running",
  queued: "running",
  pending: "warning",
  waiting: "warning",
  waiting_approval: "warning",
  failed: "danger",
  error: "danger",
  cancelled: "muted",
};

function normalizeStatus(status = "") {
  return String(status || "unknown").toLowerCase().replace(/\s+/g, "_");
}

export function getStatusTone(status) {
  return statusClassMap[normalizeStatus(status)] || "muted";
}

function StatusBadge({ status }) {
  const normalized = normalizeStatus(status);
  return <span className={`status-badge ${getStatusTone(status)}`}>{normalized.replace(/_/g, " ")}</span>;
}

export default StatusBadge;
