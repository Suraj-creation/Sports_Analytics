import { useEffect, useState } from "react";
import { usePolling } from "../../hooks/usePolling";
import { apiGet, apiPostJson, apiPost } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";
import { Pill } from "../../components/Pill";
import { ConfirmDialog } from "../../components/ConfirmDialog";

export function UsersPanel({ onInternsChanged }) {
  const [reloadKey, setReloadKey] = useState(0);
  const { data } = usePolling(() => apiGet("/api/admin/users"), {
    intervalMs: 8000, deps: [reloadKey],
  });
  const users = data?.users || [];

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [confirmTarget, setConfirmTarget] = useState(null);
  const showToast = useToast();

  // Let the parent (JobsTable's assign dropdowns) know whenever the
  // active-intern list changes -- in an effect, not during render: calling
  // it directly in the render body would create a new array every render,
  // which (if the parent stores it in state) triggers a parent re-render
  // -> child re-render -> new array -> infinite loop.
  useEffect(() => {
    if (!data) return;
    onInternsChanged(data.users.filter((u) => u.role === "intern" && u.active));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  async function handleCreate() {
    setError("");
    if (!username.trim() || !password) {
      setError("Username and password are both required.");
      return;
    }
    try {
      await apiPostJson("/api/admin/users", { username: username.trim(), password });
      setUsername(""); setPassword("");
      showToast(`Intern '${username}' created`);
      setReloadKey((k) => k + 1);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeactivate(id) {
    await apiPost(`/api/admin/users/${id}/deactivate`);
    setConfirmTarget(null);
    setReloadKey((k) => k + 1);
  }

  return (
    <div className="card" style={{ marginTop: 22 }}>
      <div className="card-head"><h2>Interns</h2></div>
      <div className="users-panel">
        <div className="field">
          <label htmlFor="new-username">Username</label>
          <input id="new-username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="new-password">Password</label>
          <input id="new-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div><button className="btn btn-primary btn-sm" onClick={handleCreate}>+ Add intern</button></div>
        {error && <div className="form-error">{error}</div>}
        <div className="users-list">
          {users.map((u) => (
            <div className="u-row" key={u.id}>
              <span style={{ flex: 1 }}>{u.username}</span>
              <Pill map={{ admin: ["pill-slate", "admin"], intern: ["pill-court", "intern"] }} statusKey={u.role} />
              {!u.active
                ? <span className="pill pill-coral">disabled</span>
                : (u.role === "intern" &&
                   <button className="btn btn-sm" onClick={() => setConfirmTarget(u)}>Disable</button>)}
            </div>
          ))}
        </div>
      </div>
      <ConfirmDialog
        open={!!confirmTarget}
        message={`Disable ${confirmTarget?.username}'s account? Existing assignment history stays intact.`}
        onConfirm={() => handleDeactivate(confirmTarget.id)}
        onCancel={() => setConfirmTarget(null)}
      />
    </div>
  );
}
