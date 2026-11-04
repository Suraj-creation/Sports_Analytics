import { afterEach, describe, expect, it, vi } from "vitest";
import type { ServerMsg } from "@/lib/socket";
import { ev, SESSION, state } from "@/test/fixtures";

const sockets: { message: (message: ServerMsg) => void }[] = [];
vi.mock("@/lib/socket", () => ({
  SessionSocket: class {
    constructor(_id: string, message: (message: ServerMsg) => void) {
      sockets.push({ message });
    }
    close() {}
  },
}));
const { useSession } = await import("./session");

function openSession() {
  useSession.getState().open("s1");
  const socket = sockets.at(-1);
  if (!socket) throw new Error("Missing test socket");
  socket.message({ type: "hello", session: SESSION, last_seq: 0 });
  return socket;
}

afterEach(() => {
  useSession.getState().close();
  sockets.length = 0;
});

describe("live score projection", () => {
  it("does not replace a newer score with an older point delivered late", () => {
    const socket = openSession();
    socket.message({
      type: "events",
      events: [ev("point", 200, { seq: 2, payload: { state_after: state(1, 1) } })],
    });
    socket.message({
      type: "events",
      backlog: true,
      events: [ev("point", 100, { seq: 1, payload: { state_after: state(1, 0) } })],
    });
    expect(useSession.getState().state?.score).toEqual({ P1: 1, P2: 1 });
  });

  it("does not replace the accepted score with a provisional point", () => {
    const socket = openSession();
    socket.message({
      type: "events",
      events: [ev("point", 100, { seq: 1, payload: { state_after: state(1, 0) } })],
    });
    socket.message({
      type: "events",
      events: [ev("point", 200, { seq: 2, status: "provisional", payload: { state_after: state(1, 1) } })],
    });
    expect(useSession.getState().state?.score).toEqual({ P1: 1, P2: 0 });
  });

  it("retains the regenerated score when refold retractions arrive after replacements", () => {
    const socket = openSession();
    const original = ev("point", 100, {
      event_id: "original",
      seq: 1,
      payload: { state_after: state(1, 0) },
    });
    socket.message({ type: "events", events: [original] });
    socket.message({
      type: "events",
      events: [ev("point", 100, { seq: 2, payload: { state_after: state(0, 1) } })],
    });
    socket.message({
      type: "events",
      events: [ev("point", 100, { seq: 3, status: "retracted", supersedes: original.event_id })],
    });
    expect(useSession.getState().state?.score).toEqual({ P1: 0, P2: 1 });
  });

  it("clears the score when its only accepted point is retracted", () => {
    const socket = openSession();
    const original = ev("point", 100, {
      event_id: "original",
      seq: 1,
      payload: { state_after: state(1, 0) },
    });
    socket.message({ type: "events", events: [original] });
    socket.message({
      type: "events",
      events: [ev("point", 100, { seq: 2, status: "retracted", supersedes: original.event_id })],
    });
    expect(useSession.getState().state).toBeNull();
  });

  it("does not revive a superseded point when its original is replayed", () => {
    const socket = openSession();
    const original = ev("point", 100, {
      event_id: "original",
      seq: 1,
      payload: { state_after: state(1, 0) },
    });
    socket.message({
      type: "events",
      events: [
        ev("point", 100, {
          seq: 2,
          status: "corrected",
          supersedes: original.event_id,
          payload: { state_after: state(0, 1) },
        }),
      ],
    });
    socket.message({ type: "events", backlog: true, events: [original] });
    expect(useSession.getState().state?.score).toEqual({ P1: 0, P2: 1 });
  });

  it("does not let a delayed state message overwrite newer durable point evidence", () => {
    const socket = openSession();
    socket.message({
      type: "events",
      events: [ev("point", 200, { seq: 2, payload: { state_after: state(1, 1) } })],
    });
    socket.message({ type: "state", state: state(1, 0) });
    expect(useSession.getState().state?.score).toEqual({ P1: 1, P2: 1 });
  });
});
