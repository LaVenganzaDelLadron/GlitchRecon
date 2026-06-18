import SidebarNav from "./Sidebar.jsx";
import Topbar from "./Navbar.jsx";

function DashboardLayout({
  activeRoute,
  apiStatus,
  children,
  currentProjectId,
  onLogout,
  onProjectChange,
  onRefresh,
  projects,
  username,
}) {
  return (
    <div className="dashboard-shell">
      <SidebarNav activeRoute={activeRoute} />
      <div className="dashboard-main">
        <Topbar
          apiStatus={apiStatus}
          currentProjectId={currentProjectId}
          onLogout={onLogout}
          onProjectChange={onProjectChange}
          onRefresh={onRefresh}
          projects={projects}
          username={username}
        />
        <main className="dashboard-content">{children}</main>
      </div>
    </div>
  );
}

export default DashboardLayout;
