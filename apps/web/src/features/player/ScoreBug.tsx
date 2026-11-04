import { clsx } from "clsx";
import { useMemo } from "react";
import { stateAt } from "@/features/session/derive";
import { shortName } from "@/lib/format";
import type { BaiEvent, PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

type BroadcastRows = [{ name: string; points: number }, { name: string; points: number }];

/** Broadcast-style score bug. State is derived for the *presented* frame — no spoilers. */
export function ScoreBug({ session }: { session: Session }) {
  const frame = usePlayback((s) => s.frame);
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const status = useSession((s) => s.session?.status);
  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const { state, known, evidence } = useMemo(() => stateAt(events, frame), [events, eventsVersion, frame]);
  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const broadcasts = useMemo(() => events.ofType("broadcast_score"), [events, eventsVersion]);

  const observed = events.latestBefore("broadcast_score", frame);
  const rows = observed?.payload.rows;
  // An accepted backend point advances the score even when OCR has not read
  // the changed board yet. Compare video frames, not packet arrival order.
  const acceptedScore =
    known &&
    evidence &&
    (evidence.frame_start > (observed?.frame_start ?? -1) ||
      (evidence.frame_start === observed?.frame_start && (evidence.seq ?? 0) >= (observed.seq ?? 0)));
  const broadcast = !acceptedScore && validBroadcastRows(rows) ? rows : null;
  const observedIndex = observed ? broadcasts.findIndex((event) => event.event_id === observed.event_id) : -1;
  const incrementName = sourceIncrementName(observed, broadcasts[observedIndex - 1], broadcast);
  const fps = session.media ? session.media.fps_num / session.media.fps_den : 30;
  const age = observed ? Math.max(0, Math.floor((frame - observed.frame_start) / fps)) : 0;

  const flag = broadcast
    ? null
    : state.winner
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
      <div className="video-score-panel overflow-hidden rounded-lg">
        {broadcast
          ? broadcast.map((row, index) => (
              <Row
                key={index === 0 ? "broadcast-top" : "broadcast-bottom"}
                name={row.name}
                pid={null}
                serving={false}
                games={null}
                points={row.points}
                pending={false}
              />
            ))
          : (["P1", "P2"] as PlayerId[]).map((pid) => (
              <Row
                key={pid}
                name={shortName(session, pid)}
                pid={pid}
                serving={known && state.server_known !== false && state.server === pid}
                games={state.games_won[pid] ?? 0}
                points={state.score[pid] ?? 0}
                pending={!known}
              />
            ))}
      </div>
      <div className="mt-1 flex items-center gap-1.5 text-[11px]">
        <span className="rounded bg-mat-deep/80 px-1.5 py-0.5 text-line-2">
          {broadcast
            ? "Broadcast score"
            : known
              ? `Game ${state.game_no}`
              : status === "analysing"
                ? "Score pending"
                : "Score unavailable"}
        </span>
        {broadcast && age > 5 && (
          <span className="rounded bg-mat-deep/80 px-1.5 py-0.5 text-line-3">Last read {age}s ago</span>
        )}
        {flag && <span className="rounded bg-line px-1.5 py-0.5 font-semibold text-mat-deep">{flag}</span>}
        {!broadcast && !known && status === "analysing" && (
          <span className="rounded bg-mat-deep/80 px-1.5 py-0.5 text-line-3">score pending</span>
        )}
      </div>
      {incrementName && (
        <div
          role="status"
          aria-label="Observed broadcast increment"
          className="mt-1 max-w-72 rounded bg-mat-deep/90 px-2 py-1 text-[11px] text-shuttle"
        >
          <span className="font-semibold">{incrementName} +1</span>
          <span className="text-line-2"> · Observed broadcast</span>
        </div>
      )}
    </div>
  );
}

function validBroadcastRows(rows: unknown): rows is BroadcastRows {
  return (
    Array.isArray(rows) &&
    rows.length === 2 &&
    rows.every(
      (row) =>
        row !== null &&
        typeof row === "object" &&
        typeof row.name === "string" &&
        row.name.trim().length > 0 &&
        Number.isInteger(row.points) &&
        row.points >= 0 &&
        row.points <= 30,
    )
  );
}

function sourceIncrementName(
  current: BaiEvent | undefined,
  previous: BaiEvent | undefined,
  rows: BroadcastRows | null,
): string | null {
  if (
    !current ||
    !previous ||
    !rows ||
    previous.frame_start >= current.frame_start ||
    [previous, current].some(
      (event) =>
        event.status !== "confirmed" ||
        event.payload.source !== "broadcast_ocr" ||
        event.payload.confirmation !== "two_distinct_observations",
    )
  )
    return null;
  const prior = previous.payload.rows;
  if (!validBroadcastRows(prior)) return null;
  const names = rows.map((row) => row.name.trim().toUpperCase());
  if (
    names[0] === names[1] ||
    names.some((name, index) => !/\p{L}/u.test(name) || name !== prior[index]?.name.trim().toUpperCase())
  )
    return null;
  const first = rows[0].points - prior[0].points;
  const second = rows[1].points - prior[1].points;
  if (first === 1 && second === 0) return rows[0].name.trim();
  if (first === 0 && second === 1) return rows[1].name.trim();
  return null;
}

function Row(props: {
  name: string;
  pid: PlayerId | null;
  serving: boolean;
  games: number | null;
  points: number;
  pending: boolean;
}) {
  return (
    <div className="flex h-7 items-center gap-2 pr-0 pl-2 text-sm">
      <span
        className="h-4 w-1 rounded-full"
        style={{
          background:
            props.pid === "P1"
              ? "var(--color-p1)"
              : props.pid === "P2"
                ? "var(--color-p2)"
                : "var(--color-line-2)",
        }}
        aria-hidden
      />
      <span className="w-28 truncate font-medium">{props.name}</span>
      <span
        className={clsx("size-1.5 rounded-full", props.serving ? "bg-shuttle" : "bg-transparent")}
        aria-hidden
      />
      <span className="sr-only">{props.serving ? "serving" : ""}</span>
      {props.games !== null && (
        <span className="numerals w-5 text-center text-line-2">{props.pending ? "—" : props.games}</span>
      )}
      <span
        className={clsx(
          "numerals grid h-7 w-8 place-items-center bg-white/8 text-base",
          props.pending && "text-line-3",
        )}
      >
        {props.pending ? "—" : props.points}
      </span>
    </div>
  );
}
