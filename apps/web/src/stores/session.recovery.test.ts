import { afterEach, describe, expect, it, vi } from "vitest";
import type { ServerMsg } from "@/lib/socket";
import { ev, SESSION } from "@/test/fixtures";

const sockets: { message: (m: ServerMsg) => void }[] = [];
function socketAt(index: number) {
  const socket = sockets[index];
  if (!socket) throw new Error(`Missing test socket ${index}`);
  return socket;
}
vi.mock("@/lib/socket", () => ({
  SessionSocket: class {
    constructor(_id: string, message: (m: ServerMsg) => void) {
      sockets.push({ message });
    }
    close() {}
  },
}));
const { useSession } = await import("./session");

afterEach(() => {
  useSession.getState().close();
  sockets.length = 0;
});

describe("analysis lifecycle recovery", () => {
  it("ignores callbacks from a previous open or a closed session", () => {
    useSession.getState().open("s1");
    const old = socketAt(0);
    useSession.getState().open("s2");
    socketAt(1).message({ type: "hello", session: { ...SESSION, session_id: "s2" } });
    old.message({ type: "hello", session: SESSION });
    expect(useSession.getState().session?.session_id).toBe("s2");
    useSession.getState().close();
    socketAt(1).message({ type: "status", status: "failed", frontier_frame: 0 });
    expect(useSession.getState().session?.status).not.toBe("failed");
  });

  it("keeps runtime coverage and capability status in the authoritative session", () => {
    useSession.getState().open("s1");
    const socket = socketAt(0);
    socket.message({ type: "hello", session: SESSION });
    socket.message({
      type: "status",
      status: "analysing",
      frontier_frame: 100,
      analysed_frames: 101,
      analysis_revision: 3,
      degraded: [{ stage: "pose", reason: "missing" }],
      capabilities: { stroke: { status: "heuristic" } },
    });
    const session = useSession.getState().session;
    if (!session) throw new Error("Session missing after hello");
    expect(session.analysed_frames).toBe(101);
    expect(session.meta.analysis_revision).toBe(3);
    expect(session.meta.capabilities).toEqual({ stroke: { status: "heuristic" } });
    socket.message({ type: "status", status: "analysed", frontier_frame: 200, analysis_revision: 2 });
    expect(useSession.getState().session?.frontier_frame).toBe(100);
  });

  it("invalidates analytics when a stroke is corrected without a new rally or point", () => {
    useSession.getState().open("s1");
    const socket = socketAt(0);
    socket.message({ type: "hello", session: SESSION });
    const before = useSession.getState().analyticsVersion;
    socket.message({
      type: "events",
      events: [
        ev("stroke", 10, {
          event_id: "corrected",
          supersedes: "original",
          status: "corrected",
          seq: 2,
        }),
      ],
    });
    expect(useSession.getState().analyticsVersion).toBeGreaterThan(before);
  });
});
