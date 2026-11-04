import { test as base } from "@playwright/test";

// Keep test execution on the GPU server while using an installed browser over SSH.
const cdpEndpoint = process.env.PW_CDP_ENDPOINT;
export const test = cdpEndpoint
  ? base.extend({
      browser: async ({ playwright }, use) => {
        const browser = await playwright.chromium.connectOverCDP(cdpEndpoint);
        try {
          await use(browser);
        } finally {
          await browser.close();
        }
      },
    })
  : base;

export { expect } from "@playwright/test";
