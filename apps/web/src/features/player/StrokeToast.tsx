import { useMemo } from "react";
import { BandChip } from "@/components/ui";
import { fps as fpsOf, OUTCOME_LABEL, playerColor, shortName, strokeLabel } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

const SHOW_S = 1.4;

/** The shot just played ("Jump smash · Axelsen · probable"), and the point when a rally ends. */
export function StrokeToast({ session }: { session: Session }) {
  const frame = usePlayback((s) => s.frame);
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const fps = fpsOf(session.media);

  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const latest = useMemo(() => {
    const win = events.window(frame - Math.round(SHOW_S * fps), frame, ["stroke", "point"]);
    const recent = win.filter((e) => e.frame_start <= frame);
    return recent[recent.length - 1];
  }, [events, eventsVersion, frame, fps]);

  if (!latest) return null;
  const pid = latest.actors.player_id as PlayerId | null;

  if (latest.type === "point") {
    const end = latest.parent_id ? events.get(latest.parent_id) : undefined;
    const outcome = end?.payload.outcome as string | undefined;
    return (
      <Toast>
        <span className="font-semibold">Point {shortName(session, pid)}</span>
        {outcome && <span className="text-line-2">· shuttle {OUTCOME_LABEL[outcome] ?? outcome}</span>}
      </Toast>
    );
  }

  const label = strokeLabel(latest.payload);
  const emph = latest.payload.stroke === "smash";
  return (
    <Toast key={latest.event_id}>
      <BandChip band={latest.band} color={playerColor(pid)}>
        <span className={emph ? "font-semibold" : undefined}>{label}</span>
      </BandChip>
      <span className="text-line-2">{shortName(session, pid)}</span>
      {latest.confidence != null && (
        <span className="tabular text-xs text-line-3">{Math.round(latest.confidence * 100)}%</span>
      )}
    </Toast>
  );
}

function Toast({ children }: { children: React.ReactNode }) {
  return (
    <div className="pointer-events-none absolute inset-x-0 top-3 flex justify-center">
      <div
        className="flex animate-[toast-in_180ms_var(--ease-snap)] items-center gap-2 rounded-full border border-white/10 bg-mat-deep/88 px-3 py-1.5 text-sm shadow-lg shadow-black/30 backdrop-blur-sm"
        role="status"
      >
        {children}
      </div>
    </div>
  );
}
