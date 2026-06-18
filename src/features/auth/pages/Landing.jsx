function Landing() {
  return (
    <div className="landing-page">
      <header className="site-header">
        <a className="brand" href="/">
          <span className="brand-mark">G</span>
          <span>GlitchRecon</span>
        </a>

        <nav className="site-nav" aria-label="Primary navigation">
          <a href="#features">Features</a>
          <a href="#workflow">Workflow</a>
          <a href="#status">Status</a>
        </nav>

        <div className="header-actions">
          <a className="header-button ghost" href="/login">
            Login
          </a>
          <a className="header-button" href="/register">
            Register
          </a>
        </div>
      </header>

      <main>
        <section className="hero-section">
          <div className="hero-copy">
            <p className="eyebrow">Authorized reconnaissance platform</p>
            <h1>
              Plan, approve, and track security scans from one focused console.
            </h1>
            <p className="hero-text">
              GlitchRecon pairs FastAPI automation with AI-assisted planning,
              strict command allowlists, and background scan logs your team can
              review without losing the thread.
            </p>

            <div className="hero-actions">
              <a className="primary-action" href="#workflow">
                View workflow
              </a>
              <a className="secondary-action" href="http://127.0.0.1:5000/docs">
                API docs
              </a>
            </div>
          </div>

          <div className="scan-console" aria-label="Scan console preview">
            <div className="console-topbar">
              <span className="window-dot"></span>
              <span className="window-dot"></span>
              <span className="window-dot"></span>
              <strong>recon-suite</strong>
            </div>

            <div className="console-body">
              <div className="console-row">
                <span>Target</span>
                <strong>https://example.com</strong>
              </div>
              <div className="console-row">
                <span>Provider</span>
                <strong>ollama</strong>
              </div>
              <div className="console-row">
                <span>Approval</span>
                <strong className="status-ready">waiting</strong>
              </div>

              <div className="terminal-output">
                <p>$ plan comprehensive reconnaissance</p>
                <p>tool registry validated: subfinder, dnsx, nuclei</p>
                <p>created parent scan #24 with 3 child jobs</p>
                <p>status: approval required before execution</p>
              </div>
            </div>
          </div>
        </section>

        <section className="metric-strip" id="status">
          <div>
            <span>Scan modes</span>
            <strong>Single + suite</strong>
          </div>
          <div>
            <span>Execution</span>
            <strong>Approval gated</strong>
          </div>
          <div>
            <span>Logs</span>
            <strong>Background jobs</strong>
          </div>
        </section>

        <section className="feature-section" id="features">
          <div className="section-heading">
            <p className="eyebrow">Core controls</p>
            <h2>Built for repeatable recon without raw shell access.</h2>
          </div>

          <div className="feature-grid">
            <article className="feature-card">
              <span className="feature-index">01</span>
              <h3>Validated scan plans</h3>
              <p>
                AI can suggest a workflow, but the backend validates tools,
                target compatibility, arguments, and approval state.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-index">02</span>
              <h3>Project tracking</h3>
              <p>
                Keep projects, targets, scans, findings, and reports organized
                around the authorized scope you are testing.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-index">03</span>
              <h3>Readable operations</h3>
              <p>
                Long-running jobs write logs to storage while the API stays
                responsive for status checks and follow-up review.
              </p>
            </article>
          </div>
        </section>

        <section className="workflow-section" id="workflow">
          <div>
            <p className="eyebrow">Workflow</p>
            <h2>From target to findings in clear checkpoints.</h2>
          </div>

          <ol className="workflow-list">
            <li>Create a project and define an authorized target.</li>
            <li>Generate a scan plan from a goal and chosen AI provider.</li>
            <li>Review, approve, run, and monitor scan logs.</li>
            <li>Turn useful output into findings and reports.</li>
          </ol>
        </section>
      </main>
    </div>
  );
}

export default Landing;
