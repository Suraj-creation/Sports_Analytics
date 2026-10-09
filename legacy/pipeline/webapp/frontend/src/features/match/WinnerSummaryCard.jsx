import { useReviewState } from "./ReviewContext";

const REASON_LABEL = { oob: "Out of bounds", net: "Hits net", land: "Wins by landing" };

export function WinnerSummaryCard() {
  const { rallies, playerA, playerB } = useReviewState();

  const aCount = rallies.filter((r) => r.winner === "A").length;
  const bCount = rallies.filter((r) => r.winner === "B").length;
  const unset = rallies.filter((r) => !r.winner).length;
  const winner = aCount === bCount ? null : aCount > bCount ? "A" : "B";
  const winnerName = winner === "B" ? playerB : winner === "A" ? playerA
    : (rallies.length === 0 ? "No rallies detected" : "Tied");

  const total = rallies.length || 1;
  const counts = { oob: 0, net: 0, land: 0 };
  let reasonUnset = 0;
  rallies.forEach((r) => { if (r.reason) counts[r.reason]++; else reasonUnset++; });

  return (
    <div className="card">
      <div className="card-head"><h2>Winner</h2></div>
      <div className="winner-display">
        <div className={"winner-name " + (winner === "B" ? "p2" : "p1")}>{winnerName}</div>
        <div className="score-line">
          {aCount} &ndash; {bCount} rallies{unset ? ` · ${unset} unassigned` : ""}
        </div>
      </div>
      {unset > 0 && (
        <div className="tie-warn">
          {unset} rally added but not yet assigned a winner &mdash; won't count toward the score until it is.
        </div>
      )}
      {unset === 0 && winner === null && rallies.length > 0 && (
        <div className="tie-warn">
          Rallies are tied at {aCount}&ndash;{bCount} &mdash; fix a rally's winner in the table to break the tie.
        </div>
      )}
      <div className="reason-block">
        <span className="detail-label">How points were won</span>
        <div className="reason-bar">
          {["oob", "net", "land"].map((k) => counts[k] ? (
            <div key={k} className={`reason-bar-seg ${k}`} style={{ width: `${(counts[k] / total) * 100}%` }} />
          ) : null)}
        </div>
        <div className="reason-legend">
          {["oob", "net", "land"].map((k) => (
            <div className="reason-legend-row" key={k}>
              <span className={`rl-swatch ${k}`} />{REASON_LABEL[k]}<span className="rl-count">{counts[k]}</span>
            </div>
          ))}
          {reasonUnset > 0 && (
            <div className="reason-legend-row">
              <span className="rl-swatch" style={{ background: "var(--amber)" }} />Not yet set
              <span className="rl-count rl-unset">{reasonUnset}</span>
            </div>
          )}
        </div>
      </div>
      <div style={{ padding: "0 20px 16px", fontSize: 12, color: "var(--ink-faint)" }}>
        Determined entirely by the rally table -- fix a rally's winner there to change it.
      </div>
    </div>
  );
}
