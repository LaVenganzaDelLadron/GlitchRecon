import { useState } from "react";
import Button from "../../../components/ui/Button.jsx";
import ProjectSelector from "./ProjectSelector.jsx";

function ScanPlanForm({ isSubmitting = false, onSubmit, projects, targets }) {
  const [form, setForm] = useState({
    goal: "",
    project_id: "",
    provider: "ollama",
    target_id: "",
  });

  const projectTargets = targets.filter((target) => String(target.project_id) === String(form.project_id));

  function updateField(name, value) {
    setForm((current) => ({
      ...current,
      [name]: value,
      ...(name === "project_id" ? { target_id: "" } : {}),
    }));
  }

  async function submitForm(event) {
    event.preventDefault();
    onSubmit({
      goal: form.goal,
      project_id: Number(form.project_id),
      provider: form.provider,
      target_id: Number(form.target_id),
    });
  }

  return (
    <form className="scan-plan-form" onSubmit={submitForm}>
      <ProjectSelector
        onChange={(value) => updateField("project_id", value)}
        projects={projects}
        value={form.project_id}
      />
      <label className="form-field">
        <span>Target</span>
        <select
          disabled={!form.project_id || isSubmitting}
          required
          value={form.target_id}
          onChange={(event) => updateField("target_id", event.target.value)}
        >
          <option value="">Select target</option>
          {projectTargets.map((target) => (
            <option key={target.id} value={target.id}>
              {target.value}
            </option>
          ))}
        </select>
      </label>
      <label className="form-field">
        <span>Provider</span>
        <select
          disabled={isSubmitting}
          value={form.provider}
          onChange={(event) => updateField("provider", event.target.value)}
        >
          <option value="ollama">ollama</option>
          <option value="openai">openai</option>
          <option value="anthropic">anthropic</option>
        </select>
      </label>
      <label className="form-field full">
        <span>Goal</span>
        <textarea
          placeholder="Perform authorized reconnaissance and summarize findings."
          disabled={isSubmitting}
          required
          rows="4"
          value={form.goal}
          onChange={(event) => updateField("goal", event.target.value)}
        ></textarea>
      </label>
      <Button className="full" disabled={isSubmitting} type="submit" variant="primary">
        {isSubmitting ? "Working..." : "Create scan plan"}
      </Button>
    </form>
  );
}

export default ScanPlanForm;
