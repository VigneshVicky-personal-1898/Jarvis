import { useState, type FormEvent } from "react";
import { login } from "../services/api";
import "./AuthGate.css";

export function AuthGate({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(password);
      onAuthenticated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-panel" aria-labelledby="auth-title">
        <p className="auth-eyebrow">RAYA · PRIVATE CLOUD</p>
        <h1 id="auth-title">Sign in</h1>
        <form className="auth-form" onSubmit={submit}>
          <label htmlFor="raya-password">Access password</label>
          <input
            id="raya-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
            autoFocus
          />
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button className="btn btn-primary" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Continue"}
          </button>
        </form>
      </section>
    </main>
  );
}