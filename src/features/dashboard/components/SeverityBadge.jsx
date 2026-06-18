const severityTone = {
  critical: "critical",
  high: "high",
  medium: "medium",
  low: "low",
  info: "info",
};

function SeverityBadge({ severity = "info" }) {
  const normalized = String(severity || "info").toLowerCase();
  return <span className={`severity-badge ${severityTone[normalized] || "info"}`}>{normalized}</span>;
}

export default SeverityBadge;
