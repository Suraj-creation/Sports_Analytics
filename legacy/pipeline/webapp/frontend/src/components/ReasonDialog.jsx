import { useState } from "react";
import { Modal } from "./Modal";

export function ReasonDialog({ open, title, prompt, onSubmit, onCancel }) {
  const [reason, setReason] = useState("");

  function handleClose() {
    setReason("");
    onCancel();
  }

  function handleSubmit() {
    if (!reason.trim()) return;
    onSubmit(reason.trim());
    setReason("");
  }

  return (
    <Modal open={open} onClose={handleClose} title={title}>
      <p style={{ fontSize: 13, color: "var(--ink-soft)", margin: "0 0 10px" }}>{prompt}</p>
      <textarea
        style={{
          width: "100%", minHeight: 70, padding: 10, boxSizing: "border-box",
          border: "1px solid var(--line-strong)", borderRadius: "var(--radius-sm)",
          background: "var(--paper)", color: "var(--ink)", font: "inherit", resize: "vertical",
        }}
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        autoFocus
      />
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 14 }}>
        <button className="btn btn-sm" onClick={handleClose}>Cancel</button>
        <button className="btn btn-primary btn-sm" onClick={handleSubmit} disabled={!reason.trim()}>
          Submit
        </button>
      </div>
    </Modal>
  );
}
