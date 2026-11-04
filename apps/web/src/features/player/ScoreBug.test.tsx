import { act, render, screen } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import type { BaiEvent, Session } from "@/lib/types";
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

it("does not let a carried human correction freeze later video-time broadcast readings", () => {
  const log = new EventLog();
  const reviewed = ev("rally_end", 260, { status: "human_verified", seq: 100 });
  // Carried human decisions are appended after inference, so their sequence is
  // newer even though the decision belongs to an EARLIER video frame.
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
    ev("broadcast_score", 500, {
      seq: 20,
      payload: {
        rows: [
          { name: "ANTONSEN", points: 7 },
          { name: "FARHAN", points: 4 },
        ],
      },
    }),
    reviewed,
    ev("point", 300, { seq: 101, parent_id: reviewed.event_id, payload: { state_after: state(5, 4) } }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  act(() => usePlayback.setState({ frame: 350 }));
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug").textContent).toMatch(/Axelsen.*05.*Momota.*04/s);
  act(() => usePlayback.setState({ frame: 500 }));
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Broadcast score");
  expect(screen.getByTestId("score-bug").textContent).toMatch(/ANTONSEN.*7.*FARHAN.*4/s);
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

it("leaves a provisional point unavailable instead of rendering it as an accepted score", () => {
  const log = new EventLog();
  log.apply([
    ev("point", 100, {
      status: "provisional",
      payload: { state_before: state(0, 0), state_after: state(1, 0) },
    }),
  ]);
  useSession.setState({
    events: log,
    eventsVersion: log.version,
    session: { ...SESSION, status: "analysed" },
  });
  usePlayback.setState({ frame: 100 });
  render(<ScoreBug session={SESSION} />);
  expect(screen.getByTestId("score-bug")).toHaveTextContent("Score unavailable");
  expect(screen.queryByText("serving")).not.toBeInTheDocument();
});

it("does not let a provisional point restore an older broadcast score over an accepted point", () => {
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
    ev("point", 300, { payload: { state_before: state(3, 2), state_after: state(4, 2) } }),
    ev("point", 350, {
      status: "provisional",
      payload: { state_before: state(4, 2), state_after: state(4, 3) },
    }),
  ]);
  useSession.setState({ events: log, eventsVersion: log.version, session: SESSION });
  usePlayback.setState({ frame: 400 });
  render(<ScoreBug session={SESSION} />);
  const bug = screen.getByTestId("score-bug");
  expect(bug.textContent).toMatch(/Axelsen.*04.*Momota.*02/s);
  expect(bug).not.toHaveTextContent("Broadcast score");
});

type BroadcastRow = { name: string; points: number };

function corroboratedBoard(frame: number, rows: BroadcastRow[], over: Partial<BaiEvent> = {}): BaiEvent {
  return {
    ...ev("broadcast_score", frame, {
      ...over,
      payload: {
        rows,
        player_mapping: null,
        source: "broadcast_ocr",
        confirmation: "two_distinct_observations",
        ...over.payload,
      },
    }),
    evidence: [{ kind: "score_ocr", frames: [frame - 10, frame] }],
  };
}

function sourceSession(matchFormat: "singles" | "doubles"): Session {
  return {
    ...SESSION,
    status: "analysed",
    players: [
      { player_id: "P1", name: "Sam" },
      { player_id: "P2", name: "TAM" },
    ],
    roster: {
      match_format: matchFormat,
      teams: [],
      participants: Array.from({ length: matchFormat === "doubles" ? 4 : 2 }, (_, index) => ({
        participant_id: `unbound-person-${index}`,
        name: null,
        team_id: null,
      })),
    },
  };
}

function renderSourceBoards(events: BaiEvent[], frame: number, session = sourceSession("singles")) {
  const log = new EventLog();
  log.apply(events);
  useSession.setState({ events: log, eventsVersion: log.version, session });
  usePlayback.setState({ frame });
  render(<ScoreBug session={session} />);
  return log;
}

it.each(["singles", "doubles"] as const)(
  "shows a named %s source +1 without binding broadcast rows to scoring aliases",
  (format) => {
    const names: [string, string] =
      format === "singles" ? ["ANTONSEN", "FARHAN"] : ["GOH / IZZUDDIN", "FAJAR / RIAN"];
    const before = corroboratedBoard(249, [
      { name: names[0], points: 3 },
      { name: names[1], points: 2 },
    ]);
    const after = corroboratedBoard(500, [
      { name: names[0], points: 4 },
      { name: names[1], points: 2 },
    ]);
    // Delivery order and sequence do not override the presented video timeline.
    const log = renderSourceBoards([after, before], 500, sourceSession(format));

    const change = screen.getByRole("status", { name: "Observed broadcast increment" });
    expect(change).toHaveTextContent(`${names[0]} +1`);
    expect(change).toHaveTextContent("Observed broadcast");
    expect(change).not.toHaveTextContent("Sam");
    expect(change).not.toHaveTextContent("TAM");
    expect(change).not.toHaveTextContent("Point won");
    expect(log.ofType("point")).toHaveLength(0);
    expect(log.get(after.event_id)?.payload.player_mapping).toBeNull();
  },
);

it("identifies the second source row when only that row gains one", () => {
  renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 3 },
      ]),
    ],
    500,
  );
  expect(screen.getByRole("status", { name: "Observed broadcast increment" })).toHaveTextContent("FARHAN +1");
});

