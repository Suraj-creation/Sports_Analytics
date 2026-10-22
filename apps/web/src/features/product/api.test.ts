import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api";
import { fetchOverview } from "./api";

afterEach(() => vi.unstubAllGlobals());
describe("catalogue transport", () => {
  it("preserves authorization failures instead of returning an empty catalogue", async () => {
    vi.stubGlobal(
      "fetch",
      async () => new Response(JSON.stringify({ detail: "Authentication required" }), { status: 401 }),
    );
    await expect(fetchOverview()).rejects.toMatchObject({ status: 401, message: "Authentication required" });
    await expect(fetchOverview()).rejects.toBeInstanceOf(ApiError);
  });
  it("rejects an incompatible response instead of rendering missing fields as zero", async () => {
    vi.stubGlobal("fetch", async () => new Response(JSON.stringify({ schema_version: 2, matches: [] })));
    await expect(fetchOverview()).rejects.toThrow("unsupported analytics response");
  });
  it("returns a valid empty response without manufacturing matches", async () => {
    vi.stubGlobal(
      "fetch",
      async () =>
        new Response(
          JSON.stringify({
            schema_version: 1,
            generated_at: "2026-10-23T00:00:00Z",
            matches: [],
            people: [],
            scope: { limit: 500, returned_matches: 0, truncated: false },
            progress: {
              named_players: 0,
              analysed_matches: 0,
              total_rallies: 0,
              active_play_s: 0,
              history: [],
              records: [],
            },
            capabilities: {
              doubles_individual_tracking: false,
              shot_speed: false,
              player_identity: "explicit_session_names",
            },
          }),
        ),
    );
    const result = await fetchOverview();
    expect(result.matches).toEqual([]);
    expect(result.progress.history).toEqual([]);
    expect(result.progress.analysed_matches).toBe(0);
  });
});
