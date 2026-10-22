import "./tokens.css";
import { RouterProvider } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { router } from "./router";

/**
 * Design prototype entry point.
 *
 * Served at /prototype.html by the existing Vite dev server. It shares no code and no
 * stylesheet with the production app in src/ — nothing here can change how that app
 * behaves, which is the point: this is design-only (DESIGN_DIRECTION, Scope).
 */

const root = document.getElementById("root");
if (!root) throw new Error("#root missing from prototype.html");

createRoot(root).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
