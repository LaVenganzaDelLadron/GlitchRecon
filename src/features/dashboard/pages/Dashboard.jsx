import { useEffect, useState } from "react";
import DashboardLayout from "../../../components/layout/DashboardLayout.jsx";
import Card from "../../../components/shared/Card.jsx";
import StatCard from "../components/StatCard.jsx";
import { api, setStoredToken } from "../../../services/api.js";

function Dashboard() {
  const [apiStatus, setApiStatus] = useState({ ok: false });

  async function refreshStatus() {
    try {
      await api.health();
      setApiStatus({ ok: true });
    } catch {
      setApiStatus({ ok: false });
    }
  }

  function logout() {
    setStoredToken("");
    window.location.assign("/login");
  }

  useEffect(() => {
    refreshStatus();
  }, []);

  return (
    <DashboardLayout
      activeRoute="overview"
      apiStatus={apiStatus}
      currentProjectId=""
      onLogout={logout}
      onProjectChange={() => {}}
      onRefresh={refreshStatus}
      projects={[]}
      username="Operator"
    >
      <section className="dashboard-overview">
        <div className="dashboard-heading">
          <p className="eyebrow">Console</p>
          <h1>GlitchRecon dashboard</h1>
          <p>
            API route helpers are ready for projects, targets, scans, findings,
            and reports. Build the CRUD screens on top of this foundation.
          </p>
        </div>

        <div className="stat-grid">
          <StatCard label="Projects API" tone="success" value="Ready" />
          <StatCard label="Scan actions" tone="running" value="Mapped" />
          <StatCard label="Auth token" tone="neutral" value="Stored" />
        </div>

        <Card title="Backend routes">
          <div className="route-list">
            <a href="/docs">Docs</a>
            <a href="/redoc">Redoc</a>
            <a href="/openapi.json">OpenAPI JSON</a>
          </div>
        </Card>
      </section>
    </DashboardLayout>
  );
}

export default Dashboard;
