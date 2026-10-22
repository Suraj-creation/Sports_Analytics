import { create } from "zustand";

export interface Layers {
  shuttle: boolean;
  players: boolean;
  labels: boolean;
  court: boolean;
  trail: boolean;
  scoreBug: boolean;
  zones: boolean;
}

/** A bounded passage of play — a moment, a rally, a sequence someone pointed at. */
export interface Clip {
  from: number;
  to: number;
  label: string;
}

interface PlayerState {
  frame: number;
  playing: boolean;
  rate: number;
  muted: boolean;
  layers: Layers;
  /** Set when a seek came from a card, so the stage can say what you are looking at. */
  cue: string | null;
  /** When set, playback is bounded: it stops at the end instead of running on. */
  clip: Clip | null;
  /** Replay the clip automatically when it reaches the end. */
  loop: boolean;

  setFrame: (f: number) => void;
  seek: (f: number, cue?: string) => void;
  /** Play a bounded passage. This is what every "Watch" in the product calls. */
  playClip: (from: number, to: number, label: string) => void;
  replayClip: () => void;
  exitClip: () => void;
  toggleLoop: () => void;
  play: () => void;
  pause: () => void;
  toggle: () => void;
  setRate: (r: number) => void;
  toggleMute: () => void;
  toggleLayer: (k: keyof Layers) => void;
  reset: () => void;
}

const DEFAULT_LAYERS: Layers = {
  // Overlays that help read the picture are on; the analyst ones start off.
  shuttle: true,
  players: true,
  labels: true,
  court: true,
  trail: true,
  scoreBug: true,
  zones: false,
};

function readLayers(): Layers {
  try {
    const raw = localStorage.getItem("rally.layers");
    return raw ? { ...DEFAULT_LAYERS, ...(JSON.parse(raw) as Partial<Layers>) } : DEFAULT_LAYERS;
  } catch {
    return DEFAULT_LAYERS;
  }
}

/** A short lead-in, so a clip starts just before the thing it is about. */
export const LEAD_IN = 30;

export const usePlayer = create<PlayerState>((set, get) => ({
  frame: 0,
  playing: false,
  rate: 1,
  muted: true,
  layers: readLayers(),
  cue: null,
  clip: null,
  loop: false,

  setFrame: (f) => set({ frame: Math.max(0, Math.round(f)) }),
  seek: (f, cue) => set({ frame: Math.max(0, Math.round(f)), playing: true, cue: cue ?? null, clip: null }),
  playClip: (from, to, label) =>
    set({
      clip: { from: Math.max(0, Math.round(from - LEAD_IN)), to: Math.round(to), label },
      frame: Math.max(0, Math.round(from - LEAD_IN)),
      playing: true,
      cue: label,
    }),
  replayClip: () => {
    const c = get().clip;
    if (c) set({ frame: c.from, playing: true });
  },
  exitClip: () => set({ clip: null, loop: false, cue: null }),
  toggleLoop: () => set({ loop: !get().loop }),
  play: () => set({ playing: true }),
  pause: () => set({ playing: false }),
  toggle: () => set({ playing: !get().playing }),
  setRate: (r) => set({ rate: r }),
  toggleMute: () => set({ muted: !get().muted }),
  toggleLayer: (k) =>
    set((s) => {
      const layers = { ...s.layers, [k]: !s.layers[k] };
      try {
        localStorage.setItem("rally.layers", JSON.stringify(layers));
      } catch {
        /* blocked storage is fine — the layer choice just won't persist */
      }
      return { layers };
    }),
  reset: () => set({ frame: 0, playing: false, cue: null, clip: null, loop: false }),
}));
