import { useMemo } from "react";
import { ErrorNote, Spinner } from "@/components/ui";
import { AskTab } from "@/features/session/tabs/AskTab";
import { HeatmapsTab } from "@/features/session/tabs/HeatmapsTab";
import { HighlightsTab } from "@/features/session/tabs/HighlightsTab";
import { RalliesTab } from "@/features/session/tabs/RalliesTab";
import { StatsTab, useAnalytics } from "@/features/session/tabs/StatsTab";
import { fps as fpsOf, STROKE_LABEL, shortName } from "@/lib/format";
import type { Analytics, PlayerId, Session } from "@/lib/types";
import { useSession } from "@/stores/session";
import { AnalysisPanel, AnalysisStat, Unavailable, Watch } from "./components";
import { activeSeconds, type EvidenceRally, evidenceRallies, shotRows } from "./evidence";
import { useInsights, useMeasuredMovement } from "./useInsights";

export interface AnalysisSearch {
  tab?: string;
  who?: PlayerId;
  kind?: string;
  rally?: number;
  f?: number;
}

export function SessionAnalytics({
  session,
  player,
  search,
}: {
  session: Session;
  player: PlayerId;
  search: AnalysisSearch;
}) {
  const q = useAnalytics(session.session_id);
  const events = useSession((s) => s.events);
  const version = useSession((s) => s.eventsVersion);
  // biome-ignore lint/correctness/useExhaustiveDependencies: version signals mutation of the event buffer.
  const rows = useMemo(() => evidenceRallies(events), [events, version]);
  const tab = search.tab ?? "overview";
  if (tab === "rallies")
    return <RalliesTab session={session} selectedPlayer={player} selectedRally={search.rally} />;
  if (tab === "moments")
    return (
      <AnalysisPanel
        title="The moments worth another look"
        hint="Ranked from the observed rallies. Each reason traces to the event log."
      >
        <HighlightsTab session={session} selectedPlayer={player} />
      </AnalysisPanel>
    );
  if (tab === "court")
    return (
      <AnalysisPanel
        title="How did you use the court?"
        hint="Measured positions on the selected court, separated by the kind of evidence."
      >
        <HeatmapsTab session={session} selectedPlayer={player} initialKind={search.kind} />
      </AnalysisPanel>
    );
  if (tab === "ask")
    return (
      <AnalysisPanel
        title="Ask about what happened"
        hint={`Selected player: ${shortName(session, player)}. Ask by name; answers link to the source evidence.`}
      >
        <div className="h-[520px]">
          <AskTab session={session} />
        </div>
      </AnalysisPanel>
    );
  if (tab === "pair")
    return (
      <Unavailable title="Your pair, when four identities can be measured">
        <p>
          This analysis currently resolves two court-side identities, P1 and P2. It does not identify four
          individual doubles players or retain partner relationships, so individual partner contributions and
          front/rear responsibility cannot yet be calculated.
        </p>
        <p className="mt-3">
          Real footage, rallies, side-based shots and court tracking remain available in the other views. A
          side must not be presented as a named doubles player.
        </p>
      </Unavailable>
    );
  if (q.isPending)
    return (
      <div className="flex items-center gap-3 py-10 text-line-2">
        <Spinner />
        Loading recorded analysis
      </div>
    );
  if (q.error) return <ErrorNote error={q.error} />;
  if (!q.data)
    return (
      <Unavailable title="Analysis is not available">
        No analytics response has been recorded for this match.
      </Unavailable>
    );
  const a = q.data;
  if (tab === "h2h")
    return (
      <AnalysisPanel
        title="The two sides, compared"
        hint="Counts use completed, counted rallies. A missing measurement is shown as a dash."
      >
        <StatsTab session={session} />
      </AnalysisPanel>
    );
  if (tab === "shots") return <ShotAnalysis session={session} player={player} analytics={a} rows={rows} />;
  if (tab === "movement") return <Movement session={session} player={player} analytics={a} rows={rows} />;
  if (tab === "tactics") return <Tactics session={session} player={player} analytics={a} rows={rows} />;
  return <Overview session={session} player={player} analytics={a} rows={rows} />;
}

