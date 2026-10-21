import { useRef } from "react";
import { useReviewState, useReviewDispatch, sortedRallies, fmt } from "./ReviewContext";

export function RallyTimeline({ videoRef }) {
  const { rallies, selectedId, total } = useReviewState();
  const dispatch = useReviewDispatch();
  const timelineRef = useRef(null);
  const dragRef = useRef(null); // { id, edge, rect } -- ref, not state: a drag shouldn't trigger its own re-render loop

  const sorted = sortedRallies(rallies);

  let cursor = 0;
  const gaps = [];
  sorted.forEach((r) => {
    if (r.start - cursor > 14) gaps.push([cursor, r.start]);
    cursor = Math.max(cursor, r.end);
  });
  if (total - cursor > 14) gaps.push([cursor, total]);

  function addRallyInGap(gs, ge) {
    const width = Math.min(20, ge - gs - 4);
    const start = gs + Math.max(2, (ge - gs - width) / 2);
    dispatch({ type: "ADD_RALLY", start, end: start + width });
  }

  function onTimelineClick(e) {
    if (!videoRef.current || !total) return;
    const rect = timelineRef.current.getBoundingClientRect();
    const t = ((e.clientX - rect.left) / rect.width) * total;
    videoRef.current.currentTime = Math.max(0, Math.min(total, t));
  }

  function startDrag(e, id, edge) {
    e.stopPropagation();
    e.preventDefault();
    dragRef.current = { id, edge, rect: timelineRef.current.getBoundingClientRect() };
    window.addEventListener("pointermove", onDrag);
    window.addEventListener("pointerup", endDrag);
  }
  function onDrag(e) {
    const d = dragRef.current;
    if (!d) return;
    let t = ((e.clientX - d.rect.left) / d.rect.width) * total;
    t = Math.max(0, Math.min(total, t));
    dispatch({ type: "DRAG_UPDATE", id: d.id, edge: d.edge, time: t });
  }
  function endDrag() {
    if (dragRef.current) dispatch({ type: "DRAG_COMMIT" });
    dragRef.current = null;
    window.removeEventListener("pointermove", onDrag);
    window.removeEventListener("pointerup", endDrag);
  }

  const tickEvery = total > 900 ? 120 : 60;
  const ticks = [];
  if (total > 0) {
    for (let t = 0; t <= total; t += tickEvery) ticks.push(t);
  }

  return (
    <div className="card">
      <div className="card-head">
        <h2>Rally timeline</h2>
        <span style={{ fontSize: 12, color: "var(--ink-faint)" }}>Drag edges to trim &middot; click a gap to add a missed rally</span>
      </div>
      <div className="timeline-wrap">
        <div className="timeline-legend">
          <span className="legend-item"><span className="legend-swatch" style={{ background: "var(--court-soft)", border: "1.5px solid var(--court)" }} />Detected</span>
          <span className="legend-item"><span className="legend-swatch" style={{ background: "var(--amber-soft)", border: "1.5px solid var(--amber)" }} />Low confidence</span>
          <span className="legend-item"><span className="legend-swatch" style={{ background: "var(--slate-soft)", border: "1.5px dashed var(--slate)" }} />Added by you</span>
          <span className="legend-item"><span className="legend-swatch" style={{ border: "1.5px dashed var(--line-strong)", background: "transparent" }} />Unmarked gap</span>
        </div>
        <div className="timeline" ref={timelineRef} onClick={onTimelineClick}>
          {gaps.map(([gs, ge], i) => (
            <div key={i} className="gap-chip"
                 style={{ left: `${(gs / total) * 100}%`, width: `${((ge - gs) / total) * 100}%` }}
                 onClick={(e) => { e.stopPropagation(); addRallyInGap(gs, ge); }}>
              + add missed rally
            </div>
          ))}
          {sorted.map((r) => (
            <div key={r.id}
                 className={"rally-block" + (r.id === selectedId ? " selected" : "") +
                            (r.flagged ? " flagged" : "") + (r.source === "user" ? " user-added" : "")}
                 style={{ left: `${(r.start / total) * 100}%`, width: `${Math.max(0.6, ((r.end - r.start) / total) * 100)}%` }}
                 onClick={(e) => { e.stopPropagation(); dispatch({ type: "SELECT_RALLY", id: r.id }); }}>
              <span className="winner-dot" style={{ background: r.winner === "A" ? "var(--p1)" : r.winner === "B" ? "var(--p2)" : "var(--ink-faint)" }} />
              <div className="rally-handle left" onPointerDown={(e) => startDrag(e, r.id, "start")} />
              <div className="rally-handle right" onPointerDown={(e) => startDrag(e, r.id, "end")} />
            </div>
          ))}
        </div>
        <div className="ruler">
          {ticks.map((t) => (
            <div key={t} className="tick" style={{ left: `${(t / total) * 100}%` }}>{fmt(t)}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
