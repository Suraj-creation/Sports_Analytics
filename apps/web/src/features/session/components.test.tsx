import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ScoreBug } from "@/features/player/ScoreBug";
import { api } from "@/lib/api";
import { EventLog } from "@/lib/events";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { ev, point, SESSION, state } from "@/test/fixtures";
import { LiveFeed } from "./LiveFeed";
import { AskTab } from "./tabs/AskTab";

function withQuery(ui: ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{ui}</QueryClientProvider>;
}

function loadEvents(events: ReturnType<typeof ev>[]) {
  const log = new EventLog();
  log.apply(events);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
}

beforeEach(() => {
  usePlayback.setState({ frame: 0, video: null });
});

describe("ScoreBug", () => {
  it("shows the score as of the presented frame, not the latest analysed one", () => {
    const s0 = state(0, 0);
    const s1 = state(1, 0);
    const s2 = state(2, 0, { game_point: null });
    loadEvents([point(300, "P1", s0, s1), point(900, "P1", s1, s2)]);
    act(() => usePlayback.setState({ frame: 400 }));
    render(<ScoreBug session={SESSION} />);
    const bug = screen.getByTestId("score-bug");
    expect(bug).toHaveTextContent("Axelsen");
    expect(bug).toHaveTextContent("Momota");
    // P1 has 1 point at frame 400 — the 2nd point (frame 900) hasn't happened on screen yet
    expect(bug.textContent).toMatch(/Axelsen.*01.*Momota.*00/s);
    act(() => usePlayback.setState({ frame: 900 }));
    expect(bug.textContent).toMatch(/Axelsen.*02/s);
  });

  it("names game and match point", () => {
    const s0 = state(19, 18);
    const s1 = state(20, 18, { game_point: "P1" });
    loadEvents([point(100, "P1", s0, s1)]);
    act(() => usePlayback.setState({ frame: 150 }));
    render(<ScoreBug session={SESSION} />);
    expect(screen.getByText("Game point")).toBeInTheDocument();
  });
});

describe("LiveFeed", () => {
  it("lists only what the video has reached, newest first, and seeks on click", () => {
    const seek = vi.fn();
    usePlayback.setState({ seekFrame: seek });
    loadEvents([
      ev("rally_end", 100, {
        frame_end: 300,
        payload: { rally_no: 1, winner: "P1", n_shots: 7, outcome: "out" },
      }),
      ev("stroke", 700, {
        actors: { player_id: "P2", track_id: null, opponent_id: "P1" },
        payload: { stroke: "smash", subtype: "jump_smash" },
        band: "probable",
      }),
      ev("rally_end", 600, { frame_end: 800, payload: { rally_no: 2, winner: "P2", n_shots: 3 } }),
    ]);
    act(() => usePlayback.setState({ frame: 750 }));
    render(<LiveFeed session={SESSION} />);
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(2); // rally 2 ends at 800 — not reached yet
    expect(items[0]).toHaveTextContent("Jump smash");
    expect(items[0]).toHaveTextContent("probable");
    expect(items[1]).toHaveTextContent("Rally 1 · Axelsen wins");
    expect(items[1]).toHaveTextContent("shuttle landed out");
    fireEvent.click(screen.getByText(/Rally 1/));
    expect(seek).toHaveBeenCalledWith(70, 30); // one second before the rally starts
  });
});

describe("AskTab", () => {
  it("renders citations as numbered chips that seek the video", async () => {
    const seek = vi.fn();
    usePlayback.setState({ seekFrame: seek });
    vi.spyOn(api, "askProvider").mockResolvedValue({ available: true, provider: "anthropic", model: "m" });
    vi.spyOn(api, "ask").mockResolvedValue({
      text: "Axelsen won **rally 4** with a smash [[ev:e4]]. Smashes are fast [[kb:rules#2]].",
      citations: [
        { kind: "ev", ref: "e4", frame: 1200, type: "rally_end" },
        { kind: "kb", ref: "rules#2" },
      ],
      grounded: true,
      issues: [],
      provider: "anthropic",
      model: "m",
    });
    render(withQuery(<AskTab session={SESSION} />));
    fireEvent.change(screen.getByLabelText("Question"), { target: { value: "How did rally 4 end?" } });
    fireEvent.click(screen.getByRole("button", { name: "Ask" }));
    const chip = await screen.findByRole("button", { name: "1" });
    expect(screen.getByText("rally 4").tagName).toBe("STRONG");
    expect(screen.getByLabelText("background source")).toBeInTheDocument();
    fireEvent.click(chip);
    expect(seek).toHaveBeenCalledWith(1170, 30);
    await waitFor(() => expect(api.ask).toHaveBeenCalledWith("s1", "How did rally 4 end?", []));
  });
});
