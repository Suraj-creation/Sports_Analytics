import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Empty, ErrorNote } from "@/components/ui";
import { Watch } from "@/features/analytics/components";
import {
  type EvidenceRally,
  evidenceRallies,
  filterRallies,
  type RallyFilter,
} from "@/features/analytics/evidence";
import { playEvidence } from "@/features/player/clip";
import { api } from "@/lib/api";
import { clock, fps as fpsOf, STROKE_LABEL, shortName } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

export function RalliesTab({
  session,
  selectedPlayer,
  selectedRally,
}: {
  session: Session;
  selectedPlayer?: PlayerId;
  selectedRally?: number;
}) {
  const events = useSession((s) => s.events);
  const version = useSession((s) => s.eventsVersion);
  const [filter, setFilter] = useState<RallyFilter>({});
  const [limit, setLimit] = useState(50);
  // biome-ignore lint/correctness/useExhaustiveDependencies: version signals mutation of the event buffer.
  const rows = useMemo(() => evidenceRallies(events), [events, version]);
  const shown = filterRallies(rows, filter);
  const set = (patch: RallyFilter) => {
    setFilter((f) => ({ ...f, ...patch }));
    setLimit(50);
  };
  if (!rows.length)
    return (
      <Empty title="No completed rallies yet">
        The real event log fills this view as processing finishes.
      </Empty>
    );
  return (
    <section>
      <h2 className="text-xl font-semibold">Every rally, and how it unfolded</h2>
      <p className="analysis-panel-hint mb-5">
        {rows.length} observed rallies. Warm-up and excluded exchanges stay visible and do not enter the
        score.
      </p>
      <div className="analysis-filters">
        <label>
          Outcome
          <select
            value={filter.outcome ?? "all"}
            onChange={(e) => set({ outcome: e.target.value as RallyFilter["outcome"] })}
          >
            <option value="all">All exchanges</option>
            <option value="counted">Counted in the match</option>
            <option value="excluded">Not counted</option>
          </select>
        </label>
        <label>
          Winner
          <select
            value={filter.winner ?? "all"}
            onChange={(e) => set({ winner: e.target.value as RallyFilter["winner"] })}
          >
            <option value="all">Either player</option>
            {session.players.map((p) => (
              <option key={p.player_id} value={p.player_id}>
                {shortName(session, p.player_id)}
                {p.player_id === selectedPlayer ? " · selected" : ""}
              </option>
            ))}
          </select>
        </label>
        <label>
          Rally length
          <select
            value={filter.minimumShots ?? 0}
            onChange={(e) => set({ minimumShots: Number(e.target.value) })}
          >
            <option value="0">Any number of shots</option>
            <option value="4">4+ shots</option>
            <option value="8">8+ shots</option>
            <option value="12">12+ shots</option>
          </select>
        </label>
        <span className="py-3 text-sm text-line-2" role="status">
          {shown.length} shown
        </span>
        <button
          type="button"
          className="analysis-watch"
          onClick={() => {
            setFilter({});
            setLimit(50);
          }}
        >
          Clear filters
        </button>
      </div>
      {shown.length === 0 && <Empty title="No rallies match these filters">Try clearing a filter.</Empty>}
      {shown.slice(0, limit).map((r) => (
        <RallyRow key={r.id} rally={r} session={session} open={selectedRally === r.no} />
      ))}
      {shown.length > limit && (
        <button type="button" className="rally-action mt-5" onClick={() => setLimit((n) => n + 50)}>
          Show 50 more rallies
        </button>
      )}
    </section>
  );
}

