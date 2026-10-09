import { create } from "zustand";

export interface Layers {
  shuttle: boolean;
  players: boolean;
  pose: boolean;
  court: boolean;
  labels: boolean;
  scoreBug: boolean;
}

interface PlaybackStore {
  /** Current presented frame, updated ~10×/s for React panels (the canvas uses the exact frame). */
  frame: number;
  playing: boolean;
  duration: number;
  layers: Layers;
  waitForAnalysis: boolean;
  video: HTMLVideoElement | null;
  setFrame: (f: number) => void;
  setPlaying: (p: boolean) => void;
  setDuration: (d: number) => void;
  toggleLayer: (k: keyof Layers) => void;
  setWaitForAnalysis: (v: boolean) => void;
  bindVideo: (v: HTMLVideoElement | null) => void;
  seekFrame: (frame: number, fps: number) => void;
}

const LAYERS_KEY = "bai.layers";
function loadLayers(): Layers {
  const d: Layers = { shuttle: true, players: true, pose: true, court: true, labels: true, scoreBug: true };
  try {
    return { ...d, ...JSON.parse(localStorage.getItem(LAYERS_KEY) ?? "{}") };
  } catch {
    return d;
  }
}

export const usePlayback = create<PlaybackStore>((set, get) => ({
  frame: 0,
  playing: false,
  duration: 0,
  layers: loadLayers(),
  waitForAnalysis: true,
  video: null,
  setFrame: (frame) => set({ frame }),
  setPlaying: (playing) => set({ playing }),
  setDuration: (duration) => set({ duration }),
  toggleLayer: (k) => {
    const layers = { ...get().layers, [k]: !get().layers[k] };
    try {
      localStorage.setItem(LAYERS_KEY, JSON.stringify(layers));
    } catch {
      /* storage unavailable */
    }
    set({ layers });
  },
  setWaitForAnalysis: (waitForAnalysis) => set({ waitForAnalysis }),
  bindVideo: (video) => set({ video }),
  seekFrame: (frame, fps) => {
    const v = get().video;
    if (!v) return;
    // seek to the middle of the frame interval so rounding lands on the intended frame
    v.currentTime = Math.max(0, (frame + 0.5) / fps);
    set({ frame });
  },
}));
