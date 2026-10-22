import { create } from "zustand";
import type { PlayerId } from "./data/types";

export type Theme = "system" | "light" | "dark";

export interface ConsentItem {
  id: string;
  label: string;
  consequence: string;
  on: boolean;
  blockedReason?: string;
}

/** A correction the player made to the event log. Mirrors the engine's correction kinds. */
export interface Correction {
  id: string;
  matchId: string;
  rallyNo: number;
  kind: "confirm_winner" | "change_winner" | "not_counted" | "counted" | "match_start";
  summary: string;
  /** What else moved as a result — the refold is the part people do not expect. */
  knockOn: string;
  at: number;
}

/**
 * A practice focus. The status ladder comes from the Front-End Blueprint §7.11:
 * reviewed → practised → seen again in play. A step is never skipped, and watching a
 * clip never counts as having practised something.
 */
export type FocusStatus = "reviewed" | "practised" | "seen_again";

export interface Focus {
  id: string;
  title: string;
  why: string;
  matchId: string;
  frame: number | null;
  status: FocusStatus;
  createdAt: number;
}

export interface Playlist {
  id: string;
  name: string;
  /** One question, not a list of faults (Blueprint §7.14). */
  question: string;
  momentIds: string[];
}

const CONSENTS: ConsentItem[] = [
  {
    id: "analysis",
    label: "Analyse my matches",
    consequence: "If you turn this off, we stop producing analysis for you. Nothing is deleted.",
    on: true,
  },
  {
    id: "keep-clips",
    label: "Keep the moments I save",
    consequence:
      "If you turn this off, your saved moments are removed from this device. The venue's recording isn't affected.",
    on: true,
  },
  {
    id: "partner-visible",
    label: "Let my doubles partner see our pair analysis",
    consequence:
      "If you turn this off, your partner sees only their own numbers from matches you played together.",
    on: true,
  },
  {
    id: "share",
    label: "Let me share a moment with someone",
    consequence: "If you turn this off, any link you've shared stops working.",
    on: true,
  },
  {
    id: "coach",
    label: "Let a coach see playlists I send them",
    consequence:
      "Access is per playlist and expires. A coach never gets your whole history, and you can revoke it.",
    on: false,
  },
  {
    id: "training",
    label: "Help improve the models",
    consequence:
      "If you turn this on, clips from your matches may be used to improve shot and rally detection. This is a separate decision from everything above, and it's off unless you turn it on.",
    on: false,
  },
];

interface State {
  theme: Theme;
  reduceMotion: boolean;
  savedMoments: string[];
  consents: ConsentItem[];
  /** Which player you are, per match. Nothing says "you" until this is set. */
  identity: Record<string, PlayerId>;
  /** Nicknames you gave the other people on court. */
  nicknames: Record<PlayerId, string>;
  corrections: Correction[];
  focus: Focus[];
  playlists: Playlist[];
  /** Matches where the "how did it feel?" prompt has been answered or dismissed. */
  reflected: Record<string, string>;
  dismissed: string[];

  setTheme: (t: Theme) => void;
  setReduceMotion: (v: boolean) => void;
  toggleSaved: (id: string) => void;
  setConsent: (id: string, on: boolean) => void;
  setIdentity: (matchId: string, playerId: PlayerId) => void;
  setNickname: (playerId: PlayerId, name: string) => void;
  addCorrection: (c: Omit<Correction, "id" | "at">) => void;
  addFocus: (f: Omit<Focus, "id" | "createdAt" | "status">) => void;
  advanceFocus: (id: string) => void;
  dropFocus: (id: string) => void;
  addPlaylist: (p: Omit<Playlist, "id">) => void;
  setReflection: (matchId: string, answer: string) => void;
  dismiss: (id: string) => void;
  /** Clears everything this device holds. Used by Settings → delete. */
  wipe: () => void;
}

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

function write(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* private mode or blocked storage — the prototype works, it just forgets */
  }
}

export function applyTheme(theme: Theme) {
  const el = document.documentElement;
  if (theme === "system") el.removeAttribute("data-theme");
  else el.setAttribute("data-theme", theme);
  try {
    if (theme === "system") localStorage.removeItem("rally.theme");
    else localStorage.setItem("rally.theme", theme);
  } catch {
    /* ignore */
  }
}