function RallyRow({ rally: r, session, open }: { rally: EvidenceRally; session: Session; open: boolean }) {
  const selection = usePlayback((s) => s.selection);
  const selected = selection && selection.start >= r.start && selection.start <= r.end;
  const qc = useQueryClient();
  const fix = useMutation({
    mutationFn: (
      action:
        | { kind: "winner"; player: PlayerId }
        | { kind: "official" }
        | { kind: "verify" }
        | { kind: "start" },
    ) => {
      if (action.kind === "winner") return api.correctWinner(session.session_id, r.id, action.player);
      if (action.kind === "official") return api.setRallyOfficial(session.session_id, r.id, !r.official);
      if (action.kind === "verify") return api.verifyEvent(session.session_id, r.id);
      return api.setMatchStart(session.session_id, r.start);
    },
    onSuccess: () => {
      void qc.invalidateQueries();
    },
  });
  return (
    <details className="rally-row" open={open || selected || undefined}>
      <summary>
        <span className="font-semibold">Rally {r.no}</span>
        <span className="text-sm text-line-2">
          {clock(r.start, session.media)} · {r.shotCount ?? "—"} shots
        </span>
        <span className="text-sm">
          {!r.official
            ? "Not counted"
            : r.winner
              ? `${shortName(session, r.winner)} won`
              : "Winner not established"}
        </span>
        <span className="ml-auto text-xs text-line-3">{r.outcome.replaceAll("_", " ")}</span>
      </summary>
      <div className="rally-row-body">
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Watch start={r.start} end={r.end} label={`Rally ${r.no}`} />
          <span className="text-xs text-line-3">
            Event {r.id.slice(0, 12)} · {r.event.status.replaceAll("_", " ")}
          </span>
        </div>
        <div className="rally-shot-list">
          {r.shots.map((s) => (
            <button
              type="button"
              key={s.event_id}
              aria-current={
                selection?.eventId === s.event_id || selection?.start === s.frame_start ? "true" : undefined
              }
              onClick={() =>
                playEvidence(
                  s.frame_start,
                  Math.min(r.end, s.frame_start + Math.round(fpsOf(session.media) * 1.5)),
                  STROKE_LABEL[String(s.payload.stroke)] ?? "Shot",
                  s.event_id,
                )
              }
            >
              <span className="mr-1" aria-hidden>
                {s.actors.player_id === "P1" ? "●" : "■"}
              </span>
              {s.actors.player_id ? `${shortName(session, s.actors.player_id)} · ` : "Unassigned · "}
              {STROKE_LABEL[String(s.payload.subtype ?? s.payload.stroke)] ??
                String(s.payload.stroke ?? "Shot")}
            </button>
          ))}
        </div>
        {!r.shots.length && (
          <p className="mt-4 text-sm text-line-2">No shot sequence was persisted for this rally.</p>
        )}
        {r.event.payload.end_reason && (
          <p className="mt-3 text-sm text-line-2">
            Why it ended: {String(r.event.payload.end_reason).replaceAll("_", " ")}
          </p>
        )}
        <div className="rally-corrections">
          <p>
            Check this rally. Changing its winner re-scores the following points and updates the analysis.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {r.winner && (
              <button
                type="button"
                className="rally-action"
                disabled={fix.isPending}
                onClick={() => fix.mutate({ kind: "verify" })}
              >
                Confirm winner
              </button>
            )}
            {session.players
              .filter((p) => p.player_id !== r.winner)
              .map((p) => (
                <button
                  type="button"
                  className="rally-action"
                  key={p.player_id}
                  disabled={fix.isPending}
                  onClick={() => fix.mutate({ kind: "winner", player: p.player_id })}
                >
                  {shortName(session, p.player_id)} won it
                </button>
              ))}
            <button
              type="button"
              className="rally-action"
              disabled={fix.isPending}
              onClick={() => fix.mutate({ kind: "official" })}
            >
              {r.official ? "Not part of the match" : "Count this rally"}
            </button>
            <button
              type="button"
              className="rally-action"
              disabled={fix.isPending}
              onClick={() => fix.mutate({ kind: "start" })}
            >
              Match starts here
            </button>
          </div>
          <ErrorNote error={fix.error} />
          {fix.isSuccess && (
            <p role="status" className="mt-3">
              Correction saved to the server. The score and analytics are refreshing.
            </p>
          )}
        </div>
      </div>
    </details>
  );
}
