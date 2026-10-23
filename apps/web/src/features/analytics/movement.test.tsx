import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import type { Analytics, PlayerStats } from "@/lib/types";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { SessionAnalytics } from "./SessionAnalytics";

function renderMovement(distance: number | null, observed = 0) {
  const stats: PlayerStats = {
    points_won: 0,
    points_lost: 0,
    win_rate: null,
    winners: 0,
    errors_out: 0,
    errors_net: 0,
    strokes: {},
    smashes: 0,
    jump_smashes: 0,
    smash_points: 0,
    serves: 0,
    serve_points_won: 0,
    points_won_under_pressure: 0,
    distance_m: distance,
    distance_quality: {
      status: distance === null ? "unavailable" : "estimate",
      method: "accepted_segments",
      observed_s: observed,
      coverage: 0.5,
      reason: distance === null ? "Calibration did not support distance" : "Partial tracking estimate",
    },
  };
  const qc = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, retry: false } } });
  qc.setQueryData(["analytics", SESSION.session_id], { rallies: 0, players: { P1: stats } } as Analytics);
  qc.setQueryData(["movement-evidence", SESSION.session_id, "P1"], { total: 10 });
  useSession.setState({ events: new EventLog(), eventsVersion: 0, calibration: null });
  render(
    <QueryClientProvider client={qc}>
      <SessionAnalytics session={SESSION} player="P1" search={{ tab: "movement" }} />
    </QueryClientProvider>,
  );
}

describe("movement evidence availability", () => {
  it("withholds null distance, derived steps and rate instead of coercing null to zero", () => {
    renderMovement(null);
    expect(screen.getByText("Calibration did not support distance")).toBeVisible();
    expect(screen.queryByText("0 m")).not.toBeInTheDocument();
    expect(screen.queryByText(/NaN|Infinity|0 m\/min/)).not.toBeInTheDocument();
    expect(
      screen.getByText("Video distance does not measure steps; no validated stride is available"),
    ).toBeVisible();
  });
  it("uses the accepted tracking time rather than whole-rally time as the rate denominator", () => {
    renderMovement(10, 2);
    expect(screen.getByText("10 m")).toBeVisible();
    expect(screen.getByText("300 m/min")).toBeVisible();
    expect(screen.getByText("Partial tracking estimate")).toBeVisible();
  });
  it("preserves a measured stationary zero as zero", () => {
    renderMovement(0, 2);
    expect(screen.getByText("0 m")).toBeVisible();
    expect(screen.getByText("0 m/min")).toBeVisible();
  });
});
