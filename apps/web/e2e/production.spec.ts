import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

const CLIP = fileURLToPath(new URL("./.tmp/clip.mp4", import.meta.url));
const ROUTES = [
  ["/", "Good to see you"],
  ["/matches", "Your matches"],
  ["/moments", "Moments worth another look"],
  ["/people", "People you play with"],
  ["/progress", "Your progress"],
  ["/settings", "Settings"],
  ["/help", "Understanding your analytics"],
] as const;

async function noHorizontalOverflow(page: Page) {
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth),
  ).toBeLessThanOrEqual(1);
}

async function upload(request: APIRequestContext) {
  const response = await request.post("/api/sessions", {
    multipart: {
      file: { name: "production-e2e.mp4", mimeType: "video/mp4", buffer: await readFile(CLIP) },
      title: "Production integration match",
      player1: "Integration Near",
      player2: "Integration Far",
    },
  });
  expect(response.status()).toBe(201);
  const created = await response.json();
  await expect
    .poll(
      async () => {
        const response = await request.get(`/api/sessions/${created.session_id}`);
        return (await response.json()).status;
      },
      { timeout: 90_000 },
    )
    .toBe("analysed");
  return (await (await request.get(`/api/sessions/${created.session_id}`)).json()) as {
    session_id: string;
    title: string;
    media: { fps_num: number; fps_den: number; n_frames: number };
  };
}

test("product routes work with a genuinely empty library on desktop and mobile", async ({
  page,
  request,
}) => {
  // This file runs before smoke.spec.ts against its throwaway, model-free API.
  expect(await (await request.get("/api/sessions")).json()).toEqual([]);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  for (const viewport of [
    { width: 1440, height: 900 },
    { width: 390, height: 844 },
  ]) {
    await page.setViewportSize(viewport);
    for (const [route, heading] of ROUTES) {
      await page.goto(route);
      await expect(page.getByRole("heading", { name: heading, exact: true })).toBeVisible();
      await noHorizontalOverflow(page);
      await expect(page.getByText("Viktor Axelsen", { exact: true })).toHaveCount(0);
    }
  }
  expect(errors).toEqual([]);
});

test("real upload creates playable media with range delivery and exact frame navigation", async ({
  page,
  request,
}) => {
  const session = await upload(request);
  const id = session.session_id;
  const fps = session.media.fps_num / session.media.fps_den;
  const playlist = await request.get(`/api/sessions/${id}/hls/index.m3u8`);
  expect(playlist.status()).toBe(200);
  expect(playlist.headers()["cache-control"]).toBe("no-cache");
  expect(await playlist.text()).toContain("#EXT-X-ENDLIST");
  const range = await request.get(`/api/sessions/${id}/proxy.mp4`, { headers: { Range: "bytes=0-1023" } });
  expect(range.status()).toBe(206);
  expect(range.headers()["content-range"]).toMatch(/^bytes 0-1023\//);
  expect((await range.body()).length).toBe(1024);
  expect((await request.get(`/api/sessions/${id}/hls/not-a-segment`)).status()).toBe(404);

  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`/matches/${id}?tab=overview&who=P1&f=60`);
  await expect(page.getByRole("heading", { name: session.title, exact: true })).toBeVisible();
  const video = page.locator("video");
  await expect
    .poll(async () => video.evaluate((v: HTMLVideoElement) => v.readyState), { timeout: 60_000 })
    .toBeGreaterThanOrEqual(2);
  await expect
    .poll(async () => video.evaluate((v: HTMLVideoElement) => v.currentTime))
    .toBeCloseTo(60 / fps, 0);
  await page.getByRole("button", { name: "Play (Space)", exact: true }).click();
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.currentTime)).toBeGreaterThan(2.5);
  await page.getByRole("button", { name: "Pause (Space)", exact: true }).click();
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(true);
  await video.evaluate((v: HTMLVideoElement) => {
    v.currentTime = 90.5 / 30;
  });
  const frameText = page.getByText(/^frame [\d,]+$/);
  await expect(frameText).toHaveText("frame 90");
  const before = Number((await frameText.textContent())?.replace(/\D/g, ""));
  await page.getByRole("button", { name: "Next frame (→)", exact: true }).click();
  await expect.poll(async () => Number((await frameText.textContent())?.replace(/\D/g, ""))).toBe(before + 1);
  await expect
    .poll(async () => video.evaluate((v: HTMLVideoElement) => Math.floor(v.currentTime * 30 + 1e-4)))
    .toBe(before + 1);
  await page.getByLabel("Playback speed", { exact: true }).selectOption("0.5");
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.playbackRate)).toBe(0.5);
  await page.getByLabel("Playback speed", { exact: true }).selectOption("1");
  const cue = () =>
    page.evaluate(() =>
      window.dispatchEvent(
        new CustomEvent("bai:play-clip", {
          detail: { start: 90, end: 105, label: "Canonical test moment" },
        }),
      ),
    );
  await cue();
  await expect(page.getByTestId("evidence-details")).toContainText("source frame 90");
  await expect(page.getByTestId("selected-event-marker")).toBeVisible();
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(true);
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => Math.floor(v.currentTime * 30))).toBe(105);
  // Re-selecting the same event is a new playback request, not a no-op from stale query state.
  await cue();
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(false);
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => v.paused)).toBe(true);
  const timeline = page.getByRole("slider", { name: "Match timeline" });
  await timeline.focus();
  await page.keyboard.press("Home");
  await expect(page.getByTestId("selected-event-marker")).toHaveCount(0);
  await expect(page.getByText("Canonical test moment · bounded clip", { exact: true })).toHaveCount(0);
  await expect.poll(async () => video.evaluate((v: HTMLVideoElement) => Math.floor(v.currentTime * 30))).toBe(0);
  await expect(timeline).toHaveAttribute("aria-valuemax", String(session.media.n_frames - 1));
  const picture = await page.getByTestId("video-stage").boundingBox();
  expect(picture).not.toBeNull();
  expect((picture?.width ?? 0) / (picture?.height ?? 1)).toBeCloseTo(16 / 9, 1);
  await page.screenshot({ path: "/tmp/bai-audit-frontend-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "Overlay layers", exact: true }).click();
  const shuttle = page.getByRole("switch", { name: "Shuttle trail", exact: true });
  await shuttle.click();
  await expect(shuttle).toHaveAttribute("aria-checked", "false");
  await page.keyboard.press("Escape");

  await page.getByRole("button", { name: "Show Far numbers", exact: true }).click();
  await expect(page).toHaveURL(/who=P2/);
  await expect(page.getByRole("button", { name: "Show Far numbers", exact: true })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  const tabs = page.getByRole("navigation", { name: "Match analysis", exact: true });
  for (const [label, value] of [
    ["Moments", "moments"],
    ["Rallies", "rallies"],
    ["Shots", "shots"],
    ["Tactics", "tactics"],
    ["Court", "court"],
    ["Movement", "movement"],
    ["Head to head", "h2h"],
    ["Your pair", "pair"],
  ]) {
    await tabs.getByRole("button", { name: label, exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`tab=${value}`));
    await expect(page).toHaveURL(/who=P2/);
  }
  await expect(
    page.getByText("This analysis currently resolves two court-side identities", { exact: false }),
  ).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: "Show Far numbers", exact: true })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await expect(tabs.getByRole("button", { name: "Your pair", exact: true })).toHaveAttribute(
    "aria-current",
    "page",
  );

  // No trained perception models run in this fixture: missing analytics must remain empty.
  const analytics = await (await request.get(`/api/sessions/${id}/analytics`)).json();
  expect(analytics.rallies).toBe(0);
  expect(analytics.avg_rally_shots).toBeNull();
  expect((await (await request.get(`/api/sessions/${id}/highlights`)).json()).highlights).toEqual([]);
  await page.setViewportSize({ width: 390, height: 844 });
  await noHorizontalOverflow(page);
  await expect(page.getByRole("button", { name: "Full screen", exact: true })).toBeVisible();
  await page.screenshot({ path: "/tmp/bai-audit-frontend-narrow.png", fullPage: true });
  expect(errors).toEqual([]);
});

