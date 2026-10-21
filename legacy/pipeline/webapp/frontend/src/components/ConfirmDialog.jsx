import { Modal } from "./Modal";

export function ConfirmDialog({ open, message, onConfirm, onCancel }) {
  return (
    <Modal open={open} onClose={onCancel} title="Please confirm">
      <p style={{ fontSize: 13.5, color: "var(--ink-soft)", margin: "0 0 18px" }}>{message}</p>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button className="btn btn-sm" onClick={onCancel}>Cancel</button>
        <button className="btn btn-primary btn-sm" onClick={onConfirm}>Confirm</button>
      </div>
    </Modal>
  );
}
