import { ArrowRight, Bookmark, CircleCheck, CircleDashed } from "lucide-react";
import { HighlightArtwork } from "./HighlightArtwork";
import type {
  HighlightCollection,
  HighlightDefinition,
  HighlightEvidence,
  HighlightInsight,
  PickKind,
} from "./types";
import { frameLabel } from "./types";

export function EvidenceState({ insight, example }: { insight: HighlightInsight; example: boolean }) {
  const label =
    insight.availability === "not_applicable"
      ? "Not applicable"
      : insight.availability === "missing"
        ? insight.definitionId === "smile"
          ? "Make a pick"
          : "Needs evidence"
        : insight.availability === "review"
          ? "Needs review"
          : insight.origin === "player"
            ? "Personal pick"
            : example
              ? "Example insight"
              : "Available";
  const Icon = insight.availability === "available" ? CircleCheck : CircleDashed;
  return (
    <span className="hl-evidence-state" data-state={insight.availability}>
      <Icon size={13} aria-hidden />
      {label}
    </span>
  );
}

export function HighlightCard({
  insight,
  definition,
  collection,
  onInspect,
  onPick,
  featured = false,
  compact = false,
}: {
  insight: HighlightInsight;
  definition: HighlightDefinition;
  collection: HighlightCollection;
  onInspect: (id: string) => void;
  onPick: (kind: PickKind, evidence?: HighlightEvidence) => void;
  featured?: boolean;
  compact?: boolean;
}) {
  const firstEvidence = insight.evidence[0];
  if (compact)
    return (
      <button type="button" className="hl-shortlist-item" onClick={() => onInspect(definition.id)}>
        <div className="hl-shortlist-art" aria-hidden>
          <HighlightArtwork visual={insight.visual} collection={collection} />
        </div>
        <span>
          <strong>{definition.title}</strong>
          <span className="hl-caption">
            {insight.metrics[0]?.value ??
              (insight.availability === "review" ? "A closer look" : "Explore the moment")}
          </span>
        </span>
        <ArrowRight size={16} aria-hidden />
      </button>
    );
  return (
    <article className={featured ? "hl-feature" : "hl-card"} data-availability={insight.availability}>
      <button
        type="button"
        className="hl-media-button"
        onClick={() => onInspect(definition.id)}
        aria-label={`Explore ${definition.title}`}
      >
        <HighlightArtwork visual={insight.visual} collection={collection} />
        {firstEvidence && (
          <span className="hl-media-time">
            {frameLabel(firstEvidence.start, collection.media)}
            {firstEvidence.shotCount !== null ? ` · ${firstEvidence.shotCount} shots` : ""}
          </span>
        )}
        {featured && (
          <span className="hl-media-open">
            Explore this rally <ArrowRight size={16} aria-hidden />
          </span>
        )}
      </button>
      <div className="hl-card-body">
        <div className="hl-card-meta">
          <span>{definition.title}</span>
          <EvidenceState insight={insight} example={collection.example} />
        </div>
        {featured ? (
          <h2>{insight.headline}</h2>
        ) : (
          <h4>
            <button type="button" onClick={() => onInspect(definition.id)}>
              {insight.headline}
            </button>
          </h4>
        )}
        <p>{insight.summary}</p>
        <div className="hl-card-actions">
          <button type="button" className="hl-text-button" onClick={() => onInspect(definition.id)}>
            {insight.availability === "missing" ? "See what's needed" : "Take a closer look"}
            <ArrowRight size={15} aria-hidden />
          </button>
          {definition.pickKind && insight.availability !== "not_applicable" && (
            <button
              type="button"
              className="hl-icon-button"
              onClick={() => onPick(definition.pickKind!, firstEvidence)}
              aria-label={`Keep a ${definition.title.toLocaleLowerCase()} selection`}
            >
              <Bookmark size={17} aria-hidden />
            </button>
          )}
        </div>
      </div>
    </article>
  );
}
