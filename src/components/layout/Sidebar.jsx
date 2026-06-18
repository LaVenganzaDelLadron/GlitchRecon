import Button from "../ui/Button.jsx";

export function SidebarNav({
  onAddProject,
  onClearSelection,
  onSelectProject,
  onSelectTarget,
  projects = [],
  selectedProjectId = "",
  selectedTargetId = "",
  targets = [],
}) {
  return (
    <aside className="dashboard-sidebar">
      <a className="dashboard-brand" href="#/overview" onClick={onClearSelection}>
        <span className="brand-mark">G</span>
        <span>GlitchRecon</span>
      </a>

      <div className="sidebar-section-header">
        <div>
          <p className="sidebar-kicker">Workspace</p>
          <h2>Projects</h2>
        </div>
        <Button
          aria-label="Add project"
          className="add-project-button"
          size="sm"
          title="Add project"
          variant="ghost"
          onClick={onAddProject}
        >
          <span aria-hidden="true">+</span>
        </Button>
      </div>

      <Button className="sidebar-reset" size="sm" variant="ghost" onClick={onClearSelection}>
        All projects
      </Button>

      <nav className="project-tree" aria-label="Projects and targets">
        {projects.length ? (
          projects.map((project) => {
            const projectTargets = targets.filter((target) => String(target.project_id) === String(project.id));
            const projectActive = String(selectedProjectId) === String(project.id) && !selectedTargetId;

            return (
              <section className="project-tree-card" key={project.id}>
                <button
                  className={`project-tree-project ${projectActive ? "active" : ""}`}
                  type="button"
                  onClick={() => onSelectProject(project.id)}
                >
                  <span className="project-tree-icon" aria-hidden="true">P</span>
                  <span className="project-tree-copy">
                    <strong>{project.name || `Project ${project.id}`}</strong>
                    <span>{project.scope || "No scope"}</span>
                  </span>
                  <small>{projectTargets.length}</small>
                </button>

                <div className="project-tree-targets">
                  {projectTargets.length ? (
                    projectTargets.map((target) => (
                      <button
                        className={String(selectedTargetId) === String(target.id) ? "active" : ""}
                        key={target.id}
                        type="button"
                        onClick={() => onSelectTarget(project.id, target.id)}
                      >
                        <span className="target-row-icon" aria-hidden="true">T</span>
                        <span>{target.value || `Target ${target.id}`}</span>
                        <small>{target.type || "target"}</small>
                      </button>
                    ))
                  ) : (
                    <p>No targets yet</p>
                  )}
                </div>
              </section>
            );
          })
        ) : (
          <p className="project-tree-empty">Create a project to begin.</p>
        )}
      </nav>
    </aside>
  );
}

export default SidebarNav;
