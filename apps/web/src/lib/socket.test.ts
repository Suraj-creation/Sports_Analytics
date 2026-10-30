import { afterEach, expect, it, vi } from "vitest";
import { SessionSocket } from "./socket";
const opened: FakeWebSocket[] = [];
class FakeWebSocket {
  static OPEN = 1;
  readyState = 0;
  binaryType = "";
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  constructor(readonly url: string) { opened.push(this); }
  close() {}
  send() {}
}
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); opened.length = 0; });
it("resumes with the current analysis generation and cursor after a reconnect", () => {
  vi.useFakeTimers();
  vi.stubGlobal("WebSocket", FakeWebSocket);
  let generation = "old-run";
  let seq = 100;
  const socket = new SessionSocket("s1", vi.fn(), () => seq, vi.fn(), () => generation);
  expect(new URL(opened[0]!.url).searchParams.get("generation")).toBe("old-run");
  opened[0]!.onclose?.();
  generation = "new-run";
  seq = 0;
  vi.advanceTimersByTime(400);
  const resumed = new URL(opened[1]!.url);
  expect(resumed.searchParams.get("generation")).toBe("new-run");
  expect(resumed.searchParams.get("last_seq")).toBe("0");
  socket.close();
});
it("ignores queued messages after its socket was deliberately replaced", () => {
  vi.stubGlobal("WebSocket", FakeWebSocket);
  const receive = vi.fn();
  const socket = new SessionSocket("s1", receive, () => 0);
  socket.close();
  opened[0]!.onmessage?.({ data: JSON.stringify({ type: "events", events: [] }) });
  expect(receive).not.toHaveBeenCalled();
});
