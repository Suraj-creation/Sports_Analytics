import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { ev, SESSION } from "@/test/fixtures";
import { LiveFeed } from "./LiveFeed";

it.each(["stroke", "rally_end"])("marks model-only %s as an estimate even with confirmed support", (type) => {
  const events = new EventLog();
  events.apply([
    ev(type, 120, {
      band: "confirmed",
      status: "confirmed",
      payload: { stroke: "smash", rally_no: 1, n_shots: 3 },
    }),
  ]);
  usePlayback.setState({ frame: 180, selection: null });
  useSession.setState({ events, eventsVersion: events.version });
  render(<LiveFeed session={SESSION} />);
  expect(screen.getByText("Estimate")).toBeInTheDocument();
  expect(screen.queryByText("Human reviewed")).not.toBeInTheDocument();
});

it.each(["stroke", "rally_end"])("keeps human-reviewed %s distinct from model support", (type) => {
  const events = new EventLog();
  events.apply([
    ev(type, 120, { status: "human_verified", payload: { stroke: "smash", rally_no: 1, n_shots: 3 } }),
  ]);
  usePlayback.setState({ frame: 180, selection: null });
  useSession.setState({ events, eventsVersion: events.version });
  render(<LiveFeed session={SESSION} />);
  expect(screen.getByText("Human reviewed")).toBeInTheDocument();
  expect(screen.queryByText("Estimate")).not.toBeInTheDocument();
});
