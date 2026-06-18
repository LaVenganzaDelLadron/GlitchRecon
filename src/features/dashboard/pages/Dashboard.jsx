import { useEffect, useState } from "react";
import DashboardLayout from "../../../components/layout/DashboardLayout.jsx";
import Card from "../../../components/shared/Card.jsx";
import EmptyState from "../../../components/shared/EmptyState.jsx";
import Button from "../../../components/ui/Button.jsx";
import Modal from "../../../components/ui/Modal.jsx";
import ConfirmActionModal from "../components/ConfirmActionModal.jsx";
import ScanPlanForm from "../components/ScanPlanForm.jsx";
import SeverityBadge from "../components/SeverityBadge.jsx";
import StatCard from "../components/StatCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";
import { api, setStoredToken } from "../../../services/api.js";

const validRoutes = new Set([
  "overview",
  "projects",
  "targets",
  "scans",
  "findings",
  "reports",
  "settings",
]);

const resourceConfigs = {
  projects: {
    title: "Projects",
    eyebrow: "Workspace",
    description: "Review authorized project scopes and operating status.",
    singular: "project",
    createLabel: "Create project",
    emptyMessage: "No projects found.",
    fields: [
      { name: "name", label: "Name", required: true },
      { name: "description", label: "Description", type: "textarea", required: true },
      { name: "scope", label: "Scope", required: true },
      { name: "status", label: "Status", required: true },
    ],
    create: api.createProject,
    update: api.updateProject,
    delete: api.deleteProject,
    renderCard: (project) => (
      <>
        <ResourceCardHeader title={project.name || "Untitled project"} meta={project.scope || "No scope"}>
          <StatusBadge status={project.status} />
        </ResourceCardHeader>
        <p>{project.description || "No description provided."}</p>
      </>
    ),
  },
  targets: {
    title: "Targets",
    eyebrow: "Scope",
    description: "Track domains, hosts, and other approved test targets.",
    singular: "target",
    createLabel: "Create target",
    emptyMessage: "No targets found.",
    fields: [
      { name: "project_id", label: "Project", type: "select", required: true, options: projectOptions },
      { name: "type", label: "Type", required: true },
      { name: "value", label: "Target", required: true },
      { name: "notes", label: "Notes", type: "textarea", required: true },
    ],
    create: api.createTarget,
    update: api.updateTarget,
    delete: api.deleteTarget,
    renderCard: (target, data) => (
      <>
        <ResourceCardHeader title={target.value || "Untitled target"} meta={projectName(data, target.project_id)}>
          <StatusBadge status={target.type || "target"} />
        </ResourceCardHeader>
        <p>{target.notes || "No notes provided."}</p>
      </>
    ),
  },
  scans: {
    title: "Scans",
    eyebrow: "Operations",
    description: "Monitor scan plans, execution state, and scanner assignments.",
    singular: "scan",
    createLabel: "Create scan",
    emptyMessage: "No scans found.",
    extraCreateActions: [
      { label: "Create plan", resource: "scanPlans", variant: "secondary" },
    ],
    workflowActionKeys: ["approve", "run", "cancel"],
    fields: [
      { name: "project_id", label: "Project", type: "select", required: true, options: projectOptions },
      { name: "target_id", label: "Target", type: "select", required: true, options: targetOptions },
      { name: "scanner", label: "Scanner", required: true },
      { name: "status", label: "Status", required: true },
      { name: "started_at", label: "Started at", type: "datetime-local" },
      { name: "finished_at", label: "Finished at", type: "datetime-local" },
    ],
    create: api.createScan,
    update: api.updateScan,
    delete: api.deleteScan,
    renderCard: (scan, data) => (
      <>
        <ResourceCardHeader title={scan.scanner || `Scan ${scan.id}`} meta={targetName(data, scan.target_id)}>
          <StatusBadge status={scan.status} />
        </ResourceCardHeader>
        <ResourceMeta
          items={[
            ["Project", projectName(data, scan.project_id)],
            ["Target", targetName(data, scan.target_id)],
            ["Started", scan.started_at || "Not started"],
          ]}
        />
      </>
    ),
  },
  findings: {
    title: "Findings",
    eyebrow: "Results",
    description: "Review vulnerability findings produced by completed scans.",
    singular: "finding",
    createLabel: "Create finding",
    emptyMessage: "No findings found.",
    fields: [
      { name: "scan_id", label: "Scan", type: "select", required: true, options: scanOptions },
      { name: "title", label: "Title", required: true },
      { name: "severity", label: "Severity", required: true },
      { name: "description", label: "Description", type: "textarea", required: true },
      { name: "evidence", label: "Evidence", type: "textarea", required: true },
      { name: "remediation", label: "Remediation", type: "textarea", required: true },
      { name: "cve", label: "CVE", required: true },
      { name: "cvss", label: "CVSS", required: true },
    ],
    create: api.createFinding,
    update: api.updateFinding,
    delete: api.deleteFinding,
    renderCard: (finding, data) => (
      <>
        <ResourceCardHeader title={finding.title || "Untitled finding"} meta={scanName(data, finding.scan_id)}>
          <SeverityBadge severity={finding.severity} />
        </ResourceCardHeader>
        <p>{finding.description || "No description provided."}</p>
        <ResourceMeta
          items={[
            ["CVE", finding.cve || "None"],
            ["CVSS", finding.cvss || "None"],
          ]}
        />
      </>
    ),
  },
  reports: {
    title: "Reports",
    eyebrow: "Exports",
    description: "Find generated report files and export metadata.",
    singular: "report",
    createLabel: "Create report",
    emptyMessage: "No reports found.",
    fields: [
      { name: "project_id", label: "Project", type: "select", required: true, options: projectOptions },
      { name: "name", label: "Name", required: true },
      { name: "format", label: "Format", required: true },
      { name: "path", label: "Path", required: true },
      { name: "generated_by", label: "Generated by", required: true },
    ],
    create: api.createReport,
    update: api.updateReport,
    delete: api.deleteReport,
    renderCard: (report, data) => (
      <>
        <ResourceCardHeader title={report.name || "Untitled report"} meta={projectName(data, report.project_id)}>
          <StatusBadge status={report.format || "report"} />
        </ResourceCardHeader>
        <ResourceMeta
          items={[
            ["Generated by", report.generated_by || "Unknown"],
            ["Path", report.path || "No path"],
          ]}
        />
      </>
    ),
  },
};

