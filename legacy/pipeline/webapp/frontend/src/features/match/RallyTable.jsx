import { useState } from "react";
import { useReviewState, useReviewDispatch, sortedRallies, computeScores, fmt } from "./ReviewContext";

function TimeInput({ value, onCommit }) {
  const [text, setText] = useState(fmt(value));
  return (
    <input
      className="time-input"
      value={text}
      onChange={(e) => setText(e.target.value)}
      onBlur={() => { onCommit(text); setText(fmt(value)); }}
      onFocus={() => setText(fmt(value))}
      onKeyDown={(e) => { if (e.key === "Enter") e.currentTarget.blur(); }}
    />
  );
}

export function RallyTable() {
  const { rallies, selectedId, total } = useReviewState();
  const dispatch = useReviewDispatch();
  const sorted = sortedRallies(rallies);
  const scores = computeScores(rallies);

  return (
    <div className="card" id="rally-list-card">
      <div className="card-head">
        <h2>Rally-by-rally</h2>
        <span style={{ fontSize: 12, color: "var(--ink-faint)", fontWeight: 400, textTransform: "none", letterSpacing: "normal" }}>
          Every field below is editable
        </span>
      </div>
      <div className="table-scroll">
        <table className="rally-table">
          <thead>
            <tr><th>#</th><th>Start</th><th>End</th><th>Winner</th><th>Won by</th><th>Score</th><th /></tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => {
              const rowClass = [
                r.flagged ? "flagged-row" : "",
                r.source === "user" ? "user-row" : "",
                r.id === selectedId ? "selected-row" : "",
              ].filter(Boolean).join(" ");
              const [sa, sb] = scores[r.id];
              return (
                <tr className={rowClass} key={r.id}>
                  <td className="rally-idx-cell">
                    {r.flagged && <span className="rt-flag-dot" title={r.note || ""} />}
                    {i + 1}
                  </td>
                  <td><TimeInput value={r.start} onCommit={(v) => dispatch({ type: "SET_TIME", id: r.id, field: "start", value: v })} /></td>
                  <td><TimeInput value={r.end} onCommit={(v) => dispatch({ type: "SET_TIME", id: r.id, field: "end", value: v })} /></td>
                  <td>
                    <div className="winner-toggle">
                      <button className={"wtbtn wtbtn-sm" + (r.winner === "A" ? " on-p1" : "")}
                              onClick={() => dispatch({ type: "SET_WINNER", id: r.id, winner: "A" })}>A</button>
                      <button className={"wtbtn wtbtn-sm" + (r.winner === "B" ? " on-p2" : "")}
                              onClick={() => dispatch({ type: "SET_WINNER", id: r.id, winner: "B" })}>B</button>
                    </div>
                  </td>
                  <td>
                    <div className="reason-toggle">
                      <button className={"rtbtn" + (r.reason === "oob" ? " on-oob" : "")} title="Out of bounds"
                              onClick={() => dispatch({ type: "SET_REASON", id: r.id, reason: "oob" })}>OOB</button>
                      <button className={"rtbtn" + (r.reason === "net" ? " on-net" : "")} title="Hits net"
                              onClick={() => dispatch({ type: "SET_REASON", id: r.id, reason: "net" })}>Net</button>
                      <button className={"rtbtn" + (r.reason === "land" ? " on-land" : "")} title="Wins by landing"
                              onClick={() => dispatch({ type: "SET_REASON", id: r.id, reason: "land" })}>Land</button>
                    </div>
                  </td>
                  <td className="rt-score">
                    <span className="s1">{sa}</span>&ndash;<span className="s2">{sb}</span>
                    {!r.winner && <span className="rt-unset" title="Winner not set -- score not updated by this rally yet">?</span>}
                  </td>
                  <td>
                    <button className="row-del" title="Delete this rally" aria-label="Delete rally"
                            onClick={() => dispatch({ type: "DELETE_RALLY", id: r.id })}>&times;</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="table-foot">
        <button className="btn btn-sm" onClick={() => {
          const lastEnd = sorted.length ? sorted[sorted.length - 1].end : 0;
          let start = lastEnd + 10;
          if (start + 18 > total) start = Math.max(0, total - 20);
          dispatch({ type: "ADD_RALLY", start, end: Math.min(total, start + 20) });
        }}>+ Add missed rally</button>
        <span style={{ fontSize: 12, color: "var(--ink-faint)", marginLeft: 10 }}>
          Model misses one occasionally -- add it wherever it actually happened.
        </span>
      </div>
    </div>
  );
}
