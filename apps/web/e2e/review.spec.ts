import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { decode } from "@msgpack/msgpack";
import { expect, test } from "./fixtures";

test("four-person review, measured pair positions, rackets, service setup and revocation", async ({
  page,
  request,
}) => {
  const clip = await readFile(fileURLToPath(new URL("./.tmp/clip.mp4", import.meta.url)));
  // Third source digest: production.spec uses one free atom, smoke uses the original.
  const marker = Buffer.from([0, 0, 0, 8, 0x66, 0x72, 0x65, 0x65]);
  const response = await request.post("/api/sessions", {
    multipart: {
      file: {
        name: "review-workflow.mp4",
        mimeType: "video/mp4",
        buffer: Buffer.concat([clip, marker, marker]),
      },
      title: "Four-player review fixture",
      match_format: "doubles",
    },
  });
  expect(response.status()).toBe(201);
  const session = await response.json();
  const base = `/api/sessions/${session.session_id}`;
  await expect
    .poll(async () => (await (await request.get(base)).json()).status, { timeout: 90_000 })
    .toBe("analysed");
  expect((await request.post(`/__test__/review-fixture/${session.session_id}`)).status()).toBe(200);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto(`/matches/${session.session_id}?tab=pair&f=30`);
  await page.getByText("Visual track observations", { exact: true }).click();
  const panel = page.getByRole("region", { name: "Player identity review" });
  // A section with aria-label is a named region in the browser accessibility tree.
  for (let i = 0; i < 4; i++) {
    await panel
      .getByRole("combobox", { name: "Observed track", exact: true })
      .selectOption({ label: `Track ${i} · frame 1` });
    await panel
      .getByRole("combobox", { name: "Roster participant", exact: true })
      .selectOption(`person-${i}`);
    await panel.getByLabel("Through frame", { exact: true }).fill("100");
    await panel.getByRole("button", { name: "Confirm player interval", exact: true }).click();
    await expect(panel.getByRole("button", { name: "Revoke player interval", exact: true })).toHaveCount(
      i + 1,
    );
  }
  for (let i = 0; i < 4; i++) {
    await panel.getByRole("button", { name: `Confirm hitter at frame ${30 + i}`, exact: true }).click();
    await expect(panel.getByRole("button", { name: "Revoke hitter review", exact: true })).toHaveCount(i + 1);
  }
  const individual = await (await request.get(`${base}/individual-analytics`)).json();
  expect(individual.accounting.attributed_shots).toBe(4);
  expect(individual.pairs.T1.observed_frames).toBeGreaterThan(0);
  expect(individual.participants["person-3"].movement.distance_m).toBeGreaterThan(0.5);
  expect(individual.participants["person-3"].movement.travel.latest.heading_deg).toBe(0);
  await expect(page.getByText("Alice & Bob", { exact: true })).toBeVisible();
  const trackWindow = await request.get(`${base}/tracks?from=30&to=33`);
  expect(trackWindow.status()).toBe(200);
  const wire = decode(await trackWindow.body()) as { rackets: { f: number[] } };
  expect(wire.rackets.f).toHaveLength(16);
  const service = page.getByRole("region", { name: "Doubles service order" });
  await service.getByRole("combobox", { name: "Opening server", exact: true }).selectOption("person-0");
  await service.getByRole("combobox", { name: "Opening receiver", exact: true }).selectOption("person-2");
  await service.getByRole("button", { name: "Set opening service order at 0–0", exact: true }).click();
  await expect(service.getByText("Alice serves to Cara · right court", { exact: true })).toBeVisible();
  await expect(page.getByText("0 unassigned of 4 linked shots.", { exact: true })).toBeVisible();
  await page.screenshot({ path: "test-results/screens/four-player-reviewed.png", fullPage: true });
  await panel.getByRole("button", { name: "Revoke player interval", exact: true }).first().click();
  await expect
    .poll(
      async () =>
        (await (await request.get(`${base}/individual-analytics`)).json()).accounting.attributed_shots,
    )
    .toBe(3);
  await expect(panel.getByRole("button", { name: "Revoke player interval", exact: true })).toHaveCount(3);
  await expect(page.getByText("1 unassigned of 4 linked shots.", { exact: true })).toBeVisible();
  expect(errors).toEqual([]);
  await page.screenshot({ path: "test-results/screens/four-player-review.png", fullPage: true });
});
