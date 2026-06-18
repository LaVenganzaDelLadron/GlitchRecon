import Card from "../../../components/shared/Card.jsx";

function ProjectCard({ project }) {
  return (
    <Card className="project-card">
      <h3>{project.name}</h3>
      <p>{project.description || "No description"}</p>
      <dl>
        <div>
          <dt>Scope</dt>
          <dd>{project.scope || "Not set"}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{project.status || "unknown"}</dd>
        </div>
      </dl>
    </Card>
  );
}

export default ProjectCard;
