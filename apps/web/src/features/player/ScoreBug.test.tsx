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

it("shows an accepted automatic point while an older OCR reading remains unchanged", () => {
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
    ev("point", 300, { payload: { state_after: state(4, 2) } }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  act(() => usePlayback.setState({ frame: 350 }));
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug").textContent).toMatch(/Axelsen.*04.*Momota.*02/s);
  expect(screen.getByTestId("score-bug")).not.toHaveTextContent("Broadcast score");
});

it("does not revert a human-corrected score when the next automatic point arrives", () => {
  const log = new EventLog();
  const reviewed = ev("rally_end", 260, { status: "human_verified" });
  log.apply([
    ev("broadcast_score", 249, {
      payload: {
        rows: [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
      },
    }),
    reviewed,
    ev("point", 300, { parent_id: reviewed.event_id, payload: { state_after: state(5, 4) } }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  act(() => usePlayback.setState({ frame: 350 }));
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug").textContent).toMatch(/Axelsen.*05.*Momota.*04/s);
  act(() => {
    log.apply([ev("point", 400, { payload: { state_after: state(6, 4) } })]);
    useSession.setState({ eventsVersion: log.version });
    usePlayback.setState({ frame: 450 });
  });
  expect(screen.getByTestId("score-bug").textContent).toMatch(/Axelsen.*06.*Momota.*04/s);
  expect(screen.getByTestId("score-bug")).not.toHaveTextContent("Broadcast score");
  act(() => {
    log.apply([
      ev("broadcast_score", 500, {
        payload: {
          rows: [
            { name: "ANTONSEN", points: 7 },
            { name: "FARHAN", points: 4 },
          ],
        },
      }),
    ]);
    useSession.setState({ eventsVersion: log.version });
    usePlayback.setState({ frame: 500 });
  });
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Broadcast score");
  expect(screen.getByTestId("score-bug").textContent).toMatch(/ANTONSEN.*7.*FARHAN.*4/s);
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

it("shows a seeded score without inventing an unknown opening server", () => {
  const log = new EventLog();
  log.apply([
    ev("point", 100, {
      payload: {
        state_before: { ...state(8, 3), server_known: false },
        state_after: { ...state(9, 3), server_known: true },
      },
    }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  act(() => usePlayback.setState({ frame: 30 }));
  render(<ScoreBug session={SESSION} />);
  expect(screen.queryByText("serving")).not.toBeInTheDocument();
  act(() => usePlayback.setState({ frame: 100 }));
  expect(screen.getByText("serving")).toBeInTheDocument();
});
