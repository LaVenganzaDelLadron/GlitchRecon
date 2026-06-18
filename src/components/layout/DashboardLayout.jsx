import SidebarNav from "./Sidebar.jsx";
import Topbar from "./Navbar.jsx";

function DashboardLayout({
  activeRoute,
  apiStatus,
  children,
  onAddProject,
  onClearSelection,
  onLogout,
  onRefresh,
  onSelectProject,
  onSelectTarget,
  projects,
  selectedProjectId,
  selectedTargetId,
  targets,
  username,
}) {
  return (
    <div className="dashboard-shell">
      <SidebarNav
        onAddProject={onAddProject}
        onClearSelection={onClearSelection}
        onSelectProject={onSelectProject}
        onSelectTarget={onSelectTarget}
        projects={projects}
        selectedProjectId={selectedProjectId}
        selectedTargetId={selectedTargetId}
        targets={targets}
      />
      <div className="dashboard-main">
        <Topbar
          activeRoute={activeRoute}
          apiStatus={apiStatus}
          onLogout={onLogout}
          onRefresh={onRefresh}
          username={username}
        />
        <main className="dashboard-content">{children}</main>
      </div>
    </div>
  );
}

export default DashboardLayout;
