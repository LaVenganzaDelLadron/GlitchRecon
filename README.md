# GlitchRecon

GlitchRecon is a FastAPI-based cybersecurity automation backend for organizing projects, targets, scans, findings, and reports. It combines traditional reconnaissance and vulnerability tooling with an AI-assisted planning layer that can suggest safe scan workflows while the backend keeps control of what commands are allowed to run.

The project is designed for authorized security testing only.

## Purpose

GlitchRecon helps security teams and learners run repeatable reconnaissance and vulnerability checks without manually stitching together many command-line tools each time. It stores targets and scan records, creates approval-gated scan plans, runs tools in the background, and keeps logs for review.

The main goal is not to give an AI unrestricted terminal access. Instead, AI can propose a plan, but the backend validates the tools, target types, command arguments, and approval state before anything executes.

## Who Uses It

- Bug bounty hunters who want repeatable recon workflows.
- Penetration testers working on scoped client assessments.
- SOC or AppSec teams doing internal asset discovery and exposure checks.
- Students learning how recon, vulnerability scanning, and secret scanning tools fit together.
- Developers building a security automation platform with human approval gates.

## Core Features

- JWT authentication with protected API routes.
- Project and target management.
- AI-assisted scan planning with Ollama, OpenAI, or Anthropic provider adapters.
- Safe fallback planning when AI is slow, unavailable, or suggests an invalid tool.
- Strict tool registry with allowlisted commands and target compatibility checks.
- Approval gate before scan execution.
- Background scan jobs so long-running tools do not freeze the API or terminal.
- Log files under `storage/scan_jobs/`.
- Single-tool scans for focused checks.
- Multi-tool reconnaissance scan plans with parent and child scans.
- Finding creation from scan output.
- Report route structure for future report generation.

## Scan Workflow

The normal flow is:

1. Log in and get a JWT token.
2. Create a project.
3. Create a target.
4. Create a scan plan.
5. Review and approve the plan.
6. Run the scan in the background.
7. Poll scan status.
8. Read scan logs and findings.

For comprehensive recon goals, GlitchRecon creates a parent `recon_suite` scan and multiple child scans. Child scans run sequentially by default to avoid overwhelming the local machine or the target.

## Supported Tool Categories

Enumeration and reconnaissance tools include:

- `amass`
- `assetfinder`
- `dnsx`
- `findomain`
- `subfinder`
- `gau`
- `waybackurls`
- `katana`
- `hakrawler`

Analysis and fingerprinting tools include:

- `whatweb`
- `wappalyzer`

Vulnerability and secret scanning tools include:

- `nuclei`
- `gitleaks`
- `trufflehog`

The backend only runs tools through `services/tool_registry.py`. Target compatibility is enforced. For example, `amass` is allowed for `domain` or `hostname` targets, while `nuclei`, `katana`, and `whatweb` are intended for `url` targets.

## Safety Model

GlitchRecon follows these safety rules:

- AI never receives raw shell access.
- Commands must come from the allowlisted tool registry.
- Commands are built as argument arrays, not shell strings.
- Scans require approval before execution.
- Long-running tools execute in background jobs.
- Output is written to log files instead of being held entirely in memory.
- Request timeouts protect the API from hanging handlers.
- Slow or invalid AI planning falls back to safe deterministic plans.

## Project Structure

```text
ai/                  AI agents, prompts, and provider adapters
api/routes/          FastAPI route definitions
core/                Database and schema helpers
models/              SQLAlchemy models
schemas/             Pydantic request schemas
services/            Business logic, scan orchestration, command runner
tools/               Tool wrapper classes grouped by security phase
storage/             SQLite DB, scan logs, reports, uploads
tests/               Pytest test suite
main.py              FastAPI entrypoint
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```bash
JWT_SECRET_KEY=change-this-secret
```

Optional AI provider variables:

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
SCAN_PLAN_TIMEOUT_SECONDS=10
REQUEST_HARD_TIMEOUT=45
```

For local Ollama planning, install and run Ollama separately, then pull a model:

```bash
ollama pull deepseek-r1:8b
```

## Run The API

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

Open the API docs:

```text
http://127.0.0.1:5000/docs
```

## Example API Flow

Log in:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "argus",
  "password": "glitcher"
}'
```

Create a project:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/project/' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "owner_id": 1,
  "name": "davaodelnorte",
  "description": "authorized reconnaissance test",
  "scope": "davaodelnorte.ph",
  "status": "active"
}'
```

Create a target:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/target/' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "project_id": 1,
  "type": "url",
  "value": "https://davaodelnorte.ph",
  "notes": "Authorized test target"
}'
```

Create a comprehensive recon plan:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/scan/plan' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "project_id": 1,
  "target_id": 1,
  "goal": "Perform comprehensive reconnaissance on the target website. Use all safe reconnaissance tools to discover endpoints, technology stack, and publicly accessible vulnerabilities within scope.",
  "provider": "ollama"
}'
```

Approve the scan:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/scan/1/approve' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json'
```

View child scans for a multi-tool plan:

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/scan/1/children' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json'
```

Run the scan:

```bash
curl -X 'POST' \
  'http://127.0.0.1:5000/scan/1/run' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json'
```

Poll status:

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/scan/1/status' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json'
```

Read logs:

```bash
curl -X 'GET' \
  'http://127.0.0.1:5000/scan/1/logs' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE' \
  -H 'accept: application/json'
```

## AI Planning Behavior

The AI planner may return a valid tool choice, fail, time out, or suggest a tool that does not match the target type. GlitchRecon handles this safely:

- Valid AI plan: use it after registry validation.
- Slow AI plan: fallback to a safe default.
- Invalid tool: fallback to a safe default.
- Comprehensive recon request: create a `recon_suite` parent scan with multiple children.

For example, if the target is a URL and AI suggests `amass`, the backend rejects it because `amass` expects a domain or hostname. It may then fallback to URL-compatible tools such as `katana`, `hakrawler`, or `nuclei`.

## Background Jobs

Scans run in the background and write output to:

```text
storage/scan_jobs/
```

This prevents long scans from freezing the API request. Use `/scan/{id}/status` and `/scan/{id}/logs` to monitor progress.

## Testing

Run the test suite:

```bash
pytest -q
```

The tests cover:

- Tool registry validation.
- AI timeout and fallback behavior.
- Background scan lifecycle.
- Multi-tool recon parent and child scans.
- Scan status, logs, cancellation, and finding creation.

## Important Notes

- Only scan systems you own or have explicit permission to test.
- Some external tools must be installed separately on the host machine.
- If a command returns `command not found`, install that tool and retry.
- Use `--reload` during development so FastAPI picks up code changes.
- Review every scan plan before approval.

## License

Add your preferred license before public release.
