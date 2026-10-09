import { create } from "zustand";
import { api } from "@/lib/api";
import { EventLog } from "@/lib/events";
import { type ServerMsg, SessionSocket } from "@/lib/socket";
import { TrackBuffer } from "@/lib/tracks";
import type { BaiEvent, Calibration, MatchState, Session, StatusMsg } from "@/lib/types";

/**
 * Live state of the open session. Heavy, high-rate data (tracks, events) lives in mutable
 * buffers; the store only carries version counters so React re-renders on *change*, never
 * per video frame. The overlay reads the buffers directly inside requestVideoFrameCallback.
 */
interface SessionStore {
  session: Session | null;
  state: MatchState | null;
  status: StatusMsg | null;
  calibration: Calibration | null;
  connection: "connecting" | "open" | "closed";
  eventsVersion: number;
  tracksVersion: number;
  analyticsVersion: number;
  ingestProgress: number | null;
  lastEvents: BaiEvent[]; // most recent appended batch (live feed)
  tracks: TrackBuffer;
  events: EventLog;
  socket: SessionSocket | null;
  open: (id: string) => void;
  close: () => void;
}

/** Fields the live socket keeps fresher than a REST snapshot. */
function pickLive(s: Session): Partial<Session> {
  return { status: s.status, status_detail: s.status_detail, frontier_frame: s.frontier_frame };
}

export const useSession = create<SessionStore>((set, get) => ({
  session: null,
  state: null,
  status: null,
  calibration: null,
  connection: "closed",
  eventsVersion: 0,
  tracksVersion: 0,
  analyticsVersion: 0,
  ingestProgress: null,
  lastEvents: [],
  tracks: new TrackBuffer(),
  events: new EventLog(),
  socket: null,

  open: (id) => {
    get().socket?.close();
    const tracks = new TrackBuffer();
    const events = new EventLog();
    set({ tracks, events, session: null, state: null, status: null, calibration: null, lastEvents: [] });
    // `hello` can arrive before ffprobe has run (media: null); status messages don't carry media,
    // so fetch the session once when it's still missing — the player can't attach without it.
    let mediaFetch: Promise<void> | null = null;
    const ensureMedia = () => {
      if (mediaFetch || get().session?.media) return;
      mediaFetch = api
        .session(id)
        .then((full) => {
          if (!full.media) return;
          set((s) => (s.session?.session_id === id ? { session: { ...full, ...pickLive(s.session) } } : {}));
        })
        .catch(() => {})
        .finally(() => {
          mediaFetch = null;
        });
    };
    const onMessage = (m: ServerMsg) => {
      switch (m.type) {
        case "hello":
          set({ session: m.session, state: m.state ?? null, calibration: m.calibration ?? null });
          break;
        case "events": {
          const evs = m.events as BaiEvent[];
          events.apply(evs);
          const cal = evs.filter((e) => e.type === "calibration").pop();
          const point = evs.filter((e) => e.type === "point").pop();
          set((s) => ({
            eventsVersion: events.version,
            lastEvents: m.backlog ? s.lastEvents : evs,
            calibration: cal ? (cal.payload as Calibration) : s.calibration,
            state: point ? (point.payload.state_after as MatchState) : s.state,
            analyticsVersion: evs.some((e) => e.type === "rally_end" || e.type === "point")
              ? s.analyticsVersion + 1
              : s.analyticsVersion,
          }));
          break;
        }
        case "tracks":
          if (m.window) {
            tracks.ingest(m.window);
            set({ tracksVersion: tracks.version });
          }
          break;
        case "status":
          set((s) => ({
            status: m as StatusMsg,
            session: s.session
              ? { ...s.session, status: m.status, status_detail: m.detail, frontier_frame: m.frontier_frame }
              : s.session,
          }));
          if (m.status !== "created" && m.status !== "ingesting") ensureMedia();
          break;
        case "ingest":
          set({ ingestProgress: m.progress });
          break;
        case "state":
          if (m.state) set({ state: m.state });
          break;
        default:
          break;
      }
    };
    const socket = new SessionSocket(
      id,
      onMessage,
      () => events.lastSeq,
      (c) => set({ connection: c }),
    );
    set({ socket });
  },

  close: () => {
    get().socket?.close();
    set({ socket: null, connection: "closed" });
  },
}));
