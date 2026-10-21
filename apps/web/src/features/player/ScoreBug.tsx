import { clsx } from "clsx";
import { useMemo } from "react";
import { stateAt } from "@/features/session/derive";
import { shortName } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

/** Broadcast-style score bug. State is derived for the *presented* frame — no spoilers. */
export function ScoreBug({ session }: { session: Session }) {
  const frame = usePlayback((s) => s.frame);
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const status = useSession((s) => s.session?.status);
  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const { state, known } = useMemo(() => stateAt(events, frame), [events, eventsVersion, frame]);

  const flag = state.winner
    ? `${shortName(session, state.winner)} wins the match`
    : state.match_point
      ? "Match point"
      : state.game_point
        ? "Game point"
        : state.deuce
          ? "Deuce"
          : null;

  return (
    <div className="pointer-events-none absolute top-3 left-3 select-none" data-testid="score-bug">
      <div className="overflow-hidden rounded-lg border border-white/10 bg-mat-deep/88 shadow-lg shadow-black/30 backdrop-blur-sm">
        {(["P1", "P2"] as PlayerId[]).map((pid) => (
          <Row
            key={pid}
            name={shortName(session, pid)}
            pid={pid}
            serving={known && state.server === pid}
            games={state.games_won[pid] ?? 0}
            points={state.score[pid] ?? 0}
            pending={!known && status === "analysing"}
          />
        ))}
      </div>
      <div className="mt-1 flex items-center gap-1.5 text-[11px]">
        <span className="rounded bg-mat-deep/80 px-1.5 py-0.5 text-line-2">Game {state.game_no}</span>
        {flag && <span className="rounded bg-line px-1.5 py-0.5 font-semibold text-mat-deep">{flag}</span>}
        {!known && status === "analysing" && (
          <span className="rounded bg-mat-deep/80 px-1.5 py-0.5 text-line-3">score pending</span>
        )}
      </div>
    </div>
  );
}

function Row(props: {
  name: string;
  pid: PlayerId;
  serving: boolean;
  games: number;
  points: number;
  pending: boolean;
}) {
  return (
    <div className="flex h-7 items-center gap-2 pr-0 pl-2 text-sm">
      <span
        className="h-4 w-1 rounded-full"
        style={{ background: props.pid === "P1" ? "var(--color-p1)" : "var(--color-p2)" }}
        aria-hidden
      />
      <span className="w-28 truncate font-medium">{props.name}</span>
      <span
        className={clsx("size-1.5 rounded-full", props.serving ? "bg-shuttle" : "bg-transparent")}
        aria-hidden
      />
      <span className="sr-only">{props.serving ? "serving" : ""}</span>
      <span className="numerals w-5 text-center text-line-2">{props.games}</span>
      <span
        className={clsx(
          "numerals grid h-7 w-8 place-items-center bg-white/8 text-base",
          props.pending && "text-line-3",
        )}
      >
        {props.points}
      </span>
    </div>
  );
}
