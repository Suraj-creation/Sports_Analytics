import { act, render, screen } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { ev, SESSION, state } from "@/test/fixtures";
import { ScoreBug } from "./ScoreBug";

beforeEach(() => usePlayback.setState({ frame: 0, video: null }));

it("shows corroborated source names and scores without assigning user aliases", () => {
  const log = new EventLog();
  log.apply([
    ev("broadcast_score", 249, {
      payload: {
        rows: [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
        player_mapping: null,
      },
    }),
    ev("broadcast_score", 500, {
      payload: {
        rows: [
          { name: "ANTONSEN", points: 4 },
          { name: "FARHAN", points: 2 },
        ],
        player_mapping: null,
      },
    }),
  ]);
  const session = {
    ...SESSION,
    status: "analysed" as const,
    players: [
      { player_id: "P1" as const, name: "Sam" },
      { player_id: "P2" as const, name: "TAM" },
    ],
  };
  useSession.setState({ events: log, eventsVersion: log.version, session });
  act(() => usePlayback.setState({ frame: 300 }));
  render(<ScoreBug session={session} />);
  const bug = screen.getByTestId("score-bug");
  expect(bug).toHaveTextContent("ANTONSEN");
  expect(bug).toHaveTextContent("FARHAN");
  expect(bug).toHaveTextContent("Broadcast score");
  expect(bug).not.toHaveTextContent("Sam");
  expect(bug.textContent).toMatch(/ANTONSEN.*3.*FARHAN.*2/s);
  expect(bug.textContent).not.toMatch(/ANTONSEN.*4/s);
  act(() => usePlayback.setState({ frame: 500 }));
  expect(bug.textContent).toMatch(/ANTONSEN.*4/s);
});

it("does not show future source scores and labels an old observation", () => {
  const log = new EventLog();
  log.apply([
    ev("broadcast_score", 249, {
      payload: {
        rows: [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
      },
    }),
  ]);
  useSession.setState({
    events: log,
    eventsVersion: log.version,
    session: { ...SESSION, status: "analysed" },
  });
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Score unavailable");
  expect(screen.getByTestId("score-bug")).not.toHaveTextContent("ANTONSEN");
  act(() => usePlayback.setState({ frame: 249 + 30 * 20 }));
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Last read 20s ago");
});

it("keeps a newer human score correction over an older broadcast reading", () => {
  const log = new EventLog();
  const rally = ev("rally_end", 260, { status: "human_verified", seq: 20 });
  log.apply([
    ev("broadcast_score", 249, {
      seq: 10,
      payload: {
        rows: [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
      },
    }),
    rally,
    ev("point", 300, { seq: 21, parent_id: rally.event_id, payload: { state_after: state(5, 4) } }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  act(() => usePlayback.setState({ frame: 350 }));
  render(<ScoreBug session={SESSION} />);
  const bug = screen.getByTestId("score-bug");
  expect(bug).toHaveTextContent("Axelsen");
  expect(bug.textContent).toMatch(/Axelsen.*05.*Momota.*04/s);
  expect(bug).not.toHaveTextContent("Broadcast score");
});

it("ignores malformed source board rows", () => {
  const log = new EventLog();
  log.apply([ev("broadcast_score", 10, { payload: { rows: [null, { name: "FARHAN", points: 2 }] } })]);
  useSession.setState({
    events: log,
    eventsVersion: log.version,
    session: { ...SESSION, status: "analysed" },
  });
  act(() => usePlayback.setState({ frame: 50 }));
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Score unavailable");
});
