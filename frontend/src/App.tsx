// AI-ASSISTED: Cursor
// PROMPT: App shell routing to Personal Jarvis dashboard
// ACCEPTED-BY: vignesh

import { useEffect, useState } from "react";
import { AuthGate } from "./components/AuthGate";
import { fetchAuthSession, logout } from "./services/api";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [authRequired, setAuthRequired] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    let active = true;
    fetchAuthSession()
      .then((session) => {
        if (!active) return;
        setAuthRequired(session.auth_required);
        setAuthenticated(session.authenticated);
      })
      .catch(() => setAuthError("RAYA could not connect to its server."))
      .finally(() => {
        if (active) setCheckingAuth(false);
      });
    const onAuthRequired = () => setAuthenticated(false);
    window.addEventListener("raya:auth-required", onAuthRequired);
    return () => {
      active = false;
      window.removeEventListener("raya:auth-required", onAuthRequired);
    };
  }, []);

  if (checkingAuth) {
    return <main className="auth-screen" aria-busy="true">Connecting to RAYA…</main>;
  }
  if (authError) {
    return <main className="auth-screen" role="alert">{authError}</main>;
  }
  if (authRequired && !authenticated) {
    return (
      <AuthGate
        onAuthenticated={() => {
          setAuthError("");
          setAuthenticated(true);
        }}
      />
    );
  }
  return (
    <Dashboard
      onSignOut={authRequired ? async () => {
        await logout();
        setAuthenticated(false);
      } : undefined}
    />
  );
}
