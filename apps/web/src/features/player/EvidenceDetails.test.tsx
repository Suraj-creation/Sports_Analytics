import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { EventLog } from "@/lib/events";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { ev, SESSION } from "@/test/fixtures";
import { playEvidence } from "./clip";
import { EvidenceDetails } from "./EvidenceDetails";

describe("evidence directly below the player", () => {
  beforeEach(() => {
    usePlayback.getState().resetMedia();
    const events = new EventLog();
    events.apply([
      ev("stroke", 60, {
        event_id: "first",
        actors: { player_id: "P1", track_id: 1, opponent_id: "P2" },
        payload: { stroke: "serve" },
      }),
      ev("stroke", 100, {
        event_id: "second",
        actors: { player_id: "P2", track_id: 2, opponent_id: "P1" },
        payload: { stroke: "smash" },
      }),
      ev("rally_end", 60, { frame_end: 180, payload: { rally_no: 3, official: false, winner: null } }),
    ]);
    useSession.setState({ events, eventsVersion: 1 });
  });
  it("shows real event time, player and unresolved rally context", () => {
    usePlayback
      .getState()
      .selectEvidence({ start: 100, end: 145, label: "Smash", eventId: "second" }, { from: 70, to: 145 });
    usePlayback.getState().setFrame(100);
    render(<EvidenceDetails session={SESSION} />);
    expect(screen.getByText(/source frame 100/)).toHaveTextContent("Momota");
    expect(screen.getByText(/Rally 3 · Not counted/)).toHaveTextContent("Winner unresolved");
    expect(screen.getByText(/frames 70–145/)).toBeVisible();
    expect(screen.getByRole("button", { name: "Next shot" })).toBeDisabled();
  });
  it("navigates canonical shots and retains repeat requests at the same frame", () => {
    usePlayback.getState().setFrame(100);
    render(<EvidenceDetails session={SESSION} />);
    fireEvent.click(screen.getByRole("button", { name: "Previous shot" }));
    expect(usePlayback.getState().selection).toMatchObject({ start: 60, eventId: "first" });
    const listener = vi.fn();
    window.addEventListener("bai:play-clip", listener);
    act(() => {
      playEvidence(60, 100, "Serve", "first");
      playEvidence(60, 100, "Serve", "first");
    });
    expect(listener).toHaveBeenCalledTimes(2);
    window.removeEventListener("bai:play-clip", listener);
  });
});
