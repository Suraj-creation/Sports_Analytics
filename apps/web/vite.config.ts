import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const api = process.env.BAI_API ?? "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: api, changeOrigin: false },
      "/ws": { target: api.replace(/^http/, "ws"), ws: true },
      "/metrics": { target: api },
    },
  },
  build: {
    target: "es2022",
    sourcemap: true,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks: {
          hls: ["hls.js/light"],
          react: ["react", "react-dom", "react-dom/client"],
          tanstack: ["@tanstack/react-query", "@tanstack/react-router"],
          radix: ["@radix-ui/react-dialog", "@radix-ui/react-popover", "@radix-ui/react-tabs"],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}"],
  },
});