function Overview({
  session,
  player,
  analytics: a,
  rows,
}: {
  session: Session;
  player: PlayerId;
  analytics: Analytics;
  rows: EvidenceRally[];
}) {
  const stats = a.players[player];
  const movement = useMeasuredMovement(session, player);
  const counted = rows.filter((r) => r.official);
  const longest = counted.reduce<EvidenceRally | undefined>(
    (best, r) => ((r.shotCount ?? 0) > (best?.shotCount ?? 0) ? r : best),
    undefined,
  );
  const basis = `Server analytics over ${a.rallies} counted rallies. Live event details may arrive incrementally.`;
  return (
    <>
      <div className="analysis-metrics">
        <AnalysisStat value={a.rallies} label="Counted rallies" note="Warm-up exchanges excluded" />
        <AnalysisStat
          value={a.longest_rally_shots || (a.rallies ? 0 : null)}
          label="Shots in the longest rally"
        />
        <AnalysisStat value={stats?.points_won} label={`${shortName(session, player)} · points won`} />
        <AnalysisStat
          value={
            stats && movement.data && movement.data.total > 0 ? `${Math.round(stats.distance_m)} m` : null
          }
          label="Ground covered"
          note="Tracking-based estimate"
        />
      </div>
      <div className="analysis-grid">
        <AnalysisPanel
          title="The rally to watch first"
          hint={
            longest
              ? `Rally ${longest.no} lasted ${longest.shotCount} recorded shots. Open the original footage to see the sequence.`
              : "Rally evidence will appear here when the event log is available."
          }
          basis={basis}
        >
          {longest ? (
            <div className="flex items-center gap-4">
              <span className="text-5xl font-bold">{longest.shotCount}</span>
              <span className="text-sm text-line-2">shots</span>
              <Watch start={longest.start} end={longest.end} label={`Rally ${longest.no}`} />
            </div>
          ) : (
            <p className="text-sm text-line-2">No completed rally evidence yet.</p>
          )}
        </AnalysisPanel>
        <AnalysisPanel title={`What ${shortName(session, player)} brought to this match`} basis={basis}>
          {stats ? (
            <dl className="grid grid-cols-2 gap-5">
              {[
                ["Winners", stats.winners],
                ["Smashes", stats.smashes],
                ["Jump smashes", stats.jump_smashes],
                ["Serve points won", `${stats.serve_points_won} / ${stats.serves}`],
                ["Errors · out", stats.errors_out],
                ["Errors · net", stats.errors_net],
              ].map(([label, value]) => (
                <div key={String(label)}>
                  <dt className="text-xs text-line-2">{label}</dt>
                  <dd className="mt-1 text-xl font-semibold">{value}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p>No player measurements were recorded.</p>
          )}
        </AnalysisPanel>
      </div>
      <div className="mt-5">
        <AnalysisPanel
          title="How the match moved"
          hint="Momentum and score progression come from the server's counted point events."
          basis={basis}
        >
          <StatsTab session={session} />
        </AnalysisPanel>
      </div>
    </>
  );
}

function ShotAnalysis({
  session,
  player,
  analytics: a,
  rows,
}: {
  session: Session;
  player: PlayerId;
  analytics: Analytics;
  rows: EvidenceRally[];
}) {
  const stats = a.players[player];
  const insights = useInsights(session.session_id);
  const authoritative = insights.data?.tactics?.[player]?.shot_distribution;
  const values = authoritative
    ? authoritative.map((s) => [s.stroke, s.count] as [string, number]).sort((x, y) => y[1] - x[1])
    : Object.entries(stats?.strokes ?? {}).sort((x, y) => y[1] - x[1]);
  const evidence = shotRows(rows, player);
  const total = values.reduce((n, [, count]) => n + count, 0);
  return (
    <div className="analysis-grid">
      <AnalysisPanel
        title="Which shots did you play?"
        preview="Shot names are rule-based estimates. Inspect the evidence before interpreting fine distinctions."
        hint={`${shortName(session, player)} · ${total} classified shots`}
        basis={`Server stroke totals over ${a.rallies} counted rallies.`}
      >
        {values.length ? (
          <div className="analysis-table-wrap">
            <table className="analysis-table">
              <caption className="sr-only">Shot type, count and share</caption>
              <thead>
                <tr>
                  <th>Shot</th>
                  <th>Count</th>
                  <th>Share</th>
                  <th>Evidence</th>
                </tr>
              </thead>
              <tbody>
                {values.map(([stroke, count]) => {
                  const e = evidence.find((x) => x.stroke === stroke);
                  return (
                    <tr key={stroke}>
                      <th scope="row">{STROKE_LABEL[stroke] ?? stroke}</th>
                      <td>{count}</td>
                      <td>
                        <div
                          className="analysis-bar"
                          style={{ width: `${total ? Math.max(2, (count / total) * 100) : 0}%` }}
                        />
                        <span className="text-xs text-line-2">
                          {total ? Math.round((count / total) * 100) : 0}%
                        </span>
                      </td>
                      <td>
                        {e ? (
                          <Watch
                            start={e.frame}
                            end={e.frame + Math.round(fpsOf(session.media) * 2)}
                            label={STROKE_LABEL[stroke] ?? stroke}
                          />
                        ) : (
                          "—"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-line-2">No assigned stroke measurements are available.</p>
        )}
      </AnalysisPanel>
      <AnalysisPanel
        title="What happened in rallies with each shot?"
        hint="Association in observed rallies, not proof that a shot caused the outcome. Rates require at least five rallies."
        basis="Derived from the available, counted rally shot sequences. It may cover fewer events than the server's full totals."
      >
        <div className="analysis-table-wrap">
          <table className="analysis-table">
            <caption className="sr-only">Rallies containing each shot and rallies won</caption>
            <thead>
              <tr>
                <th>Shot</th>
                <th>Rallies won / seen</th>
                <th>Rate</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((row) => (
                <tr key={row.stroke}>
                  <th scope="row">{STROKE_LABEL[row.stroke] ?? row.stroke}</th>
                  <td>
                    {row.won} / {row.rallies}
                  </td>
                  <td>
                    {row.rallies >= 5 ? `${Math.round((row.won / row.rallies) * 100)}%` : "Too few rallies"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!evidence.length && (
          <p className="text-sm text-line-2">No attributable shot sequences have arrived.</p>
        )}
      </AnalysisPanel>
    </div>
  );
}

function Movement({
  session,
  player,
  analytics: a,
  rows,
}: {
  session: Session;
  player: PlayerId;
  analytics: Analytics;
  rows: EvidenceRally[];
}) {
  const stats = a.players[player];
  const movement = useMeasuredMovement(session, player);
  const measured = Boolean(movement.data && movement.data.total > 0);
  const active = activeSeconds(rows, fpsOf(session.media));
  return (
    <>
      <div className="analysis-metrics">
        <AnalysisStat
          value={stats && measured ? `${Math.round(stats.distance_m)} m` : null}
          label="Distance covered"
          note="Tracking-based estimate"
        />
        <AnalysisStat
          value={stats && measured ? Math.round(stats.distance_m / 0.78).toLocaleString() : null}
          label="Estimated steps"
          note="Distance ÷ 0.78 m assumed stride; not footfalls"
        />
        <AnalysisStat
          value={active === null ? null : `${(active / 60).toFixed(1)} min`}
          label="Observed active play"
          note="Counted rally frame spans"
        />
        <AnalysisStat
          value={
            stats && active && measured ? `${(stats.distance_m / (active / 60)).toFixed(0)} m/min` : null
          }
          label="Ground covered per active minute"
        />
      </div>
      <AnalysisPanel
        title="Where did you cover that ground?"
        preview="Position estimates can include tracking jitter; distance is not a fitness measure."
        basis="Measured court coordinates and counted rally spans."
      >
        <HeatmapsTab session={session} selectedPlayer={player} initialKind="movement" />
      </AnalysisPanel>
    </>
  );
}

function Tactics({
  session,
  player,
  rows,
}: {
  session: Session;
  player: PlayerId;
  analytics: Analytics;
  rows: EvidenceRally[];
}) {
  const q = useInsights(session.session_id);
  const stats = q.data?.tactics?.[player];
  const sequences = rows
    .filter((r) => r.official && r.shots.length >= 3 && r.shots.some((s) => s.actors.player_id === player))
    .slice(0, 30);
  return (
    <div className="analysis-grid">
      <AnalysisPanel
        title="What happened on serve and return?"
        hint="Calculated by the server from observed serves, second-shot returns and rallies with a known winner."
        basis={
          q.data
            ? `Canonical event sequence ${q.data.lineage.event_seq}. ${q.data.availability.reason ?? "Completed analysis."}`
            : "Loading server evidence."
        }
      >
        <div className="text-4xl font-bold">
          {stats ? `${stats.serve_points_won} / ${stats.serve_rallies}` : "—"}
        </div>
        <p className="mt-2 text-sm text-line-2">Serve points won / service rallies with a known winner</p>
        {stats && stats.serve_rallies >= 5 && stats.serve_win_rate !== null ? (
          <p className="mt-4 text-lg">
            {Math.round(stats.serve_win_rate * 100)}% of resolved service points won
          </p>
        ) : (
          <p className="mt-4 text-sm text-line-2">
            At least five resolved service rallies are needed before showing a rate.
          </p>
        )}
        <div className="mt-6 border-t border-seam pt-5">
          <p className="text-3xl font-bold">
            {stats ? `${stats.return_points_won} / ${stats.return_rallies}` : "—"}
          </p>
          <p className="mt-2 text-sm text-line-2">
            Return points won / observed return rallies with a known winner
          </p>
          {stats && stats.return_rallies >= 5 && stats.return_win_rate !== null && (
            <p className="mt-3">{Math.round(stats.return_win_rate * 100)}% of resolved return points won</p>
          )}
        </div>
        {q.isPending && <Spinner className="mt-4" />}
        <ErrorNote error={q.error} />
        {stats && (
          <div className="analysis-table-wrap">
            <table className="analysis-table">
              <caption>How rally length related to points won</caption>
              <thead>
                <tr>
                  <th>Length</th>
                  <th>Points won / rallies</th>
                </tr>
              </thead>
              <tbody>
                {stats.rally_length.map((bucket) => (
                  <tr key={bucket.label}>
                    <th scope="row">{bucket.label}</th>
                    <td>
                      {bucket.points_won} / {bucket.rallies}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </AnalysisPanel>
      <AnalysisPanel
        title="What led to the point?"
        hint="The final three recorded shots keep the sequence visible, rather than crediting the finishing shot alone."
        basis="First 30 eligible rallies from the available event log."
      >
        {sequences.length ? (
          <ol className="space-y-3">
            {sequences.map((r) => (
              <li key={r.id} className="border-b border-seam pb-3">
                <div className="flex items-center gap-3 text-sm">
                  <span>
                    Rally {r.no} · {r.winner ? shortName(session, r.winner) : "Unresolved"}
                  </span>
                  <Watch
                    start={r.shots.at(-3)?.frame_start ?? r.start}
                    end={r.end}
                    label={`Rally ${r.no} build-up`}
                  />
                </div>
                <p className="mt-2 text-xs text-line-2">
                  {r.shots
                    .slice(-3)
                    .map(
                      (s) =>
                        STROKE_LABEL[String(s.payload.stroke)] ??
                        String(s.payload.stroke ?? "Unclassified shot"),
                    )
                    .join(" → ")}
                </p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-line-2">No complete three-shot sequence was recorded.</p>
        )}
      </AnalysisPanel>
    </div>
  );
}
