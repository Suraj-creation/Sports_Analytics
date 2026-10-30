import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ServerMsg } from "@/lib/socket";
import { ev, SESSION, state } from "@/test/fixtures";
import { usePlayback } from "@/stores/playback";

const sockets: { onMessage: (m: ServerMsg) => void; lastSeq: () => number; generation: () => string | undefined }[] = [];
vi.mock("@/lib/socket", () => ({
  SessionSocket: class {
    constructor(_id: string, onMessage: (m: ServerMsg) => void, lastSeq: () => number, _onState: unknown, generation: () => string | undefined = () => undefined) {
      sockets.push({ onMessage, lastSeq, generation });
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

  it("replaces old live results on analysis_reset while retaining media and the supplied manual court", () => {
    useSession.getState().open("s1");
    const sock = sockets[0]!;
    const manual = { H: [[1, 0, 20], [0, 1, 30], [0, 0, 1]], reprojection_error_px: 0, n_points: 4, source: "human" };
    sock.onMessage({ type: "hello", session: { ...SESSION, status: "analysed", meta: { analysis_generation: "old-run" } }, last_seq: 100 });
    sock.onMessage({ type: "events", generation: "old-run", events: [
      ev("stroke", 30, { event_id: "old-shot", seq: 100 }),
      ev("point", 20, { seq: 99, payload: { state_after: state(2, 1) } }),
    ] });
    sock.onMessage({ type: "tracks", window: { v: 1, from: 0, to: 40, shuttle: { f: [30], x: [10], y: [20], c: [0.9] }, players: {} } });
    usePlayback.setState({ selection: { start: 30, end: 30, label: "Old shot" } });
    sock.onMessage({ type: "analysis_reset", session_id: "s1", generation: "new-run", calibration: manual });
    const current = useSession.getState();
    expect(current.session?.media).toEqual(SESSION.media);
    expect(current.session?.meta.analysis_generation).toBe("new-run");
    expect(current.events.size).toBe(0);
    expect(current.events.lastSeq).toBe(0);
    expect(current.tracks.shuttle.size).toBe(0);
    expect(current.tracks.isCovered(30)).toBe(false);
    expect(current.state).toBeNull();
    expect(current.lastEvents).toEqual([]);
    expect(current.calibration).toEqual(manual);
    expect(usePlayback.getState().selection).toBeNull();
    expect(sock.lastSeq()).toBe(0);
    expect(sock.generation()).toBe("new-run");
    sock.onMessage({ type: "events", generation: "new-run", events: [ev("stroke", 30, { event_id: "new-shot", seq: 1 })] });
    expect(current.events.ofType("stroke").map((event) => event.event_id)).toEqual(["new-shot"]);
  });

  it("clears an obsolete generation on reconnect even when the new log sequence is higher", () => {
    useSession.getState().open("s1");
    const sock = sockets[0]!;
    sock.onMessage({ type: "hello", session: { ...SESSION, meta: { analysis_generation: "old-run" } }, last_seq: 100 });
    sock.onMessage({ type: "events", events: [ev("stroke", 30, { event_id: "old-shot", seq: 100 })] });
    sock.onMessage({ type: "hello", session: { ...SESSION, meta: { analysis_generation: "new-run" } }, last_seq: 200 });
    expect(useSession.getState().events.size).toBe(0);
    sock.onMessage({ type: "events", backlog: true, events: [ev("stroke", 30, { event_id: "new-shot", seq: 1 })] });
    expect(useSession.getState().events.ofType("stroke").map((event) => event.event_id)).toEqual(["new-shot"]);
  });

  it("clears legacy results when the server hello sequence rolls back", () => {
    useSession.getState().open("s1");
    const sock = sockets[0]!;
    sock.onMessage({ type: "hello", session: SESSION, last_seq: 100 });
    sock.onMessage({ type: "events", events: [ev("stroke", 30, { event_id: "old-shot", seq: 100 })] });
    sock.onMessage({ type: "hello", session: SESSION, last_seq: 10 });
    expect(useSession.getState().events.size).toBe(0);
    expect(sock.lastSeq()).toBe(0);
  });

  it("recovers a missed reset by reconnecting read-only from zero with the new generation", () => {
    const control = vi.spyOn(api, "control");
    useSession.getState().open("s1");
    const sock = sockets[0]!;
    sock.onMessage({ type: "hello", session: { ...SESSION, meta: { analysis_generation: "old-run" } }, last_seq: 100 });
    sock.onMessage({ type: "events", events: [ev("stroke", 30, { event_id: "old-shot", seq: 100 })] });
    sock.onMessage({ type: "events", generation: "new-run", events: [ev("stroke", 60, { event_id: "latest-shot", seq: 42 })] });
    expect(sockets).toHaveLength(2);
    const replay = sockets[1]!;
    expect(replay.lastSeq()).toBe(0);
    expect(replay.generation()).toBe("new-run");
    expect(useSession.getState().events.size).toBe(0);
    expect(useSession.getState().session?.media).toEqual(SESSION.media);
    replay.onMessage({ type: "hello", session: { ...SESSION, meta: { analysis_generation: "new-run" } }, last_seq: 42 });
    replay.onMessage({ type: "events", backlog: true, events: [
      ev("stroke", 30, { event_id: "first-shot", seq: 1 }),
      ev("stroke", 60, { event_id: "latest-shot", seq: 42 }),
    ] });
    expect(useSession.getState().events.ofType("stroke").map((event) => event.event_id)).toEqual(["first-shot", "latest-shot"]);
    expect(control).not.toHaveBeenCalled();
  });

  it("resyncs legacy live sequence-one replacement while retaining ordinary reconnect deltas", () => {
    useSession.getState().open("s1");
    const sock = sockets[0]!;
    sock.onMessage({ type: "hello", session: SESSION, last_seq: 100 });
    sock.onMessage({ type: "events", events: [ev("stroke", 30, { event_id: "old-shot", seq: 100 })] });
    sock.onMessage({ type: "hello", session: SESSION, last_seq: 120 });
    expect(useSession.getState().events.size).toBe(1);
    sock.onMessage({ type: "events", events: [ev("stroke", 30, { event_id: "replacement-shot", seq: 1 })] });
    expect(sockets).toHaveLength(2);
    expect(sockets[1]!.lastSeq()).toBe(0);
    expect(useSession.getState().events.size).toBe(0);
  });

});
