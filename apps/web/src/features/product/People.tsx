import { Link } from "@tanstack/react-router";
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { dateLabel } from "./model";
import { Card, Catalogue, Empty, MatchLink, Stat } from "./ui";

export function PeoplePage() {
  const [selected, setSelected] = useState<string | null>(null);
  return (
    <Catalogue title="People" lead="Match history for the player names entered in your recordings.">
      {(data) => (
        <div className="rally-stack">
          <p className="rally-caption">
            Matching names are labels, not verified identities. Points and win rates use available score
            evidence.
          </p>
          <div className="rally-grid rally-grid-two">
            {data.people.map((person) => (
              <Card key={person.person_id} className="rally-person-card">
                <div className="product-card-heading">
                  <div>
                    <h2>{person.name}</h2>
                    <p className="rally-caption">
                      {person.matches} named {person.matches === 1 ? "recording" : "recordings"}
                    </p>
                  </div>
                </div>
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
                  aria-controls={`history-${person.person_id}`}
                  onClick={() => setSelected(selected === person.person_id ? null : person.person_id)}
                >
                  {selected === person.person_id ? "Hide match history" : "View match history"}
                  <ChevronDown
                    size={16}
                    aria-hidden
                    style={{
                      transform: selected === person.person_id ? "rotate(180deg)" : undefined,
                      transition: "transform 160ms ease",
                    }}
                  />
                </button>
                {selected === person.person_id && (
                  <ul className="rally-list" id={`history-${person.person_id}`}>
                    {person.history.map((match) => (
                      <li key={`${match.session_id}-${match.player_id}`}>
                        <MatchLink id={match.session_id} tab="h2h">
                          <strong>{match.title}</strong>
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
              Open a match and name its players to build their history.{" "}
              <Link to="/matches" className="rally-inline-link">
                Browse matches
              </Link>
            </Empty>
          )}
          <section className="rally-notice" aria-labelledby="partners-note">
            <h2 id="partners-note" className="font-medium mb-2">
              Doubles and partner history
            </h2>
            <p>
              Individual doubles tracking and persistent partner identities are not available from the current
              two-track pipeline. Pair history needs those inputs before it can be measured.
            </p>
          </section>
        </div>
      )}
    </Catalogue>
  );
}
