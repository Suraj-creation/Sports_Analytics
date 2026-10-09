/**
 * The presented-frame clock. The video stage publishes the exact frame shown on screen from
 * requestVideoFrameCallback; canvases (overlay, minimap, timeline playhead) subscribe and
 * redraw without going through React. React panels read the throttled copy in usePlayback.
 */
type Listener = (frame: number) => void;

class FrameClock {
  private listeners = new Set<Listener>();
  frame = 0;

  publish(frame: number): void {
    this.frame = frame;
    for (const l of this.listeners) l(frame);
  }

  subscribe(l: Listener): () => void {
    this.listeners.add(l);
    l(this.frame);
    return () => {
      this.listeners.delete(l);
    };
  }

  /** Re-run listeners at the same frame (e.g. new tracks arrived while paused). */
  poke(): void {
    this.publish(this.frame);
  }
}

export const frameClock = new FrameClock();

/** Frame index for a media time. `+1e-4` guards float error at exact frame boundaries. */
export function timeToFrame(t: number, fps: number): number {
  return Math.max(0, Math.floor(t * fps + 1e-4));
}
