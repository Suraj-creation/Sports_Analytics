export interface ClipRange {
  from: number;
  to: number;
}
export function normalizeClip(start: number, end: number, fps: number, nFrames: number): ClipRange | null {
  if (
    ![start, end, fps, nFrames].every(Number.isFinite) ||
    start > end ||
    fps <= 0 ||
    nFrames < 1 ||
    end < 0 ||
    start >= nFrames
  )
    return null;
  return { from: Math.max(0, Math.floor(start - fps)), to: Math.min(nFrames - 1, Math.floor(end)) };
}

/** Every analytical Watch action addresses the same real source player. */
export function playEvidence(start: number, end: number, label: string) {
  window.dispatchEvent(new CustomEvent("bai:play-clip", { detail: { start, end, label } }));
  document.querySelector("[data-match-player]")?.scrollIntoView({
    behavior:
      document.documentElement.dataset.reducedMotion === "true" ||
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
    block: "start",
  });
}
