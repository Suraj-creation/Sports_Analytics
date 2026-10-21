import { defineConfig } from "@playwright/test";

const PORT = Number(process.env.BAI_E2E_PORT ?? 8765);

/**
 * Browser end-to-end tests against the real API + engine (model-free profile).
 * Build the SPA first (`pnpm build`); the server serves apps/web/dist.
 * PW_CHANNEL=msedge|chrome uses an installed browser instead of Playwright's Chromium.
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    channel: process.env.PW_CHANNEL || undefined,
    viewport: { width: 1440, height: 900 },
    trace: "retain-on-failure",
  },
  webServer: {
    command: `uv run python e2e/server.py ${PORT}`,
    url: `http://127.0.0.1:${PORT}/api/health`,
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
});
