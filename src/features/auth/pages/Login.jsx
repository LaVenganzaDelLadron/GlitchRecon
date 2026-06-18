import { useState } from "react";
import { api, getAuthTokenFromPayload, setStoredToken } from "../../../services/api.js";

function Login() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitLogin(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const credentials = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    try {
      const result = await api.login(credentials);
      const token = getAuthTokenFromPayload(result);

      if (token) {
        setStoredToken(token);
      }

      window.location.assign("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

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

        <form className="auth-form" onSubmit={submitLogin}>
          <label className="auth-field">
            <span>Username</span>
            <input
              autoComplete="username"
              name="username"
              placeholder="argus"
              required
              type="text"
            />
          </label>

          <label className="auth-field">
            <span>Password</span>
            <input
              autoComplete="current-password"
              name="password"
              placeholder="Enter your password"
              required
              type="password"
            />
          </label>

          {error ? <p className="auth-alert error">{error}</p> : null}

          <button className="auth-submit" disabled={loading} type="submit">
            {loading ? "Logging in..." : "Login"}
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
