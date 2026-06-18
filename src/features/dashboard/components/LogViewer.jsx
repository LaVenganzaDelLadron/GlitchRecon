import { useEffect, useState } from "react";
import Loader from "../../../components/ui/Loader.jsx";
import { api } from "../../../services/api.js";

function stringifyLogs(data) {
  if (typeof data === "string") {
    return data;
  }

  if (data?.logs) {
    return data.logs;
  }

  if (data?.content) {
    return data.content;
  }

  return JSON.stringify(data ?? "", null, 2);
}

function LogViewer({ scanId }) {
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(Boolean(scanId));
  const [error, setError] = useState("");

  useEffect(() => {
    if (!scanId) {
      return undefined;
    }

    let active = true;

    async function loadLogs() {
      try {
        const result = await api.getScanLogs(scanId);
        if (active) {
          setLogs(stringifyLogs(result.data));
          setError("");
        }
      } catch (err) {
        if (active) {
          setError(err.message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadLogs();
    const timer = window.setInterval(loadLogs, 4000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [scanId]);

  if (!scanId) {
    return <div className="log-viewer empty">Select a scan to view logs.</div>;
  }

  if (loading) {
    return <Loader label="Loading logs" />;
  }

  return (
    <pre className="log-viewer">
      {error ? `Error: ${error}` : logs || "No log output yet."}
    </pre>
  );
}

export default LogViewer;
