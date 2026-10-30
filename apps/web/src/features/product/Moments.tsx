import { useState } from "react";
import { strokeLabel } from "./model";
import { Card, Catalogue, Empty, MomentRow } from "./ui";

export function MomentsPage() {
  const [category, setCategory] = useState("all");
  const [sessionId, setSessionId] = useState("all");
  const [personId, setPersonId] = useState("all");
  return (
    <Catalogue title="Moments" lead="Selected rallies, linked to their source frames.">
      {(data) => {
        const moments = data.matches.flatMap((match) =>
          match.highlights.map((highlight) => ({ match, highlight })),
        );
        const categories = [...new Set(moments.flatMap(({ highlight }) => highlight.categories))].sort();
        const person = data.people.find((entry) => entry.person_id === personId);
        const shown = moments.filter(
          ({ match, highlight }) =>
            (sessionId === "all" || match.session.session_id === sessionId) &&
            (category === "all" || highlight.categories.includes(category)) &&
            (personId === "all" ||
              person?.history.some(
                (entry) =>
                  entry.session_id === match.session.session_id && entry.player_id === highlight.player,
              )),
        );
        return (
          <div className="rally-stack">
            <div className="rally-filters">
              <label>
                Category
                <select value={category} onChange={(event) => setCategory(event.target.value)}>
                  <option value="all">Every category</option>
                  {categories.map((value) => (
                    <option key={value} value={value}>
                      {strokeLabel(value)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Match
                <select value={sessionId} onChange={(event) => setSessionId(event.target.value)}>
                  <option value="all">Every match</option>
                  {data.matches.map(({ session }) => (
                    <option key={session.session_id} value={session.session_id}>
                      {session.title}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Player
                <select value={personId} onChange={(event) => setPersonId(event.target.value)}>
                  <option value="all">All players and unassigned moments</option>
                  {data.people.map((entry) => (
                    <option key={entry.person_id} value={entry.person_id}>
                      {entry.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <p className="rally-caption" role="status">
              {shown.length} moments · categories and reasons come from the event ranker. Player filters use
              explicit session names and recorded moment attribution.
            </p>
            {shown.map(({ match, highlight }) => (
              <Card key={`${match.session.session_id}-${highlight.rally_id}`} className="rally-moment-card">
                <MomentRow match={match} highlight={highlight} />
                <details>
                  <summary>Why this moment?</summary>
                  <ul className="rally-list">
                    {Object.entries(highlight.reasons).map(([reason, value]) => (
                      <li key={reason}>
                        {strokeLabel(reason)}
                        <span>{value.toFixed(2)}</span>
                      </li>
                    ))}
                  </ul>
                  <p className="rally-caption">
                    Internal ranking contributions describe the selection; they are not a player grade.
                  </p>
                </details>
              </Card>
            ))}
            {!shown.length && (
              <Empty title="No moments in this selection">
                Choose another filter, or analyse a recording to find its moments.
              </Empty>
            )}
          </div>
        );
      }}
    </Catalogue>
  );
}
