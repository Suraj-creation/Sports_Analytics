import { createContext, useCallback, useContext, useRef, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toast, setToast] = useState({ show: false, message: "", isErr: false });
  const timerRef = useRef(null);

  const showToast = useCallback((message, isErr = false) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setToast({ show: true, message, isErr });
    timerRef.current = setTimeout(() => setToast((t) => ({ ...t, show: false })), 2600);
  }, []);

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className={"toast" + (toast.show ? " show" : "") + (toast.isErr ? " err" : "")}>
        <span>{toast.message}</span>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