const KEYS = [
  "rally.saved",
  "rally.identity",
  "rally.nicknames",
  "rally.corrections",
  "rally.focus",
  "rally.playlists",
  "rally.reflected",
  "rally.dismissed",
];

export const useStore = create<State>((set, get) => ({
  theme: read<Theme>("rally.theme.pref", "system"),
  reduceMotion: read("rally.reduceMotion", false),
  savedMoments: read<string[]>("rally.saved", []),
  consents: CONSENTS,
  identity: read<Record<string, PlayerId>>("rally.identity", {}),
  nicknames: read<Record<PlayerId, string>>("rally.nicknames", {}),
  corrections: read<Correction[]>("rally.corrections", []),
  focus: read<Focus[]>("rally.focus", []),
  playlists: read<Playlist[]>("rally.playlists", []),
  reflected: read<Record<string, string>>("rally.reflected", {}),
  dismissed: read<string[]>("rally.dismissed", []),

  setTheme: (t) => {
    applyTheme(t);
    write("rally.theme.pref", t);
    set({ theme: t });
  },
  setReduceMotion: (v) => {
    write("rally.reduceMotion", v);
    set({ reduceMotion: v });
  },
  toggleSaved: (id) =>
    set((s) => {
      const next = s.savedMoments.includes(id)
        ? s.savedMoments.filter((x) => x !== id)
        : [...s.savedMoments, id];
      write("rally.saved", next);
      return { savedMoments: next };
    }),
  setConsent: (id, on) =>
    set((s) => ({
      consents: s.consents.map((c) => (c.id === id && !c.blockedReason ? { ...c, on } : c)),
    })),
  setIdentity: (matchId, playerId) =>
    set((s) => {
      const next = { ...s.identity, [matchId]: playerId };
      write("rally.identity", next);
      return { identity: next };
    }),
  setNickname: (playerId, name) =>
    set((s) => {
      const next = { ...s.nicknames, [playerId]: name };
      write("rally.nicknames", next);
      return { nicknames: next };
    }),
  addCorrection: (c) =>
    set((s) => {
      const next = [...s.corrections, { ...c, id: `${c.matchId}-${c.rallyNo}-${c.kind}`, at: Date.now() }];
      write("rally.corrections", next);
      return { corrections: next };
    }),
  addFocus: (f) =>
    set((s) => {
      const next = [
        ...s.focus,
        { ...f, id: `focus-${Date.now()}`, status: "reviewed" as FocusStatus, createdAt: Date.now() },
      ];
      write("rally.focus", next);
      return { focus: next };
    }),
  advanceFocus: (id) =>
    set((s) => {
      const order: FocusStatus[] = ["reviewed", "practised", "seen_again"];
      const next = s.focus.map((f) =>
        f.id === id
          ? { ...f, status: order[Math.min(order.length - 1, order.indexOf(f.status) + 1)] as FocusStatus }
          : f,
      );
      write("rally.focus", next);
      return { focus: next };
    }),
  dropFocus: (id) =>
    set((s) => {
      const next = s.focus.filter((f) => f.id !== id);
      write("rally.focus", next);
      return { focus: next };
    }),
  addPlaylist: (p) =>
    set((s) => {
      const next = [...s.playlists, { ...p, id: `pl-${Date.now()}` }];
      write("rally.playlists", next);
      return { playlists: next };
    }),
  setReflection: (matchId, answer) =>
    set((s) => {
      const next = { ...s.reflected, [matchId]: answer };
      write("rally.reflected", next);
      return { reflected: next };
    }),
  dismiss: (id) =>
    set((s) => {
      const next = [...s.dismissed, id];
      write("rally.dismissed", next);
      return { dismissed: next };
    }),
  wipe: () => {
    for (const k of KEYS) {
      try {
        localStorage.removeItem(k);
      } catch {
        /* ignore */
      }
    }
    set({
      savedMoments: [],
      identity: {},
      nicknames: {},
      corrections: [],
      focus: [],
      playlists: [],
      reflected: {},
      dismissed: [],
    });
    void get();
  },
}));

/** Stable empty arrays, so selectors never hand React a fresh reference each render. */
export const NO_CORRECTIONS: readonly Correction[] = Object.freeze([]);
