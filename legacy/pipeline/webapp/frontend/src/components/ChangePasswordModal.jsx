import { useState } from "react";
import { Modal } from "./Modal";
import { apiPostJson } from "../lib/api";
import { useToast } from "./ToastProvider";

export function ChangePasswordModal({ open, onClose }) {
  const [oldPw, setOldPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const showToast = useToast();

  function handleClose() {
    setOldPw(""); setNewPw(""); setError("");
    onClose();
  }

  async function handleSave() {
    setError("");
    if (newPw.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    setSaving(true);
    try {
      await apiPostJson("/api/me/change-password", { old_password: oldPw, new_password: newPw });
      handleClose();
      showToast("Password changed");
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Modal open={open} onClose={handleClose} title="Change password">
      <div className="field" style={{ marginBottom: 12 }}>
        <label htmlFor="pw-old">Current password</label>
        <input id="pw-old" type="password" autoComplete="current-password"
               value={oldPw} onChange={(e) => setOldPw(e.target.value)} />
      </div>
      <div className="field" style={{ marginBottom: 12 }}>
        <label htmlFor="pw-new">New password (min 8 characters)</label>
        <input id="pw-new" type="password" autoComplete="new-password"
               value={newPw} onChange={(e) => setNewPw(e.target.value)} />
      </div>
      {error && <div className="form-error" style={{ marginBottom: 10 }}>{error}</div>}
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button className="btn btn-sm" onClick={handleClose}>Cancel</button>
        <button className="btn btn-primary btn-sm" onClick={handleSave} disabled={saving}>
          {saving ? "Saving..." : "Save"}
        </button>
      </div>
    </Modal>
  );
}
