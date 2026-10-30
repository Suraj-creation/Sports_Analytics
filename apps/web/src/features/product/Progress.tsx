import { useNavigate, useSearch } from "@tanstack/react-router";
import { useState } from "react";
import { dateLabel, strokeLabel } from "./model";
import { Card, Catalogue, Empty, MatchLink, Stat } from "./ui";

export function ProgressPage() {
  const search = useSearch({ strict: false }) as { tab?: string };
  const navigate = useNavigate();
  const [personId, setPersonId] = useState("");
  const tab = search.tab || "overview";
  return (
    <Catalogue title="Progress" lead="Recording-level trends and the history of your named players.">
      {(data) => {
        const person = data.people.find((entry) => entry.person_id === personId) ?? data.people[0];
        const maxAverage = Math.max(1, ...data.progress.history.map((entry) => entry.avg_rally_shots ?? 0));
        return (
          <div className="rally-stack">
            <div
              className="rally-tabbar"
              role="tablist"
              aria-label="Progress views"
              onKeyDown={(event) => {
                if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
                event.preventDefault();
                const tabs = Array.from(
                  event.currentTarget.querySelectorAll<HTMLButtonElement>('[role="tab"]'),
                );
                const index = tabs.indexOf(document.activeElement as HTMLButtonElement);
                const next =
                  event.key === "Home"
                    ? 0
                    : event.key === "End"
                      ? tabs.length - 1
                      : (index + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
                tabs[next]?.focus();
                tabs[next]?.click();
              }}
            >
              {[
                ["overview", "Trends"],
                ["records", "Records"],
                ["shots", "Shot history"],
                ["focus", "Review focus"],
                ["story", "Summary"],
              ].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  role="tab"
                  aria-selected={tab === key}
                  tabIndex={tab === key ? 0 : -1}
                  id={`progress-tab-${key}`}
                  aria-controls="progress-panel"
                  onClick={() => navigate({ to: "/progress", search: { tab: key } })}
                >
                  {label}
                </button>
              ))}
            </div>
            <label className="rally-person-select">
              Player
              <select value={person?.person_id ?? ""} onChange={(event) => setPersonId(event.target.value)}>
                {!data.people.length && <option value="">No named player</option>}
                {data.people.map((entry) => (
                  <option key={entry.person_id} value={entry.person_id}>
                    {entry.name}
                  </option>
                ))}
              </select>
            </label>
            <div
              role="tabpanel"
              id="progress-panel"
              aria-labelledby={`progress-tab-${tab}`}
              className="rally-stack"
            >
              {tab === "overview" && (
                <>
                  <section className="rally-summary" aria-label="Completed analysis totals">
                    <div className="rally-stats">
                      <Stat value={data.progress.analysed_matches} label="Analysed matches" />
                      <Stat value={data.progress.total_rallies} label="Counted rallies" />
                      <Stat
                        value={data.progress.analysed_matches ? data.progress.active_play_s / 60 : null}
                        unit="min"
                        label="Recorded active play"
                      />
                    </div>
                    <p className="rally-caption">
                      These totals include every completed analysis in the current selection.
                    </p>
                  </section>
                  <Card title="Rally length by recording">
                    <p className="rally-muted">
                      Rally length across completed analyses. These are match-level observations; individual
                      player history is listed below.
                    </p>
                    {data.progress.history.length ? (
                      <>
                        <figure className="rally-bars" aria-label="Average shots per counted rally">
                          {data.progress.history.map((entry) => (
                            <MatchLink key={entry.session_id} id={entry.session_id} tab="rallies">
                              <strong>{entry.avg_rally_shots?.toFixed(1) ?? "Unavailable"}</strong>
                              {entry.avg_rally_shots != null && (
                                <span style={{ height: `${(entry.avg_rally_shots / maxAverage) * 144}px` }} />
                              )}
                              <small>{dateLabel(entry.created_at)}</small>
                            </MatchLink>
                          ))}
                        </figure>
                        <div className="rally-table-wrap">
                          <table>
                            <caption>Match-level trends and evidence</caption>
                            <thead>
                              <tr>
                                <th>Match date</th>
                                <th>Rallies</th>
                                <th>Average shots</th>
                                <th>Active play</th>
                              </tr>
                            </thead>
                            <tbody>
                              {data.progress.history.map((entry) => (
                                <tr key={entry.session_id}>
                                  <td>
                                    <MatchLink id={entry.session_id}>{dateLabel(entry.created_at)}</MatchLink>
                                  </td>
                                  <td>{entry.rallies}</td>
                                  <td>{entry.avg_rally_shots?.toFixed(1) ?? "—"}</td>
                                  <td>{(entry.active_play_s / 60).toFixed(1)} min</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </>
                    ) : (
                      <p className="rally-caption mt-4">No completed analyses to compare yet.</p>
                    )}
                  </Card>
                </>
              )}
              {tab === "records" && (
                <Card title="Recording records">
                  {data.progress.records?.length ? (
                    <div className="rally-grid rally-grid-two rally-records-grid">
                      {data.progress.records.map((record) => (
                        <MatchLink key={record.key} id={record.session_id} frame={record.frame ?? undefined}>
                          <Stat
                            value={record.value}
                            unit={record.unit}
                            label={record.label}
                            detail="Open the recording"
                          />
                        </MatchLink>
                      ))}
                    </div>
                  ) : (
                    <p className="rally-muted">Records need a completed analysis.</p>
                  )}
                  <p className="rally-caption">
                    These are recording-level records. The selected player’s match history appears below.
                  </p>
                </Card>
              )}
              {tab === "shots" && (
                <Card title="Recorded shot types">
                  <p className="rally-caption">
                    Rule-based shot naming is a preview. Counts come from the named player’s analysed match
                    events.
                  </p>
                  {person?.strokes ? (
                    <ul className="rally-list">
                      {Object.entries(person.strokes).map(([stroke, count]) => (
                        <li key={stroke}>
                          {strokeLabel(stroke)}
                          <strong>{count}</strong>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="rally-muted">Name players in analysed matches to build a shot history.</p>
                  )}
                </Card>
              )}
              {tab === "focus" && (
                <Card title="Review a recording">
                  <p className="rally-muted">
                    Pick a match and inspect its serve, return and shot patterns. Long-term challenges need
                    persistent athlete identities and challenge rules, which the current pipeline does not yet
                    record.
                  </p>
                  {data.matches
                    .filter((match) => match.analytics)
                    .slice(0, 3)
                    .map((match) => (
                      <p key={match.session.session_id}>
                        <MatchLink id={match.session.session_id} tab="tactics" className="rally-text-action">
                          Explore {match.session.title} →
                        </MatchLink>
                      </p>
                    ))}
                </Card>
              )}
              {tab === "story" && (
                <Card title="Recorded active play">
                  <p>
                    {data.progress.analysed_matches} completed recordings contain{" "}
                    {data.progress.total_rallies} counted rallies and{" "}
                    {(data.progress.active_play_s / 60).toFixed(1)} minutes of active play.
                  </p>
                  <p className="rally-muted mt-3">
                    Every observation comes from recorded events. Changes in footage, calibration and tracking
                    quality can affect comparisons.
                  </p>
                </Card>
              )}
              {person && (
                <Card title={`${person.name} · match history`}>
                  <ul className="rally-list">
                    {person.history.map((entry) => (
                      <li key={`${entry.session_id}-${entry.player_id}`}>
                        <MatchLink id={entry.session_id}>
                          {entry.title}
                          <span>
                            {entry.points_won == null
                              ? "Analysis unavailable"
                              : `${entry.points_won} points won · ${entry.points_lost} lost`}
                          </span>
                        </MatchLink>
                      </li>
                    ))}
                  </ul>
                </Card>
              )}
              {!data.progress.analysed_matches && (
                <Empty title="Your history starts with a match">
                  Complete an analysis to see trends, records and shot history here.
                </Empty>
              )}
            </div>
          </div>
        );
      }}
    </Catalogue>
  );
}
