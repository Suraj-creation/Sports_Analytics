import { shortName } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";

export function PlayerSelector({
  session,
  selected,
  onSelect,
}: {
  session: Session;
  selected: PlayerId;
  onSelect: (id: PlayerId) => void;
}) {
  const players = session.players.filter((p) => p.player_id === "P1" || p.player_id === "P2");
  return (
    <div>
      <div className="match-people">
        <span className="mr-2 text-xs text-line-2">Showing numbers for</span>
        {players.map((p) => (
          <button
            type="button"
            key={p.player_id}
            className="match-person"
            aria-pressed={selected === p.player_id}
            aria-label={`Show ${shortName(session, p.player_id)} numbers`}
            onClick={() => onSelect(p.player_id)}
          >
            <span className={`match-person-glyph ${p.player_id === "P2" ? "other" : ""}`} aria-hidden>
              {p.player_id === "P1" ? "●" : "■"}
            </span>
            {shortName(session, p.player_id)}
          </button>
        ))}
      </div>
      <p className="mt-2 text-xs text-line-2">
        These are legacy two-slot estimates. In doubles, they cannot identify four individual players; review
        the video before attributing statistics.
      </p>
    </div>
  );
}