test("sign-in failure remains an actionable authentication boundary", async ({ page }) => {
  // This is deliberately a UI contract fixture. API authentication/CSRF has independent API tests.
  await page.route("**/api/auth/me", (route) =>
    route.fulfill({ json: { authenticated: false, auth_required: true, csrf: null } }),
  );
  await page.route("**/api/auth/login", (route) =>
    route.fulfill({ status: 401, json: { detail: "That passphrase is not correct" } }),
  );
  await page.goto("/matches");
  await expect(page.getByRole("heading", { name: "Sign in to Badminton AI" })).toBeVisible();
  await page.getByLabel("Passphrase").fill("invalid-test-passphrase");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(/passphrase/i);
  await expect(page.getByRole("heading", { name: "Your matches", exact: true })).toHaveCount(0);
});

test("an unknown match reports a missing record rather than displaying sample data", async ({ page }) => {
  await page.goto("/matches/DOESNOTEXIST");
  await expect(page.getByRole("alert")).toContainText(/not found/i);
  await expect(page.locator("video")).toHaveCount(0);
});

test("display preferences survive refresh and progress uses the recorded player catalogue", async ({
  page,
}) => {
  await page.goto("/settings");
  await page.getByRole("combobox", { name: "Appearance", exact: true }).selectOption("dark");
  await page.getByLabel("Reduce motion", { exact: true }).check();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.locator("html")).toHaveAttribute("data-reduced-motion", "true");
  await page.reload();
  await expect(page.getByRole("combobox", { name: "Appearance", exact: true })).toHaveValue("dark");
  await expect(page.getByLabel("Reduce motion", { exact: true })).toBeChecked();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await expect(page.locator("html")).toHaveAttribute("data-reduced-motion", "true");
  await page.goto("/progress");
  await expect(page.getByRole("heading", { name: "Your progress", exact: true })).toBeVisible();
  await expect(page.getByText("Viktor Axelsen", { exact: true })).toHaveCount(0);
  await page.goto("/matches");
  await page.getByLabel("Find a match", { exact: true }).fill("does not exist");
  await expect(page.getByRole("heading", { name: "No matching recordings", exact: true })).toBeVisible();
  await page.getByLabel("Find a match", { exact: true }).fill("Production integration match");
  await expect(page.getByRole("link", { name: "Production integration match", exact: true })).toBeVisible();
});
