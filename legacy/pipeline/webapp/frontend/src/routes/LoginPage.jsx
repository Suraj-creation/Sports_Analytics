import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { apiPostJson } from "../lib/api";
import "./LoginPage.css";

export function LoginPage() {
  const { user, loading, refresh } = useCurrentUser();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!loading && user) {
    return <Navigate to={user.role === "admin" ? "/admin" : "/tasks"} replace />;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await apiPostJson("/api/login", { username, password });
      await refresh();
      navigate(data.role === "admin" ? "/admin" : "/tasks");
    } catch (err) {
      setError(err.message || "Invalid username or password");
      setSubmitting(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="brand" style={{ justifyContent: "center", marginBottom: 26 }}>
        <div className="brand-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 3v18M3 12h18" />
          </svg>
        </div>
        <div>
          <div className="brand-name">Rally Review</div>
          <div className="brand-sub">Sign in to continue</div>
        </div>
      </div>
      <div className="card" style={{ padding: "22px 22px 26px" }}>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" type="text" autoComplete="username" required
                   value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div className="field" style={{ marginTop: 16 }}>
            <label htmlFor="password">Password</label>
            <input id="password" type="password" autoComplete="current-password" required
                   value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitting}
                  style={{ width: "100%", marginTop: 22, padding: 12 }}>
            {submitting ? "Signing in..." : "Log in"}
          </button>
          {error && <div className="form-error" style={{ marginTop: 10 }}>{error}</div>}
        </form>
      </div>
    </div>
  );
}
