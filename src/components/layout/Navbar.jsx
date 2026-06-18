import Button from "../ui/Button.jsx";

export function Topbar({
  apiStatus,
  currentProjectId,
  onProjectChange,
  onRefresh,
  onLogout,
  projects = [],
  username = "Operator",
}) {
  return (
    <header className="dashboard-topbar">
      <label className="project-select">
        <span>Project</span>
        <select value={currentProjectId || ""} onChange={(event) => onProjectChange(event.target.value)}>
          <option value="">All projects</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </label>

      <div className="topbar-actions">
        <span className={`api-indicator ${apiStatus?.ok ? "online" : "offline"}`}>
          {apiStatus?.ok ? "API online" : "API offline"}
        </span>
        <span className="user-label">{username}</span>
        <Button size="sm" variant="ghost" onClick={onRefresh}>
          Refresh
        </Button>
        <Button size="sm" variant="ghost" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
}

export default Topbar;
