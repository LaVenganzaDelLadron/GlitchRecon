function Register() {
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
              autoComplete="new-password"
              name="password"
              placeholder="Create a password"
              type="password"
            />
          </label>

          <button className="auth-submit" type="submit">
            Register
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
