import { Link } from "@tanstack/react-router";
import { Card, Catalogue, Empty, MatchCard, MatchLink, Stat, Status } from "./ui";

export function HomePage() {
  return (
    <Catalogue title="Good to see you" lead="Your court time, made clear.">
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
                  <span className="rally-caption">We’re still watching this one.</span>
                </span>
                <Status match={active} />
              </MatchLink>
            )}
            {latest ? (
              <MatchCard match={latest} hero />
            ) : (
              <Empty title="Your first match starts here">
                Upload a recording to watch your rallies and explore the analysis.{" "}
                <Link to="/library" className="rally-text-action">
                  Add a recording →
                </Link>
              </Empty>
            )}
            <div className="rally-home-columns">
              <Card title="Your matches so far">
                <div className="rally-stats">
                  <Stat value={data.progress.analysed_matches} label="Analysed matches" />
                  <Stat value={data.progress.total_rallies} label="Counted rallies" />
                  <Stat
                    value={data.progress.analysed_matches ? data.progress.active_play_s / 60 : null}
                    unit="min"
                    label="Active play"
                  />
                </div>
                <p className="rally-muted">
                  Only completed analyses contribute to these totals. Open a match to review the underlying
                  events.
                </p>
                <Link to="/progress" className="rally-text-action">
                  All your progress →
                </Link>
              </Card>
              <div className="rally-stack">
                <Card title="Best so far">
                  {data.progress.records?.length ? (
                    <ul className="rally-list">
                      {data.progress.records.slice(0, 4).map((record) => (
                        <li key={record.key}>
                          <MatchLink id={record.session_id} frame={record.frame}>
                            {record.label}
                            <strong>
                              {record.value.toLocaleString()} {record.unit}
                            </strong>
                          </MatchLink>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="rally-muted">Records appear when there is enough analysed play.</p>
                  )}
                </Card>
                <Card title="People you play with">
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
                    <p className="rally-muted">Name the players in a match to build their history.</p>
                  )}
                  <Link to="/people" className="rally-text-action">
                    Everyone →
                  </Link>
                </Card>
              </div>
            </div>
            <Card title="Lately">
              <ul className="rally-list">
                {data.matches.slice(0, 5).map((match) => (
                  <li key={match.session.session_id}>
                    <MatchLink id={match.session.session_id}>
                      {match.session.title}
                      <Status match={match} />
                    </MatchLink>
                  </li>
                ))}
              </ul>
              {!data.matches.length && <p className="rally-muted">Your recordings will appear here.</p>}
            </Card>
          </div>
        );
      }}
    </Catalogue>
  );
}