const workflowActions = {
  approve: {
    actionLabel: "Approve",
    message: (scan) => `Approve scan ${recordName(scan)} for execution?`,
    run: api.approveScan,
    title: "Approve scan",
  },
  run: {
    actionLabel: "Run",
    message: (scan) => `Run scan ${recordName(scan)} now?`,
    run: api.runScan,
    title: "Run scan",
  },
  cancel: {
    actionLabel: "Cancel scan",
    message: (scan) => `Cancel scan ${recordName(scan)}? This may stop active work.`,
    run: api.cancelScan,
    title: "Cancel scan",
  },
};

function projectOptions(data) {
  return data.projects.map((project) => ({ label: project.name || `Project ${project.id}`, value: project.id }));
}

function targetOptions(data, values) {
  const targets = values.project_id
    ? data.targets.filter((target) => String(target.project_id) === String(values.project_id))
    : data.targets;

  return targets.map((target) => ({ label: target.value || `Target ${target.id}`, value: target.id }));
}

function scanOptions(data) {
  return data.scans.map((scan) => ({
    label: `${scan.scanner || `Scan ${scan.id}`} - ${targetName(data, scan.target_id)}`,
    value: scan.id,
  }));
}

function projectName(data, projectId) {
  const project = data.projects.find((item) => String(item.id) === String(projectId));
  return project?.name || (projectId ? `Project ${projectId}` : "No project");
}

function targetName(data, targetId) {
  const target = data.targets.find((item) => String(item.id) === String(targetId));
  return target?.value || (targetId ? `Target ${targetId}` : "No target");
}

function scanName(data, scanId) {
  const scan = data.scans.find((item) => String(item.id) === String(scanId));
  if (!scan) {
    return scanId ? `Scan ${scanId}` : "No scan";
  }

  return scan.scanner ? `${scan.scanner} scan` : `Scan ${scan.id}`;
}

