import { BookmarkPlus } from "lucide-react";
import { highlightProvider } from "./providers";
import type { HighlightCollection, HighlightVisual } from "./types";

export function HighlightArtwork({
  visual,
  collection,
}: {
  visual: HighlightVisual;
  collection: HighlightCollection;
}) {
  if (visual.kind === "diagram")
    return (
      <div className="hl-diagram">
        {highlightProvider(collection.sport)?.renderDiagram(visual.variant, collection.format)}
        <span className="hl-art-caption">
          {visual.illustrated ? "Illustrated positions" : "Position evidence"}
        </span>
      </div>
    );
  if (visual.kind === "scores")
    return (
      <div className="hl-score-art" aria-label="Score recovery sequence">
        {visual.points.map((point) => (
          <div key={point.label}>
            <span className="hl-score-value">{point.value}</span>
            <span>{point.label}</span>
          </div>
        ))}
      </div>
    );
  if (visual.kind === "bars")
    return (
      <div className="hl-bars">
        {visual.rows.map((row) => {
          const percent =
            Number.isFinite(row.value) && Number.isFinite(row.max) && row.max > 0
              ? Math.max(0, Math.min(100, (row.value / row.max) * 100))
              : 0;
          return (
            <div className="hl-bar-row" key={row.label}>
              <div className="hl-bar-label">
                <span>{row.label}</span>
                <strong>{row.display}</strong>
              </div>
              <div className="hl-bar-track" aria-hidden>
                <span style={{ width: `${percent}%` }} />
              </div>
              {row.detail && <p>{row.detail}</p>}
            </div>
          );
        })}
      </div>
    );
  if (visual.kind === "record")
    return (
      <div className="hl-record-art">
        <div>
          <span>Previous</span>
          <strong>
            {visual.previous}
            <small>{visual.unit}</small>
          </strong>
        </div>
        <svg viewBox="0 0 48 24" width="48" height="24" fill="none" aria-hidden>
          <path d="M3 12H43M34 3L43 12L34 21" stroke="currentColor" strokeWidth="1.5" />
        </svg>
        <div>
          <span>This session</span>
          <strong>
            {visual.current}
            <small>{visual.unit}</small>
          </strong>
        </div>
      </div>
    );
  return (
    <div className="hl-invitation">
      <BookmarkPlus size={28} strokeWidth={1.25} aria-hidden />
      <span>{visual.label}</span>
    </div>
  );
}
