import { useMutation } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Check, ChevronDown } from "lucide-react";
import { useMemo, useState } from "react";
import { BandChip, Button, Empty, ErrorNote, PlayerDot } from "@/components/ui";
import { type RallyView, rallies } from "@/features/session/derive";
import { api } from "@/lib/api";
import { clock, fps as fpsOf, OUTCOME_LABEL, playerColor, STROKE_LABEL, shortName } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

/**
 * Review: every rally with its shots, outcome and the evidence behind the winner. Corrections
 * are written as human-verified events; the score and statistics refold from them.
 */
export function RalliesTab({ session }: { session: Session }) {
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const frame = usePlayback((s) => s.frame);
  const [onlyDoubtful, setOnlyDoubtful] = useState(false);
  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const list = useMemo(() => rallies(events).reverse(), [events, eventsVersion]);
  const shown = onlyDoubtful
    ? list.filter((r) => r.end.band !== "confirmed" && r.end.status !== "human_verified")
    : list;

  if (!list.length)
    return <Empty title="No rallies yet">Rallies are listed here as soon as they finish.</Empty>;
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 text-sm">
        <span className="text-line-2">{list.length} rallies</span>
        <label className="ml-auto flex items-center gap-2 text-line-2">
          <input
            type="checkbox"
            className="size-4 accent-[var(--color-signal)]"
            checked={onlyDoubtful}
            onChange={(e) => setOnlyDoubtful(e.target.checked)}
          />
          Only rallies that need a look
        </label>
      </div>
      <ul className="divide-y divide-seam rounded-[var(--radius-card)] border border-seam">
        {shown.map((r) => (
          <RallyRow
            key={r.end.event_id}
            r={r}
            session={session}
            current={frame >= r.start && frame <= r.stop}
          />
        ))}
      </ul>
    </div>
  );
}

function RallyRow({ r, session, current }: { r: RallyView; session: Session; current: boolean }) {
  const [open, setOpen] = useState(false);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const fps = fpsOf(session.media);
  const p = r.end.payload;
  const shots =
    (p.shots as {
      event_id: string | null;
      frame: number;
      player_id: PlayerId | null;
      stroke: string;
      subtype: string | null;
    }[]) ?? [];
  const verified = r.end.status === "human_verified" || r.end.status === "corrected";
  const fix = useMutation({
    mutationFn: (winner: PlayerId) => api.correctWinner(session.session_id, r.end.event_id, winner),
  });
  const confirm = useMutation({ mutationFn: () => api.verifyEvent(session.session_id, r.end.event_id) });

  return (
    <li className={clsx("px-3 py-2.5", current && "bg-stand-raised/60")}>
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="tabular w-12 shrink-0 text-left text-xs text-line-3 hover:text-line"
          onClick={() => seekFrame(Math.max(0, r.start - Math.round(fps)), fps)}
          aria-label={`Jump to rally ${r.no}`}
        >
          {clock(r.start, session.media)}
        </button>
        <span className="w-16 shrink-0 text-sm font-medium">Rally {r.no}</span>
        <BandChip band={verified ? "confirmed" : r.end.band} color={playerColor(r.winner)}>
          {r.winner ? `${shortName(session, r.winner)} wins` : "Winner unclear"}
        </BandChip>
        <span className="hidden truncate text-xs text-line-2 sm:inline">
          {p.n_shots ?? shots.length} shots
          {p.outcome && ` · shuttle ${OUTCOME_LABEL[p.outcome as string] ?? p.outcome}`}
          {p.winner_source === "ocr" && " · from the scoreboard"}
        </span>
        {verified && (
          <span className="flex items-center gap-1 text-xs text-signal">
            <Check className="size-3.5" aria-hidden /> checked
          </span>
        )}
        <button
          type="button"
          className="ml-auto grid size-7 place-items-center rounded-md text-line-2 hover:bg-stand-raised hover:text-line"
          aria-expanded={open}
          aria-label={open ? "Hide details" : "Show details"}
          onClick={() => setOpen((o) => !o)}
        >
          <ChevronDown className={clsx("size-4 transition-transform", open && "rotate-180")} />
        </button>
      </div>
      {open && (
        <div className="mt-3 space-y-3 pl-[7.5rem]">
          <div className="flex flex-wrap gap-1.5">
            {shots.map((s, i) => (
              <button
                key={s.event_id ?? `${s.frame}-${i}`}
                type="button"
                onClick={() => seekFrame(Math.max(0, s.frame - 10), fps)}
                className="flex items-center gap-1.5 rounded-full border border-seam px-2 py-0.5 text-xs hover:border-line-3"
              >
                <PlayerDot pid={s.player_id} />
                {s.subtype === "jump_smash" ? "Jump smash" : (STROKE_LABEL[s.stroke] ?? s.stroke)}
              </button>
            ))}
          </div>
          {p.end_reason && (
            <p className="text-xs text-line-2">
              Why the rally ended: {String(p.end_reason).replace(/_/g, " ")}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-line-3">Is the winner right?</span>
            {!verified && r.winner && (
              <Button size="sm" variant="secondary" busy={confirm.isPending} onClick={() => confirm.mutate()}>
                Yes, {shortName(session, r.winner)} won
              </Button>
            )}
            {(["P1", "P2"] as PlayerId[])
              .filter((pid) => pid !== r.winner || !r.winner)
              .map((pid) => (
                <Button
                  key={pid}
                  size="sm"
                  variant="ghost"
                  busy={fix.isPending}
                  onClick={() => fix.mutate(pid)}
                >
                  <PlayerDot pid={pid} /> {shortName(session, pid)} won it
                </Button>
              ))}
            <span className="text-xs text-line-3">
              Changing the winner re-scores every point after this one.
            </span>
          </div>
          <ErrorNote error={fix.error ?? confirm.error} />
        </div>
      )}
    </li>
  );
}