function getRouteFromHash() {
  const route = window.location.hash.replace(/^#\/?/, "") || "overview";
  return validRoutes.has(route) ? route : "overview";
}

function unwrapList(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  if (Array.isArray(payload?.items)) {
    return payload.items;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  return [];
}

function isEmptyListError(error) {
  return /no .+ found|empty/i.test(error?.message || "");
}

function getPayloadData(payload) {
  return payload?.data || payload;
}

function makeDefaultScanGoal(project, target) {
  return `Perform safe authorized reconnaissance for project "${project.name}" against target "${target.value}". Stay within scope: ${project.scope}. Summarize findings and evidence.`;
}

function recordName(record = {}) {
  return record.name || record.title || record.value || `#${record.id}`;
}

function formatDateTimeInput(value) {
  if (!value) {
    return "";
  }

  return String(value).slice(0, 16);
}

function getInitialFormValues(config, record) {
  return config.fields.reduce((values, field) => {
    const value = record?.[field.name];
    values[field.name] = field.type === "datetime-local" ? formatDateTimeInput(value) : value ?? "";
    return values;
  }, {});
}

function buildPayload(config, values) {
  return config.fields.reduce((payload, field) => {
    const value = values[field.name];

    if (field.type === "number" || field.name.endsWith("_id")) {
      payload[field.name] = Number(value);
      return payload;
    }

    if (field.type === "datetime-local") {
      payload[field.name] = value ? value : null;
      return payload;
    }

    payload[field.name] = value;
    return payload;
  }, {});
}

function filterDashboardData(data, selectedProjectId, selectedTargetId) {
  if (!selectedProjectId && !selectedTargetId) {
    return data;
  }

  const projects = selectedProjectId
    ? data.projects.filter((project) => String(project.id) === String(selectedProjectId))
    : data.projects;
  const targets = data.targets.filter((target) => {
    if (selectedTargetId) {
      return String(target.id) === String(selectedTargetId);
    }

    return selectedProjectId ? String(target.project_id) === String(selectedProjectId) : true;
  });
  const scans = data.scans.filter((scan) => {
    if (selectedTargetId) {
      return String(scan.target_id) === String(selectedTargetId);
    }

    return selectedProjectId ? String(scan.project_id) === String(selectedProjectId) : true;
  });
  const scanIds = new Set(scans.map((scan) => String(scan.id)));
  const findings = data.findings.filter((finding) => scanIds.has(String(finding.scan_id)));
  const reports = selectedProjectId
    ? data.reports.filter((report) => String(report.project_id) === String(selectedProjectId))
    : data.reports;

  return { findings, projects, reports, scans, targets };
}

function Dashboard() {
  const [activeRoute, setActiveRoute] = useState(getRouteFromHash);
  const [apiStatus, setApiStatus] = useState({ ok: false });
  const [dashboardData, setDashboardData] = useState({
    findings: [],
    projects: [],
    reports: [],
    scans: [],
    targets: [],
  });
  const [dataError, setDataError] = useState("");
  const [loadingData, setLoadingData] = useState(false);
  const [formModal, setFormModal] = useState(null);
  const [confirmModal, setConfirmModal] = useState(null);
  const [modalError, setModalError] = useState("");
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [selectedTargetId, setSelectedTargetId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [wizard, setWizard] = useState({
    error: "",
    isOpen: false,
    isSubmitting: false,
    project: {
      description: "",
      name: "",
      scope: "",
      status: "active",
    },
    step: "project",
    target: {
      notes: "",
      type: "url",
      value: "",
    },
  });

  async function refreshStatus() {
    try {
      await api.health();
      setApiStatus({ ok: true });
    } catch {
      setApiStatus({ ok: false });
    }
  }

  async function loadDashboardData() {
    setLoadingData(true);
    try {
      const results = await Promise.allSettled([
        api.listProjects(),
        api.listTargets(),
        api.listScans(),
        api.listFindings(),
        api.listReports(),
      ]);
      const [projects, targets, scans, findings, reports] = results.map((result) => (
        result.status === "fulfilled" || isEmptyListError(result.reason) ? result.value : null
      ));
      const failed = results.find((result) => result.status === "rejected" && !isEmptyListError(result.reason));

      setDashboardData({
        findings: unwrapList(findings),
        projects: unwrapList(projects),
        reports: unwrapList(reports),
        scans: unwrapList(scans),
        targets: unwrapList(targets),
      });

      setDataError(failed ? failed.reason.message : "");
    } catch (err) {
      setDataError(err.message);
    } finally {
      setLoadingData(false);
    }
  }

  async function refreshDashboard() {
    await Promise.all([refreshStatus(), loadDashboardData()]);
  }

  function openCreateModal(resource) {
    setModalError("");
    setFormModal({ mode: "create", resource, record: null });
  }

  function openEditModal(resource, record) {
    setModalError("");
    setFormModal({ mode: "edit", resource, record });
  }

  function openDeleteModal(resource, record) {
    setModalError("");
    setConfirmModal({ action: "delete", resource, record });
  }

  function openWorkflowModal(action, record) {
    setModalError("");
    setConfirmModal({ action, resource: "scans", record });
  }

  function selectProject(projectId) {
    setSelectedProjectId(String(projectId));
    setSelectedTargetId("");
  }

  function selectTarget(projectId, targetId) {
    setSelectedProjectId(String(projectId));
    setSelectedTargetId(String(targetId));
  }

  function clearSelection() {
    setSelectedProjectId("");
    setSelectedTargetId("");
  }

  function openWizard() {
    setWizard({
      error: "",
      isOpen: true,
      isSubmitting: false,
      project: {
        description: "",
        name: "",
        scope: "",
        status: "active",
      },
      step: "project",
      target: {
        notes: "",
        type: "url",
        value: "",
      },
    });
  }

  function closeWizard() {
    setWizard((current) => (current.isSubmitting ? current : { ...current, error: "", isOpen: false }));
  }

  function updateWizardSection(section, name, value) {
    setWizard((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [name]: value,
      },
    }));
  }

  function advanceWizard() {
    setWizard((current) => ({ ...current, error: "", step: "target" }));
  }

  async function finishWizard() {
    setWizard((current) => ({ ...current, error: "", isSubmitting: true }));

    try {
      const projectResult = await api.createProject(wizard.project);
      const project = getPayloadData(projectResult);
      const targetResult = await api.createTarget({
        ...wizard.target,
        project_id: project.id,
      });
      const target = getPayloadData(targetResult);
      const scanPlanResult = await api.createScanPlan({
        goal: makeDefaultScanGoal(project, target),
        project_id: project.id,
        provider: "ollama",
        target_id: target.id,
      });
      const scan = getPayloadData(scanPlanResult);

      await api.approveScan(scan.id);
      await loadDashboardData();
      setSelectedProjectId(String(project.id));
      setSelectedTargetId(String(target.id));
      setWizard((current) => ({ ...current, error: "", isOpen: false, isSubmitting: false }));
      window.location.hash = "#/scans";
    } catch (err) {
      setWizard((current) => ({ ...current, error: err.message, isSubmitting: false }));
    }
  }

  function closeModals() {
    if (submitting) {
      return;
    }

    setFormModal(null);
    setConfirmModal(null);
    setModalError("");
  }

  async function submitForm(values) {
    if (!formModal) {
      return;
    }

    setSubmitting(true);
    setModalError("");

    try {
      if (formModal.resource === "scanPlans") {
        await api.createScanPlan(values);
      } else {
        const config = resourceConfigs[formModal.resource];
        const payload = buildPayload(config, values);

        if (formModal.mode === "create") {
          await config.create(payload);
        } else {
          await config.update(formModal.record.id, payload);
        }
      }

      await loadDashboardData();
      setFormModal(null);
    } catch (err) {
      setModalError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function confirmAction() {
    if (!confirmModal) {
      return;
    }

    setSubmitting(true);
    setModalError("");

    try {
      if (confirmModal.action === "delete") {
        await resourceConfigs[confirmModal.resource].delete(confirmModal.record.id);
      } else {
        await workflowActions[confirmModal.action].run(confirmModal.record.id);
      }

      await loadDashboardData();
      setConfirmModal(null);
    } catch (err) {
      setModalError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function logout() {
    setStoredToken("");
    window.location.assign("/login");
  }

  useEffect(() => {
    function syncRoute() {
      setActiveRoute(getRouteFromHash());
    }

    syncRoute();
    window.addEventListener("hashchange", syncRoute);

    return () => {
      window.removeEventListener("hashchange", syncRoute);
    };
  }, []);

  useEffect(() => {
    refreshDashboard();
  }, []);

  const filteredData = filterDashboardData(dashboardData, selectedProjectId, selectedTargetId);
  const routeContext = {
    data: filteredData,
    loadingData,
    openCreateModal,
    openDeleteModal,
    openEditModal,
    openWorkflowModal,
  };

  return (
    <DashboardLayout
      activeRoute={activeRoute}
      apiStatus={apiStatus}
      onAddProject={openWizard}
      onClearSelection={clearSelection}
      onLogout={logout}
      onRefresh={refreshDashboard}
      onSelectProject={selectProject}
      onSelectTarget={selectTarget}
      projects={dashboardData.projects}
      selectedProjectId={selectedProjectId}
      selectedTargetId={selectedTargetId}
      targets={dashboardData.targets}
      username="Operator"
    >
      {dataError ? <p className="auth-alert error">{dataError}</p> : null}
      {renderDashboardRoute(activeRoute, routeContext)}
      <DashboardFormModal
        data={dashboardData}
        error={modalError}
        formModal={formModal}
        isSubmitting={submitting}
        onCancel={closeModals}
        onSubmit={submitForm}
      />
      <DashboardConfirmModal
        confirmModal={confirmModal}
        error={modalError}
        isSubmitting={submitting}
        onCancel={closeModals}
        onConfirm={confirmAction}
      />
      <ProjectTargetWizard
        error={wizard.error}
        isOpen={wizard.isOpen}
        isSubmitting={wizard.isSubmitting}
        onCancel={closeWizard}
        onFinish={finishWizard}
        onNext={advanceWizard}
        onUpdate={updateWizardSection}
        project={wizard.project}
        step={wizard.step}
        target={wizard.target}
      />
    </DashboardLayout>
  );
}

function renderDashboardRoute(activeRoute, context) {
  const { data, loadingData } = context;

  if (resourceConfigs[activeRoute]) {
    return <ResourceSection context={context} resourceKey={activeRoute} />;
  }

  if (activeRoute === "settings") {
    return (
      <DashboardSection eyebrow="System" title="Settings" description="Useful backend references and console actions.">
        <Card title="Backend routes">
          <div className="route-list">
            <a href="/docs">Docs</a>
            <a href="/redoc">Redoc</a>
            <a href="/openapi.json">OpenAPI JSON</a>
          </div>
        </Card>
      </DashboardSection>
    );
  }

  return (
    <section className="dashboard-overview">
      <div className="dashboard-heading">
        <p className="eyebrow">Console</p>
        <h1>GlitchRecon dashboard</h1>
        <p>
          Use the sidebar to open projects, targets, scans, findings, reports,
          and settings without leaving the dashboard shell.
        </p>
      </div>

      <div className="stat-grid">
        <StatCard label="Projects" tone="success" value={data.projects.length} />
        <StatCard label="Targets" tone="running" value={data.targets.length} />
        <StatCard label="Scans" tone="neutral" value={data.scans.length} />
      </div>

      {!loadingData && !data.projects.length && !data.targets.length && !data.scans.length ? (
        <EmptyState
          message="Create projects, targets, and scans through the dashboard actions to populate the console."
          title="No dashboard records yet"
        />
      ) : null}
    </section>
  );
}

function ResourceSection({ context, resourceKey }) {
  const { data, loadingData, openCreateModal, openDeleteModal, openEditModal, openWorkflowModal } = context;
  const config = resourceConfigs[resourceKey];
  const createButtons = (
    <>
      <Button onClick={() => openCreateModal(resourceKey)} variant="primary">
        {config.createLabel}
      </Button>
      {(config.extraCreateActions || []).map((action) => (
        <Button
          key={action.resource}
          onClick={() => openCreateModal(action.resource)}
          variant={action.variant || "secondary"}
        >
          {action.label}
        </Button>
      ))}
    </>
  );

  return (
    <DashboardSection
      action={createButtons}
      eyebrow={config.eyebrow}
      title={config.title}
      description={config.description}
    >
      <ResourceCardList
        actions={(record) => (
          <ResourceActions
            config={config}
            onDelete={() => openDeleteModal(resourceKey, record)}
            onEdit={() => openEditModal(resourceKey, record)}
            onWorkflow={(action) => openWorkflowModal(action, record)}
          />
        )}
        emptyAction={<div className="section-actions">{createButtons}</div>}
        emptyMessage={loadingData ? `Loading ${config.title.toLowerCase()}...` : config.emptyMessage}
        items={data[resourceKey]}
        renderCard={(record) => config.renderCard(record, data)}
      />
    </DashboardSection>
  );
}

function ResourceActions({ config, onDelete, onEdit, onWorkflow }) {
  return (
    <TableActions>
      <Button size="sm" variant="ghost" onClick={onEdit}>Edit</Button>
      {(config.workflowActionKeys || []).map((key) => (
        <Button key={key} size="sm" variant="ghost" onClick={() => onWorkflow(key)}>
          {workflowActions[key].actionLabel}
        </Button>
      ))}
      <Button size="sm" variant="ghost" onClick={onDelete}>Delete</Button>
    </TableActions>
  );
}

function DashboardSection({ action, children, description, eyebrow, title }) {
  return (
    <section className="dashboard-overview">
      <div className="dashboard-heading-row">
        <div className="dashboard-heading">
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
        {action ? <div className="section-actions">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}

function TableActions({ children }) {
  return <div className="table-actions">{children}</div>;
}

function ResourceCardList({ actions, emptyAction, emptyMessage, items, renderCard }) {
  if (!items.length) {
    return <EmptyState action={emptyAction} message={emptyMessage} />;
  }

  return (
    <div className="resource-card-grid">
      {items.map((item, index) => (
        <article className="resource-card" key={item.id ?? index}>
          <div className="resource-card-body">{renderCard(item)}</div>
          {actions ? <footer className="resource-card-actions">{actions(item)}</footer> : null}
        </article>
      ))}
    </div>
  );
}

function ResourceCardHeader({ children, meta, title }) {
  return (
    <header className="resource-card-header">
      <div>
        <h2>{title}</h2>
        <span>{meta}</span>
      </div>
      {children}
    </header>
  );
}

function ResourceMeta({ items }) {
  return (
    <dl className="resource-meta">
      {items.map(([label, value]) => (
        <div key={label}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function DashboardFormModal({ data, error, formModal, isSubmitting, onCancel, onSubmit }) {
  if (!formModal) {
    return null;
  }

  if (formModal.resource === "scanPlans") {
    return (
      <Modal isOpen onClose={onCancel} title="Create scan plan">
        <div className="modal-body">
          {error ? <p className="auth-alert error">{error}</p> : null}
          <ScanPlanForm
            isSubmitting={isSubmitting}
            onSubmit={onSubmit}
            projects={data.projects}
            targets={data.targets}
          />
        </div>
      </Modal>
    );
  }

  const config = resourceConfigs[formModal.resource];
  const title = `${formModal.mode === "create" ? "Create" : "Edit"} ${config.singular}`;

  return (
    <Modal isOpen onClose={onCancel} title={title}>
      <RecordForm
        config={config}
        data={data}
        error={error}
        isSubmitting={isSubmitting}
        mode={formModal.mode}
        onCancel={onCancel}
        onSubmit={onSubmit}
        record={formModal.record}
      />
    </Modal>
  );
}

function RecordForm({ config, data, error, isSubmitting, mode, onCancel, onSubmit, record }) {
  const [values, setValues] = useState(() => getInitialFormValues(config, record));

  useEffect(() => {
    setValues(getInitialFormValues(config, record));
  }, [config, record]);

  function updateValue(name, value) {
    setValues((current) => ({
      ...current,
      [name]: value,
      ...(name === "project_id" && "target_id" in current ? { target_id: "" } : {}),
    }));
  }

  async function submit(event) {
    event.preventDefault();
    await onSubmit(values);
  }

  return (
    <form className="record-form" onSubmit={submit}>
      <div className="modal-body">
        {config.fields.map((field) => (
          <FormField
            data={data}
            field={field}
            isSubmitting={isSubmitting}
            key={field.name}
            onChange={(value) => updateValue(field.name, value)}
            values={values}
          />
        ))}
        {error ? <p className="auth-alert error full">{error}</p> : null}
      </div>
      <footer className="modal-actions">
        <Button disabled={isSubmitting} variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
        <Button disabled={isSubmitting} type="submit" variant="primary">
          {isSubmitting ? "Working..." : mode === "create" ? `Create ${config.singular}` : `Save ${config.singular}`}
        </Button>
      </footer>
    </form>
  );
}

function FormField({ data, field, isSubmitting, onChange, values }) {
  const value = values[field.name] ?? "";
  const commonProps = {
    disabled: isSubmitting,
    id: `field-${field.name}`,
    name: field.name,
    onChange: (event) => onChange(event.target.value),
    required: field.required,
    value,
  };

  if (field.type === "textarea") {
    return (
      <label className="form-field full" htmlFor={commonProps.id}>
        <span>{field.label}</span>
        <textarea {...commonProps} rows="4" />
      </label>
    );
  }

  if (field.type === "select") {
    const options = field.options(data, values);

    return (
      <label className="form-field" htmlFor={commonProps.id}>
        <span>{field.label}</span>
        <select {...commonProps}>
          <option value="">Select {field.label.toLowerCase()}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    );
  }

  return (
    <label className="form-field" htmlFor={commonProps.id}>
      <span>{field.label}</span>
      <input {...commonProps} type={field.type || "text"} />
    </label>
  );
}

function ProjectTargetWizard({
  error,
  isOpen,
  isSubmitting,
  onCancel,
  onFinish,
  onNext,
  onUpdate,
  project,
  step,
  target,
}) {
  if (!isOpen) {
    return null;
  }

  function updateProject(name, value) {
    onUpdate("project", name, value);
  }

  function updateTarget(name, value) {
    onUpdate("target", name, value);
  }

  function submitProject(event) {
    event.preventDefault();
    onNext();
  }

  function submitTarget(event) {
    event.preventDefault();
    onFinish();
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onCancel}
      title={step === "project" ? "Add project" : "Add target"}
    >
      {step === "project" ? (
        <form className="record-form" onSubmit={submitProject}>
          <div className="modal-body">
            <label className="form-field">
              <span>Name</span>
              <input
                disabled={isSubmitting}
                required
                value={project.name}
                onChange={(event) => updateProject("name", event.target.value)}
              />
            </label>
            <label className="form-field">
              <span>Status</span>
              <input
                disabled={isSubmitting}
                required
                value={project.status}
                onChange={(event) => updateProject("status", event.target.value)}
              />
            </label>
            <label className="form-field full">
              <span>Scope</span>
              <input
                disabled={isSubmitting}
                required
                value={project.scope}
                onChange={(event) => updateProject("scope", event.target.value)}
              />
            </label>
            <label className="form-field full">
              <span>Description</span>
              <textarea
                disabled={isSubmitting}
                required
                rows="4"
                value={project.description}
                onChange={(event) => updateProject("description", event.target.value)}
              />
            </label>
            {error ? <p className="auth-alert error full">{error}</p> : null}
          </div>
          <footer className="modal-actions">
            <Button disabled={isSubmitting} variant="ghost" onClick={onCancel}>
              Cancel
            </Button>
            <Button disabled={isSubmitting} type="submit" variant="primary">
              Next
            </Button>
          </footer>
        </form>
      ) : (
        <form className="record-form" onSubmit={submitTarget}>
          <div className="modal-body">
            <label className="form-field">
              <span>Type</span>
              <input
                disabled={isSubmitting}
                required
                value={target.type}
                onChange={(event) => updateTarget("type", event.target.value)}
              />
            </label>
            <label className="form-field">
              <span>Target</span>
              <input
                disabled={isSubmitting}
                required
                value={target.value}
                onChange={(event) => updateTarget("value", event.target.value)}
              />
            </label>
            <label className="form-field full">
              <span>Notes</span>
              <textarea
                disabled={isSubmitting}
                required
                rows="4"
                value={target.notes}
                onChange={(event) => updateTarget("notes", event.target.value)}
              />
            </label>
            {error ? <p className="auth-alert error full">{error}</p> : null}
          </div>
          <footer className="modal-actions">
            <Button disabled={isSubmitting} variant="ghost" onClick={onCancel}>
              Cancel
            </Button>
            <Button disabled={isSubmitting} type="submit" variant="primary">
              {isSubmitting ? "Working..." : "Finish"}
            </Button>
          </footer>
        </form>
      )}
    </Modal>
  );
}

function DashboardConfirmModal({ confirmModal, error, isSubmitting, onCancel, onConfirm }) {
  if (!confirmModal) {
    return null;
  }

  if (confirmModal.action === "delete") {
    const config = resourceConfigs[confirmModal.resource];

    return (
      <ConfirmActionModal
        actionLabel={`Delete ${config.singular}`}
        error={error}
        isOpen
        isSubmitting={isSubmitting}
        message={`Delete ${config.singular} ${recordName(confirmModal.record)}? This cannot be undone.`}
        onCancel={onCancel}
        onConfirm={onConfirm}
        title={`Delete ${config.singular}`}
      />
    );
  }

  const action = workflowActions[confirmModal.action];

  return (
    <ConfirmActionModal
      actionLabel={action.actionLabel}
      error={error}
      isOpen
      isSubmitting={isSubmitting}
      message={action.message(confirmModal.record)}
      onCancel={onCancel}
      onConfirm={onConfirm}
      title={action.title}
    />
  );
}

export default Dashboard;
