# GlitchRecon

**Evidence-driven web security scanner** — automated scanners collect raw evidence, then AI explains, prioritises, and recommends fixes.

GlitchRecon runs a battery of passive and active security checks (XSS, SQLi, CSRF, SSRF, IDOR, security headers, cookie analysis, TLS fingerprinting, and more) against a target web application. Every finding is backed by scanner-captured evidence. An LLM (Groq or Ollama) is used *only* to generate human-readable summaries, risk scoring, and remediation guidance — it never hallucinates findings.

## Who is this for?

- **Security researchers & penetration testers** — automate the initial reconnaissance and evidence gathering phase of a web application audit.
- **Bug bounty hunters** — quickly assess a target's attack surface and get AI-prioritised findings before diving deeper.
- **DevOps & platform engineers** — integrate into a CI/CD pipeline to catch regressions in security headers, cookie flags, and common misconfigurations.
- **Web developers** — run an on-demand scan against a staging or production environment to understand the current security posture and get actionable fix recommendations.
- **Site owners** — verify that a web property you own or are authorised to test follows security best practices.

> **⚠️ Ethical use only.** Only scan systems you own or have explicit written authorisation to test.

---

## How it works

1. **Target intake** — you provide a URL via the CLI, web UI, or REST API.
2. **Validation & crawling** — the target is validated, resolved, and crawled to discover endpoints and technologies.
3. **Scanning pipeline** — each security scanner runs independently and records raw evidence (headers, cookies, response payloads, timing data, etc.).
4. **AI enrichment** — the LLM analyses all collected evidence to assign severities, write an executive summary, suggest remediation steps, and compute an evidence-weighted risk score.
5. **Report generation** — a structured report containing every finding, the raw evidence it was based on, and the AI-generated analysis is returned.

---

## Quick start

### 1. Clone & set up

```bash
git clone <repo-url>
cd GlitchRecon
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure an LLM provider

Open `.env` and choose one provider:

**Groq** (default):

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile     # optional
GROQ_BASE_URL=https://api.groq.com      # optional
GROQ_TIMEOUT=30                         # optional
```

**Ollama** (local):

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
OLLAMA_HOST=http://localhost:11434       # optional
OLLAMA_TIMEOUT=120                       # optional
```

### 3. Run a scan

#### Via the REST API (recommended)

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in a browser to use the built-in web UI, or send a POST request:

```bash
curl -X POST http://127.0.0.1:8000/scans \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com"}'
```

#### Via the CLI

```bash
python main.py
```

You will be prompted for a target URL. The CLI will print the AI-generated response for that prompt.

> **Note:** The primary interface is the web API and its accompanying web UI. The legacy CLI (`main.py`) currently sends a single prompt to the LLM and is provided for convenience / debugging.

#### Programmatic usage (Python)

```python
from app.pipeline.pipeline import Pipeline
from app.pipeline.stages import (
    ValidationStage,
    ReconStage,
    FingerprintingStage,
)

pipeline = Pipeline()
pipeline.add_stage(ValidationStage())
pipeline.add_stage(ReconStage())
pipeline.add_stage(FingerprintingStage())
# ... add more stages ...

context = await pipeline.run("https://example.com")
print(context.status)          # "completed" or "failed"
print(context.findings)        # raw scanner findings
print(context.technologies)    # detected technologies
```

---

## Run tests

```bash
pytest
```

Tests run in isolation and never contact an external LLM service or network target.

---

## Project structure

```
GlitchRecon/
├── main.py                      # FastAPI ASGI entry point
├── app/
│   ├── api/                     # REST endpoints (scan, AI, report)
│   ├── core/                    # LLM providers (Groq, Ollama), base classes
│   ├── models/                  # Pydantic schemas (Scan, Finding, Report)
│   └── pipeline/                # Scan pipeline and stages
│       └── stages/
│           ├── intake.py        # Target pre-processing
│           ├── validation.py    # URL validation & reachability
│           ├── recon.py         # Basic recon / endpoint discovery
│           ├── fingerprinting.py# TLS / HTTP fingerprinting
│           ├── planning.py      # Scan plan generation
│           ├── crawler.py       # Web crawling
│           ├── ai_analysis.py   # AI enrichment of findings
│           ├── report.py        # Report assembly
│           ├── save.py          # Persistence
│           └── ...              # More stages
├── scanners/                    # Individual security scanners
│   ├── xss/
│   ├── sqli/
│   ├── csrf/
│   ├── ssrf/
│   ├── idor/
│   ├── headers/
│   ├── cookies/
│   └── fingerprinting/
├── services/                    # Business logic services
├── repositories/                # Data access layer (scan, finding, report)
├── tests/                       # Pytest test suite
├── index.html                   # Web UI front-end
├── requirements.txt
└── .env.example                 # Environment variable template
```

---

## Key concepts

| Concept | Description |
|---|---|
| **Scanner** | A self-contained module that checks one security aspect (e.g., missing `X-Frame-Options`) and records raw evidence. |
| **Finding** | An individual security issue detected by a scanner, backed by evidence. |
| **Pipeline** | Ordered sequence of stages that processes a target from intake to report. |
| **AI enrichment** | The LLM analyses raw scanner evidence to produce human-readable summaries, severity labels, and remediation steps. The AI *never* creates findings — it only explains what the scanners found. |
| **Evidence** | Raw data captured by a scanner (response headers, cookie attributes, DOM snapshots, etc.). This is what every finding is grounded in. |

---

## License

See [LICENSE](./LICENSE).
