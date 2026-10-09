import { decode, encode } from "@msgpack/msgpack";

export type ServerMsg = { type: string; [k: string]: any };

/**
 * Session WebSocket with automatic reconnect and lossless resume (`last_seq`).
 * Frames are msgpack (binary); see apps/api/src/bai_api/ws.py.
 */
export class SessionSocket {
  private ws: WebSocket | null = null;
  private closed = false;
  private retry = 0;
  private lastPlayheadSent = 0;
  private pendingPlayhead: { frame: number; playing: boolean } | null = null;
  private timer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly sessionId: string,
    private readonly onMessage: (m: ServerMsg) => void,
    private readonly lastSeq: () => number,
    private readonly onState: (s: "connecting" | "open" | "closed") => void = () => {},
  ) {
    this.connect();
  }

  private url(): string {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${location.host}/ws/sessions/${this.sessionId}?last_seq=${this.lastSeq()}`;
  }

  private connect(): void {
    if (this.closed) return;
    this.onState("connecting");
    const ws = new WebSocket(this.url());
    ws.binaryType = "arraybuffer";
    ws.onopen = () => {
      this.retry = 0;
      this.onState("open");
    };
    ws.onmessage = (ev) => {
      try {
        const msg = ev.data instanceof ArrayBuffer ? decode(new Uint8Array(ev.data)) : JSON.parse(ev.data);
        if (msg && typeof msg === "object") {
          const m = msg as ServerMsg;
          if (m.type === "tracks" && m.bin instanceof Uint8Array) m.window = decode(m.bin);
          this.onMessage(m);
        }
      } catch (e) {
        console.warn("bad frame", e);
      }
    };
    ws.onclose = () => {
      this.onState("closed");
      if (this.closed) return;
      const delay = Math.min(10_000, 400 * 2 ** this.retry++);
      this.timer = setTimeout(() => this.connect(), delay);
    };
    this.ws = ws;
  }

  private send(msg: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(encode(msg));
  }

  /** Throttled: the engine only needs ~4 playhead updates per second to prioritise work. */
  playhead(frame: number, playing: boolean): void {
    const now = performance.now();
    if (now - this.lastPlayheadSent > 250) {
      this.send({ type: "playhead", frame, playing });
      this.lastPlayheadSent = now;
      this.pendingPlayhead = null;
    } else {
      this.pendingPlayhead = { frame, playing };
    }
  }

  flushPlayhead(): void {
    if (this.pendingPlayhead) {
      this.send({ type: "playhead", ...this.pendingPlayhead });
      this.pendingPlayhead = null;
    }
  }

  seek(frame: number): void {
    this.send({ type: "seek", frame });
  }

  requestTracks(from: number, to: number): void {
    this.send({ type: "tracks", from, to });
  }

  close(): void {
    this.closed = true;
    if (this.timer) clearTimeout(this.timer);
    this.ws?.close();
  }
}
