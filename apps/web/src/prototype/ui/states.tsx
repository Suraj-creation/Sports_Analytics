import { clsx } from "clsx";
import { CircleAlert, CircleDot, type Clock } from "lucide-react";
import type { ReactNode } from "react";
import type { Match } from "../data/types";
import { StateArt } from "./art";

/* ─────────────────────────────────────────────────────────────────────────────
   States.

   One shell, several motifs. Every state names what happened, why, and exactly one
   thing to do next. Failure is never red beyond the small icon and never blames the
   player or the footage.
   ───────────────────────────────────────────────────────────────────────────── */

export type StateKind =
  | "empty"
  | "partial"
  | "low-coverage"
  | "failed"
  | "not-enough"
  | "offline"
  | "permission"
  | "processing";

export function StateShell({
  kind,
  title,
  reason,
  action,
  secondary,
  className,
}: {
  kind: StateKind;
  title: string;
  reason: ReactNode;
  action?: ReactNode;
  secondary?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "flex flex-col items-center gap-4 rounded-[14px] border border-edge bg-surface px-6 py-10 text-center",
        kind === "failed" && "border-error/30",
        className,
      )}
    >
      <StateArt motif={kind} className="h-16 w-20" />
      <div className="measure">
        <p className="text-lg font-[650] text-ink">{title}</p>
        <div className="mt-1.5 text-sm text-muted">{reason}</div>
      </div>
      {(action || secondary) && (
        <div className="flex flex-wrap items-center justify-center gap-2">
          {action}
          {secondary}
        </div>
      )}
    </div>
  );
}

const STATUS: Record<Match["status"], { word: string; icon: typeof Clock; tone: string; shape: string }> = {
  analysing: { word: "Analysing", icon: CircleDot, tone: "text-ink", shape: "border-solid" },
  ready: { word: "Ready", icon: CircleDot, tone: "text-ink", shape: "border-solid" },
  failed: { word: "Couldn't finish", icon: CircleAlert, tone: "text-error", shape: "border-solid" },
};

export function MatchStatusChip({
  status,
  progress,
  className,
}: {
  status: Match["status"];
  progress?: number;
  className?: string;
}) {
  const s = STATUS[status];
  const Icon = s.icon;
  return (
    <span
      className={clsx(
        "inline-flex min-h-7 items-center gap-1.5 rounded-full border border-current/40 px-2.5 py-1 text-xs font-medium",
        s.tone,
        s.shape,
        className,
      )}
    >
      <Icon
        className={clsx("size-3.5 shrink-0", status === "analysing" && "live-dot text-live")}
        aria-hidden
      />
      {s.word}
      {status === "analysing" && typeof progress === "number" && (
        <span className="tabular">{Math.round(progress * 100)}%</span>
      )}
    </span>
  );
}
