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
  return {
    status: s.status,
    status_detail: s.status_detail,
    frontier_frame: s.frontier_frame,
    analysed_frames: s.analysed_frames,
    meta: s.meta,
  };
}

let lifecycle = 0;

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
    const active = ++lifecycle;
    get().socket?.close();
    const tracks = new TrackBuffer();
    const events = new EventLog();
    let revision = 0;
    set({
      tracks,
      events,
      session: null,
      state: null,
      status: null,
      calibration: null,
      lastEvents: [],
      eventsVersion: 0,
      tracksVersion: 0,
      analyticsVersion: 0,
      ingestProgress: null,
    });
    const reset = () => {
      tracks.clear();
      events.clear();
      set((s) => ({
        state: null,
        calibration: null,
        lastEvents: [],
        eventsVersion: events.version,
        tracksVersion: tracks.version,
        analyticsVersion: s.analyticsVersion + 1,
      }));
    };
    // `hello` can arrive before ffprobe has run (media: null); status messages don't carry media,
    // so fetch the session once when it's still missing — the player can't attach without it.
    let mediaFetch: Promise<void> | null = null;
    const ensureMedia = () => {
      if (mediaFetch || get().session?.media) return;
      mediaFetch = api
        .session(id)
        .then((full) => {
          if (!full.media || active !== lifecycle) return;
          set((s) => (s.session?.session_id === id ? { session: { ...full, ...pickLive(s.session) } } : {}));
        })
        .catch(() => {})
        .finally(() => {
          mediaFetch = null;
        });
    };
    const onMessage = (m: ServerMsg) => {
      if (active !== lifecycle) return;
      const incoming =
        m.analysis_revision ?? (m.type === "hello" ? (m.session.meta?.analysis_revision ?? 0) : revision);
      if (incoming < revision) return;
      if (incoming > revision || (m.type === "hello" && (m.reset || m.last_seq < events.lastSeq))) {
        reset();
        revision = incoming;
      }
      switch (m.type) {
        case "hello":
          set((s) => ({
            session: m.session,
            state: m.state ?? null,
            calibration: m.calibration ?? null,
            analyticsVersion: s.analyticsVersion + 1,
          }));
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
            analyticsVersion: evs.length ? s.analyticsVersion + 1 : s.analyticsVersion,
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
            ingestProgress: m.ingest_progress ?? s.ingestProgress,
            analyticsVersion:
              s.session?.status !== m.status || s.session?.frontier_frame !== m.frontier_frame
                ? s.analyticsVersion + 1
                : s.analyticsVersion,
            session: s.session
              ? {
                  ...s.session,
                  status: m.status,
                  status_detail: m.detail,
                  frontier_frame: m.frontier_frame,
                  analysed_frames: m.analysed_frames ?? s.session.analysed_frames,
                  meta: {
                    ...s.session.meta,
                    analysis_revision: revision,
                    ...(m.degraded ? { degraded: m.degraded } : {}),
                    ...(m.capabilities ? { capabilities: m.capabilities } : {}),
                  },
                }
              : s.session,
          }));
          if (m.status !== "created" && m.status !== "ingesting") ensureMedia();
          break;
        case "ingest":
          set({ ingestProgress: m.progress });
          break;
        case "state":
          if (m.state) set((s) => ({ state: m.state, analyticsVersion: s.analyticsVersion + 1 }));
          break;
        default:
          break;
      }
    };
    const socket = new SessionSocket(
      id,
      onMessage,
      () => events.lastSeq,
      (c) => {
        if (active === lifecycle) set({ connection: c });
      },
      () => revision,
    );
    set({ socket });
  },

  close: () => {
    lifecycle++;
    get().socket?.close();
    set({ socket: null, connection: "closed" });
  },
}));
