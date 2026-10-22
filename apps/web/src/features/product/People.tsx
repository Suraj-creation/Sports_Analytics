import { useState } from "react";
import { dateLabel } from "./model";
import { Card, Catalogue, Empty, MatchLink, Stat } from "./ui";

export function PeoplePage() {
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <Catalogue title="People you play with" lead="Match history for the players you have named.">
      {(data) => (
        <div className="rally-stack">
          <Card title="Partners">
            <p className="rally-muted">
              Individual doubles tracking and persistent partner identities are not available from the current
              two-track pipeline. Pair history will need those inputs before it can be measured.
            </p>
          </Card>
          <section>
            <h2 className="rally-section-title">Players and opponents</h2>
            <p className="rally-caption">
              History groups explicit player names. Matching names are labels, not verified identities.
            </p>
            <div className="rally-grid rally-grid-two">
              {data.people.map((person) => (
                <Card key={person.person_id} title={person.name}>
                  <div className="rally-stats">
                    <Stat value={person.matches} label="Matches" />
                    <Stat value={person.points_won} label="Points won" />
                    <Stat
                      value={person.win_rate == null ? null : person.win_rate * 100}
                      unit="%"
                      label="Point win rate"
                    />
                  </div>
                  <button
                    type="button"
                    className="rally-text-action"
                    aria-expanded={selected === person.person_id}
                    onClick={() => setSelected(selected === person.person_id ? null : person.person_id)}
                  >
                    View match history
                  </button>
                  {selected === person.person_id && (
                    <ul className="rally-list">
                      {person.history.map((match) => (
                        <li key={`${match.session_id}-${match.player_id}`}>
                          <MatchLink id={match.session_id} tab="h2h">
                            {match.title}
                            <span>
                              {dateLabel(match.created_at)} ·{" "}
                              {match.points_won == null
                                ? "Analysis unavailable"
                                : `${match.points_won}–${match.points_lost} points`}
                            </span>
                          </MatchLink>
                        </li>
                      ))}
                    </ul>
                  )}
                </Card>
              ))}
            </div>
            {!data.people.length && (
              <Empty title="No named players yet">
                Open a match, name its players, and their history will appear here.
              </Empty>
            )}
          </section>
        </div>
      )}
    </Catalogue>
  );
}
