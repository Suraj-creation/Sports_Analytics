import type { Page } from "@playwright/test";
import { expect, test } from "./fixtures";

async function expectScore(page: Page, p1: number, p2: number) {
  const bug = page.getByTestId("score-bug");
  await expect(bug).toBeVisible();
  const rows = bug.locator(".video-score-panel > div");
  await expect(rows).toHaveCount(2);
  await expect(rows.nth(0).locator("span").last()).toHaveText(String(p1));
  await expect(rows.nth(1).locator("span").last()).toHaveText(String(p2));
  await expect(bug).not.toContainText("Score unavailable");
  await expect(bug).not.toContainText("Score pending");
}

test("point decisions persist and synchronize through correction and reload", async ({ page, request }) => {
  const seeded = await request.post("/__test__/score-fixture");
  expect(seeded.status()).toBe(200);
  const fixture = (await seeded.json()) as {
    session_id: string;
    rally_event_ids: string[];
    frame: number;
    score: { P1: number; P2: number };
  };
  expect(fixture.score).toEqual({ P1: 1, P2: 1 });
  expect(fixture.rally_event_ids).toHaveLength(2);
  const base = `/api/sessions/${fixture.session_id}`;
  const persistedState = async () => (await (await request.get(`${base}/state`)).json()).state;
  const livePoints = async () =>
    (await (await request.get(`${base}/events?types=point`)).json()).events as {
      event_id: string;
      parent_id: string;
      payload: { winner: string; state_after: { score: { P1: number; P2: number } } };
      status: string;
    }[];
  expect((await persistedState()).score).toEqual({ P1: 1, P2: 1 });
  const initialPoints = await livePoints();
  expect(initialPoints).toHaveLength(2);
  expect(initialPoints.map((point) => point.payload.winner)).toEqual(["P1", "P2"]);
  expect(initialPoints.every((point) => point.status === "confirmed")).toBe(true);

  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`/sessions/${fixture.session_id}?f=${fixture.frame}`);
  await expect(page.getByText(`frame ${fixture.frame.toLocaleString()}`, { exact: true })).toBeVisible();
  await expectScore(page, 1, 1);

  // Use the normal command endpoint while the page stays open. The score display
  // only consumes socket events, so this assertion also verifies live delivery.
  const correction = {
    kind: "winner",
    rally_event_id: fixture.rally_event_ids[1],
    winner: "P1",
  };
  expect((await request.post(`${base}/corrections`, { data: correction })).status()).toBe(202);
  await expect.poll(async () => (await persistedState()).score).toEqual({ P1: 2, P2: 0 });
  await expectScore(page, 2, 0);
  const correctedPoints = await livePoints();
  expect(correctedPoints).toHaveLength(2);
  expect(correctedPoints.map((point) => point.payload.winner)).toEqual(["P1", "P1"]);
  expect(correctedPoints.at(-1)?.payload.state_after.score).toEqual({ P1: 2, P2: 0 });

  await page.reload();
  await expect(page.getByText(`frame ${fixture.frame.toLocaleString()}`, { exact: true })).toBeVisible();
  await expectScore(page, 2, 0);
  expect((await persistedState()).score).toEqual({ P1: 2, P2: 0 });
  expect(await livePoints()).toHaveLength(2);
  expect(errors).toEqual([]);
  await page.screenshot({ path: "test-results/screens/score-integrity-reloaded.png", fullPage: true });
});
