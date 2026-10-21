import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev-only: forwards /api/* (including byte-serving routes like video/PDF/
// frame JPEGs) to the Flask backend so the browser only ever talks to one
// origin -- session cookies stay correctly scoped with zero CORS config.
// Not used in production; server.py serves the built dist/ directly.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
