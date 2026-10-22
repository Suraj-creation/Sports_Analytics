import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";

const CLIP = fileURLToPath(new URL("./.tmp/clip.mp4", import.meta.url));

test("upload → play with synced clock → analysis completes → tabs and exports", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  await page.goto("/library");
  await expect(page.getByRole("heading", { name: "Analyse a match" })).toBeVisible();

  // upload
  await page.locator('input[type="file"]').setInputFiles(CLIP);
  await page.getByLabel("Player 1").first().fill("Viktor Axelsen");
  await page.getByLabel("Player 2").first().fill("Kento Momota");
  await page.getByRole("button", { name: "Analyse video" }).click();

  // the session page opens straight away
  await expect(page).toHaveURL(/\/sessions\/[A-Z0-9]+$/);
  await expect(page.getByRole("heading", { name: "clip" })).toBeVisible();
  await expect(page.getByTestId("score-bug")).toContainText("Axelsen");

  // the video plays through hls.js and the presented-frame clock advances
  const video = page.locator("video");
  await expect
    .poll(async () => video.evaluate((v: HTMLVideoElement) => v.readyState), { timeout: 60_000 })
    .toBeGreaterThanOrEqual(2);
  await page.getByTestId("video-stage").click(); // click toggles play
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.currentTime)).toBeGreaterThan(0.5);
  await page.keyboard.press("Space");

  // frame stepping is exact: → advances one frame
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(true);
  // Seek a known paused frame; the final presented-frame callback after pause can
  // arrive after React's throttled readout, so its in-flight value is not a baseline.
  await video.evaluate((v: HTMLVideoElement) => {
    v.currentTime = 45.5 / 30;
  });
  const frameText = page.getByText(/^frame [\d,]+$/);
  await expect(frameText).toHaveText("frame 45");
  const before = Number((await frameText.textContent())?.replace(/\D/g, ""));
  await page.keyboard.press("ArrowRight");
  await expect.poll(async () => Number((await frameText.textContent())?.replace(/\D/g, ""))).toBe(before + 1);

  // analysis finishes (model-free profile) and the status says so
  await expect(page.locator(".match-subtitle").filter({ hasText: "Analysed" })).toBeVisible({
    timeout: 90_000,
  });

  await page.screenshot({ path: "test-results/screens/session.png", fullPage: true });

  // shortcuts dialog
  await page.keyboard.press("?");
  await expect(page.getByRole("dialog", { name: "Keyboard shortcuts" })).toBeVisible();
  await page.keyboard.press("Escape");

  // tabs render; exports download real files
  await page
    .getByRole("navigation", { name: "Match analysis" })
    .getByRole("button", { name: "Rallies", exact: true })
    .click();
  await page.getByRole("button", { name: "Export", exact: true }).click();
  const [download] = await Promise.all([
    page.waitForEvent("download"),
    page.getByRole("link", { name: /Event log/ }).click(),
  ]);
  expect(download.suggestedFilename()).toMatch(/\.jsonl$/);

  // the library lists the match as analysed
  await page.goto("/library");
  await expect(page.getByRole("link", { name: "clip" })).toBeVisible();
  await expect(page.getByText("Analysed").first()).toBeVisible();
  await page.screenshot({ path: "test-results/screens/library.png", fullPage: true });

  // system page
  await page.goto("/system");
  await expect(page.getByRole("heading", { name: "Models" })).toBeVisible();
  await page.screenshot({ path: "test-results/screens/system.png", fullPage: true });

  expect(errors).toEqual([]);
});
