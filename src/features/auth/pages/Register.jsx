import { useState } from "react";
import { api } from "../../../services/api.js";

function Register() {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");

  async function submitRegister(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const credentials = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    try {
      await api.register(credentials);
      setSuccess("Account created. Redirecting to login...");
      window.setTimeout(() => {
        window.location.assign("/login");
      }, 700);
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

      <section className="auth-card" aria-labelledby="register-title">
        <div className="auth-header">
          <p className="eyebrow">Create access</p>
          <h1 id="register-title">Register your account</h1>
          <p>
            Set up a workspace login for planning and reviewing scan activity.
          </p>
        </div>

        <form className="auth-form" onSubmit={submitRegister}>
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
              autoComplete="new-password"
              name="password"
              placeholder="Create a password"
              required
              type="password"
            />
          </label>

          {error ? <p className="auth-alert error">{error}</p> : null}
          {success ? <p className="auth-alert success">{success}</p> : null}

          <button className="auth-submit" disabled={loading} type="submit">
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <a href="/login">Login instead</a>
        </p>
      </section>
    </main>
  );
}

export default Register;
