import { Link } from "@tanstack/react-router";
import { ArrowRight, Plus } from "lucide-react";
import { dateLabel } from "./model";
import { Card, Catalogue, Empty, MatchCard, MatchLink, Stat, Status } from "./ui";

export function HomePage() {
  return (
    <Catalogue
      title="Home"
      lead="Your recordings, ready for review."
      actions={
        <Link to="/library" className="rally-action rally-action-primary">
          <Plus size={16} aria-hidden />
          Add a recording
        </Link>
      }
    >
      {(data) => {
        const latest = data.matches.find((match) => match.analytics);
        const active = data.matches.find((match) =>
          ["created", "ingesting", "analysing"].includes(match.session.status),
        );
        return (
          <div className="rally-stack">
            {active && (
              <MatchLink id={active.session.session_id} className="rally-processing">
                <span>
                  <strong>{active.session.title}</strong>
                  <span className="rally-caption">Processing continues on your connected server.</span>
                </span>
                <Status match={active} />
                <ArrowRight size={16} aria-hidden />
              </MatchLink>
            )}
            <section aria-label="Completed analysis totals" className="rally-summary">
              <div className="rally-stats">
                <Stat value={data.progress.analysed_matches} label="Analysed matches" />
                <Stat value={data.progress.total_rallies} label="Counted rallies" />
                <Stat
                  value={data.progress.analysed_matches ? data.progress.active_play_s / 60 : null}
                  unit="min"
                  label="Active play"
                />
              </div>
              <p className="rally-caption">
                Totals use completed analyses.{" "}
                <Link to="/progress" className="rally-inline-link">
                  View progress
                </Link>
              </p>
            </section>
            {latest ? (
              <section>
                <h2 className="rally-section-title">Latest analysis</h2>
                <MatchCard match={latest} hero />
              </section>
            ) : (
              <Empty title="Add your first recording">
                <p>
                  Upload a video or import a YouTube recording to review rallies and inspect the analysis.
                </p>
                <Link to="/library" className="rally-action rally-action-primary">
                  Add a recording <ArrowRight size={16} aria-hidden />
                </Link>
              </Empty>
            )}
            <div className="rally-home-columns">
              <Card>
                <div className="rally-section-heading">
                  <h2>Recent recordings</h2>
                  <Link to="/matches" className="rally-text-action">
                    View all <ArrowRight size={16} aria-hidden />
                  </Link>
                </div>
                <ul className="rally-list rally-recording-list">
                  {data.matches.slice(0, 5).map((match) => (
                    <li key={match.session.session_id}>
                      <MatchLink id={match.session.session_id}>
                        <span>
                          <strong>{match.session.title}</strong>
                          <span className="rally-caption">{dateLabel(match.session.created_at)}</span>
                        </span>
                        <Status match={match} />
                      </MatchLink>
                    </li>
                  ))}
                </ul>
                {!data.matches.length && (
                  <p className="rally-muted">Your saved recordings will appear here.</p>
                )}
              </Card>
              <div className="rally-stack">
                <Card title="Recording records">
                  {data.progress.records?.length ? (
                    <ul className="rally-list">
                      {data.progress.records.slice(0, 4).map((record) => (
                        <li key={record.key}>
                          <MatchLink id={record.session_id} frame={record.frame}>
                            <span>{record.label}</span>
                            <strong>
                              {record.value.toLocaleString()} {record.unit}
                            </strong>
                          </MatchLink>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="rally-muted">Records appear after a completed analysis.</p>
                  )}
                </Card>
                <Card>
                  <div className="rally-section-heading">
                    <h2>Named players</h2>
                    <Link to="/people" className="rally-text-action">
                      View all <ArrowRight size={16} aria-hidden />
                    </Link>
                  </div>
                  {data.people.length ? (
                    <ul className="rally-list">
                      {data.people.slice(0, 4).map((person) => (
                        <li key={person.person_id}>
                          <span>{person.name}</span>
                          <span>{person.matches} matches</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="rally-muted">Name players in a recording to build their match history.</p>
                  )}
                </Card>
              </div>
            </div>
          </div>
        );
      }}
    </Catalogue>
  );
}
