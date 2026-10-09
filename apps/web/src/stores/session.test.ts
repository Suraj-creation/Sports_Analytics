import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ServerMsg } from "@/lib/socket";
import { SESSION } from "@/test/fixtures";

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