it("derives source increments at the presented canonical frame when seeking backward and forward", () => {
  renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: "ANTONSEN", points: 4 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(700, [
        { name: "ANTONSEN", points: 4 },
        { name: "FARHAN", points: 3 },
      ]),
    ],
    450,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
  act(() => usePlayback.setState({ frame: 500 }));
  expect(screen.getByRole("status", { name: "Observed broadcast increment" })).toHaveTextContent("ANTONSEN +1");
  act(() => usePlayback.setState({ frame: 700 }));
  expect(screen.getByRole("status", { name: "Observed broadcast increment" })).toHaveTextContent("FARHAN +1");
  act(() => usePlayback.setState({ frame: 550 }));
  expect(screen.getByRole("status", { name: "Observed broadcast increment" })).toHaveTextContent("ANTONSEN +1");
  act(() => usePlayback.setState({ frame: 300 }));
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
});

const nonIncrementBroadcasts: { reason: string; points: [number, number]; names: [string, string] }[] = [
  { reason: "a two-point jump", points: [5, 2], names: ["ANTONSEN", "FARHAN"] },
  { reason: "both rows changing", points: [4, 3], names: ["ANTONSEN", "FARHAN"] },
  { reason: "a game reset", points: [0, 0], names: ["ANTONSEN", "FARHAN"] },
  { reason: "a score decrement", points: [2, 2], names: ["ANTONSEN", "FARHAN"] },
  { reason: "an unchanged board", points: [3, 2], names: ["ANTONSEN", "FARHAN"] },
  { reason: "reordered row identities", points: [4, 2], names: ["FARHAN", "ANTONSEN"] },
  { reason: "a changed source identity", points: [4, 2], names: ["ANOTHER PLAYER", "FARHAN"] },
  { reason: "duplicate source identities", points: [4, 2], names: ["ANTONSEN", "ANTONSEN"] },
];

it.each(nonIncrementBroadcasts)("does not call $reason a one-point source increment", ({ points, names }) => {
  renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: names[0], points: points[0] },
        { name: names[1], points: points[1] },
      ]),
    ],
    500,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
});

const incompleteBroadcastEvidence: {
  reason: string;
  previous: Partial<BaiEvent>;
  current: Partial<BaiEvent>;
}[] = [
  { reason: "a provisional current reading", previous: {}, current: { status: "provisional" } },
  { reason: "a provisional previous reading", previous: { status: "provisional" }, current: {} },
  { reason: "an uncorroborated current reading", previous: {}, current: { payload: { confirmation: null } } },
  { reason: "an uncorroborated previous reading", previous: { payload: { confirmation: null } }, current: {} },
  { reason: "a non-broadcast current source", previous: {}, current: { payload: { source: "unknown" } } },
  { reason: "a non-broadcast previous source", previous: { payload: { source: "unknown" } }, current: {} },
];

it.each(incompleteBroadcastEvidence)("withholds a source increment for $reason", ({ previous, current }) => {
  renderSourceBoards(
    [
      corroboratedBoard(
        249,
        [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
        previous,
      ),
      corroboratedBoard(
        500,
        [
          { name: "ANTONSEN", points: 4 },
          { name: "FARHAN", points: 2 },
        ],
        current,
      ),
    ],
    500,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
});

it("does not infer a source increment from a single observation or numeric aliases", () => {
  renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "1", points: 3 },
        { name: "2", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: "1", points: 4 },
        { name: "2", points: 2 },
      ]),
    ],
    249,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
  act(() => usePlayback.setState({ frame: 500 }));
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
  expect(screen.getByTestId("score-bug")).not.toHaveTextContent("Sam");
});

it("requires different canonical frames for the two broadcast observations", () => {
  renderSourceBoards(
    [
      corroboratedBoard(500, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: "ANTONSEN", points: 4 },
        { name: "FARHAN", points: 2 },
      ]),
    ],
    500,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
});

it("withdraws the source increment when its changed board is corrected", () => {
  const current = corroboratedBoard(500, [
    { name: "ANTONSEN", points: 4 },
    { name: "FARHAN", points: 2 },
  ]);
  const log = renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      current,
    ],
    500,
  );
  act(() => {
    log.apply([
      corroboratedBoard(
        500,
        [
          { name: "ANTONSEN", points: 3 },
          { name: "FARHAN", points: 2 },
        ],
        { supersedes: current.event_id },
      ),
    ]);
    useSession.setState({ eventsVersion: log.version });
  });
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
  expect(screen.getByTestId("score-bug").textContent).toMatch(/ANTONSEN.*3.*FARHAN.*2/s);
});

it("does not retain a broadcast increment beside a newer accepted score", () => {
  renderSourceBoards(
    [
      corroboratedBoard(249, [
        { name: "ANTONSEN", points: 3 },
        { name: "FARHAN", points: 2 },
      ]),
      corroboratedBoard(500, [
        { name: "ANTONSEN", points: 4 },
        { name: "FARHAN", points: 2 },
      ]),
      ev("point", 600, { payload: { state_before: state(4, 2), state_after: state(5, 2) } }),
    ],
    650,
  );
  expect(screen.queryByRole("status", { name: "Observed broadcast increment" })).not.toBeInTheDocument();
  expect(screen.getByTestId("score-bug")).not.toHaveTextContent("Broadcast score");
  expect(screen.getByTestId("score-bug").textContent).toMatch(/Sam.*05.*TAM.*02/s);
});
