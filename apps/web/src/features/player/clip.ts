import { fps as fpsOf, strokeLabel } from "@/lib/format";
import type { BaiEvent, MediaInfo } from "@/lib/types";
import { type EvidenceSelection, usePlayback } from "@/stores/playback";

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
export function playEvidence(start: number, end: number, label: string, eventId?: string) {
  if (![start, end].every(Number.isFinite) || start < 0 || start > end) return;
  const selection: EvidenceSelection = { start, end, label, eventId };
  // Retain the request even when media is still loading; the player consumes it when ready.
  usePlayback.setState({ selection, clip: null });
  window.dispatchEvent(new CustomEvent("bai:play-clip", { detail: selection }));
  document.querySelector("[data-match-player]")?.scrollIntoView({
    behavior:
      document.documentElement.dataset.reducedMotion === "true" ||
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
    block: "start",
  });
}

/** Known event previews retain identity, uncertainty and the canonical source interval. */
export function playEventEvidence(event: BaiEvent, media: MediaInfo | null) {
  const label =
    event.type === "stroke"
      ? strokeLabel(event.payload)
      : event.type === "rally_end"
        ? `Rally ${event.payload.rally_no ?? ""}`.trim()
        : event.type.replaceAll("_", " ");
  const end =
    event.frame_end > event.frame_start
      ? event.frame_end
      : event.frame_start + Math.round(fpsOf(media) * 1.5);
  playEvidence(event.frame_start, Math.min((media?.n_frames ?? end + 1) - 1, end), label, event.event_id);
}
