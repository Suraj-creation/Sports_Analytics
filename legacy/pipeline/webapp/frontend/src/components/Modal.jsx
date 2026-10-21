import { createPortal } from "react-dom";

// Rendered via a portal straight onto document.body -- .topbar (this
// component's usual DOM ancestor via ChangePasswordModal) has
// backdrop-filter set, which establishes a CSS containing block for
// position:fixed descendants (same effect as `filter`), so a plain nested
// fixed-position modal renders clipped to the topbar's box instead of
// centered in the viewport. A portal sidesteps that entirely.
export function Modal({ open, onClose, title, width = 340, children }) {
  if (!open) return null;
  return createPortal(
    <div
      style={{
        display: "flex", position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
        zIndex: 50, alignItems: "center", justifyContent: "center",
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="card" style={{ width, padding: "20px 22px 22px" }}>
        {title && (
          <h2 style={{ fontFamily: "var(--font-head)", fontSize: 15, margin: "0 0 14px" }}>
            {title}
          </h2>
        )}
        {children}
      </div>
    </div>,
    document.body
  );
}
