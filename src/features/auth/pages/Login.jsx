function Login() {
  return (
    <main className="auth-page">
      <a className="auth-brand" href="/">
        <span className="brand-mark">G</span>
        <span>GlitchRecon</span>
      </a>

      <section className="auth-card" aria-labelledby="login-title">
        <div className="auth-header">
          <p className="eyebrow">Welcome back</p>
          <h1 id="login-title">Login to your console</h1>
          <p>
            Continue managing authorized scans, targets, findings, and reports.
          </p>
        </div>

        <form className="auth-form">
          <label className="auth-field">
            <span>Username</span>
            <input
              autoComplete="username"
              name="username"
              placeholder="argus"
              type="text"
            />
          </label>

          <label className="auth-field">
            <span>Password</span>
            <input
              autoComplete="current-password"
              name="password"
              placeholder="Enter your password"
              type="password"
            />
          </label>

          <button className="auth-submit" type="submit">
            Login
          </button>
        </form>

        <p className="auth-switch">
          New to GlitchRecon? <a href="/register">Create an account</a>
        </p>
      </section>
    </main>
  );
}

export default Login;
