import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ServerMsg } from "@/lib/socket";
import { ev, SESSION } from "@/test/fixtures";

const sockets: { onMessage: (m: ServerMsg) => void }[] = [];
vi.mock("@/lib/socket", () => ({
  SessionSocket: class {
    constructor(_id: string, onMessage: (m: ServerMsg) => void) {
      sockets.push({ onMessage });
    }
    close() {}
  },
}));

const { useSession } = await import("./session");

afterEach(() => {
  sockets.length = 0;
  vi.restoreAllMocks();
});

describe("session store", () => {
  it("clears replaced analysis data and ignores late packets from the previous generation", () => {
    useSession.getState().open("s1");
    const send = sockets[0]!.onMessage;
    send({ type: "hello", session: SESSION, analysis_revision: 0 });
    send({ type: "events", analysis_revision: 0, events: [ev("stroke", 10, { seq: 99 })] });
    send({
      type: "tracks",
      analysis_revision: 0,
      window: { v: 1, from: 0, to: 20, shuttle: { f: [10], x: [2], y: [3], c: [0.9] }, players: {} },
    });
    send({
      type: "status",
      status: "analysing",
      detail: null,
      frontier_frame: 0,
      analysed_frames: 0,
      analysis_revision: 1,
      degraded: [{ stage: "pose", reason: "unavailable" }],
    });
    expect(useSession.getState().events.size).toBe(0);
    expect(useSession.getState().events.lastSeq).toBe(0);
    expect(useSession.getState().tracks.shuttle.size).toBe(0);
    send({ type: "events", analysis_revision: 0, events: [ev("stroke", 11)] });
    expect(useSession.getState().events.size).toBe(0);
    send({ type: "events", analysis_revision: 1, events: [ev("stroke", 12, { seq: 1 })] });
    expect(useSession.getState().events.lastSeq).toBe(1);
    send({
      type: "status",
      status: "analysed",
      frontier_frame: 119,
      analysed_frames: 120,
      analysis_revision: 1,
    });
    expect(useSession.getState().session?.analysed_frames).toBe(120);
    expect(useSession.getState().session?.meta.degraded).toEqual([{ stage: "pose", reason: "unavailable" }]);
  });

  it("ignores callbacks from closed or previously opened sessions", () => {
    useSession.getState().open("s1");
    const old = sockets[0]!.onMessage;
    useSession.getState().open("s2");
    old({ type: "hello", session: SESSION });
    expect(useSession.getState().session).toBeNull();
    const current = sockets[1]!.onMessage;
    useSession.getState().close();
    current({ type: "hello", session: { ...SESSION, session_id: "s2" } });
    expect(useSession.getState().session).toBeNull();
  });
  it("fetches media details once the probe has run (hello arrived before them)", async () => {
    const full = { ...SESSION, status: "ready_to_play" as const };
    const get = vi.spyOn(api, "session").mockResolvedValue(full);
    useSession.getState().open("s1");
    const sock = sockets[0];
    if (!sock) throw new Error("no socket");
    sock.onMessage({ type: "hello", session: { ...SESSION, media: null, status: "ingesting" } });
    expect(useSession.getState().session?.media).toBeNull();

    sock.onMessage({
      type: "status",
      status: "ready_to_play",
      detail: null,
      n_frames: 9000,
      frontier_frame: 0,
    });
    sock.onMessage({
      type: "status",
      status: "ready_to_play",
      detail: null,
      n_frames: 9000,
      frontier_frame: 0,
    });
    await vi.waitFor(() => expect(useSession.getState().session?.media?.n_frames).toBe(9000));
    expect(get).toHaveBeenCalledTimes(1); // one fetch even when several status messages arrive
    expect(useSession.getState().session?.status).toBe("ready_to_play");
  });

  it("does not refetch when media is already known", () => {
    const get = vi.spyOn(api, "session").mockResolvedValue(SESSION);
    useSession.getState().open("s1");
    const sock = sockets[0];
    if (!sock) throw new Error("no socket");
    sock.onMessage({ type: "hello", session: SESSION });
    sock.onMessage({
      type: "status",
      status: "analysing",
      detail: null,
      n_frames: 9000,
      frontier_frame: 120,
    });
    expect(get).not.toHaveBeenCalled();
    expect(useSession.getState().session?.frontier_frame).toBe(120);
  });
});
