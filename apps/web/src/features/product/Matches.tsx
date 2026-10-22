import { Link } from "@tanstack/react-router";
import { useState } from "react";
import { filterMatches } from "./model";
import { Catalogue, Empty, MatchCard } from "./ui";

export function MatchesPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  return (
    <Catalogue title="Your matches" lead="Every recording, with its rallies, shots and moments.">
      {(data) => {
        const shown = filterMatches(data.matches, search, status);
        return (
          <div className="rally-stack">
            <div className="rally-filters">
              <label>
                Find a match
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search title or player"
                  type="search"
                />
              </label>
              <label>
                Processing status
                <select value={status} onChange={(event) => setStatus(event.target.value)}>
                  <option value="all">All matches</option>
                  <option value="analysed">Analysed</option>
                  <option value="analysing">Analysing</option>
                  <option value="ready_to_play">Ready to analyse</option>
                  <option value="failed">Failed</option>
                </select>
              </label>
              <Link to="/library" className="rally-action">
                Add a recording
              </Link>
            </div>
            <p className="rally-caption" role="status">
              {shown.length} of {data.matches.length} matches
            </p>
            {shown.map((match) => (
              <MatchCard key={match.session.session_id} match={match} />
            ))}
            {!shown.length && (
              <Empty title={data.matches.length ? "No matching recordings" : "No recordings yet"}>
                {data.matches.length
                  ? "Try a different search or processing status."
                  : "Add a recording to start analysing your play."}
              </Empty>
            )}
          </div>
        );
      }}
    </Catalogue>
  );
}
