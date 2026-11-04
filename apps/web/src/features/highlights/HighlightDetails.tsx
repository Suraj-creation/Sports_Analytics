import * as Dialog from "@radix-ui/react-dialog";
import { ArrowUpRight, BookmarkPlus, ExternalLink, X } from "lucide-react";
import { MatchLink } from "@/features/product/ui";
import { HighlightArtwork } from "./HighlightArtwork";
import { EvidenceState } from "./HighlightCard";
import type {
  HighlightCollection,
  HighlightDefinition,
  HighlightEvidence,
  HighlightInsight,
  PersonalPick,
  PickKind,
} from "./types";
import { frameLabel } from "./types";

export function HighlightDetails({
  collection,
  insight,
  definition,
  personalPicks,
  onClose,
  onPick,
  restoreFocus,
}: {
  collection: HighlightCollection;
  insight: HighlightInsight;
  definition: HighlightDefinition;
  personalPicks: PersonalPick[];
  onClose: () => void;
  onPick: (kind: PickKind, evidence?: HighlightEvidence) => void;
  restoreFocus: HTMLElement | null;
}) {
  return (
    <Dialog.Root
      open
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="hl-overlay" />
        <Dialog.Content
          className="hl-detail"
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            restoreFocus?.focus({ preventScroll: true });
          }}
        >
          <div className="hl-dialog-heading">
            <Dialog.Title>{definition.title}</Dialog.Title>
            <Dialog.Close className="hl-icon-button" aria-label="Close highlight details">
              <X size={20} aria-hidden />
            </Dialog.Close>
          </div>
          <Dialog.Description className="hl-detail-headline">{insight.headline}</Dialog.Description>
          <div className="hl-detail-state">
            <EvidenceState insight={insight} example={collection.example} />
            <span>
              {collection.example
                ? "Synthetic example"
                : insight.origin === "player"
                  ? "Private personal selection"
                  : "Recorded observations"}
            </span>
          </div>
          <div className="hl-detail-visual">
            <HighlightArtwork visual={insight.visual} collection={collection} />
          </div>
          <p className="hl-detail-summary">{insight.summary}</p>
          {insight.metrics.length > 0 && (
            <dl className="hl-detail-metrics">
              {insight.metrics.map((metric) => (
                <div key={metric.label}>
                  <dt>{metric.label}</dt>
                  <dd>{metric.value}</dd>
                  {metric.detail && <p>{metric.detail}</p>}
                </div>
              ))}
            </dl>
          )}
          <section className="hl-detail-section" aria-label="Source evidence">
            <h3>Back to the moment</h3>
            {collection.example && (
              <p className="hl-muted">
                These are illustrative intervals. No source video is attached to the example.
              </p>
            )}
            {insight.evidence.length ? (
              <ul className="hl-evidence-list">
                {insight.evidence.map((evidence) => (
                  <li key={evidence.id}>
                    <div>
                      <strong>{evidence.label}</strong>
                      <span>
                        {frameLabel(evidence.start, collection.media)}–
                        {frameLabel(evidence.end, collection.media)}
                        {evidence.shotCount !== null ? ` · ${evidence.shotCount} shots` : " · count unknown"}
                      </span>
                      {evidence.outcome && <span>{evidence.outcome}</span>}
                      {evidence.eventStatus && (
                        <span>
                          Event status: {evidence.eventStatus.replaceAll("_", " ")}
                          {evidence.evidenceBand ? ` · ${evidence.evidenceBand} evidence` : ""}. Field-level
                          verification is separate.
                        </span>
                      )}
                    </div>
                    {!collection.example && collection.media && (
                      <MatchLink
                        id={collection.id}
                        tab="rallies"
                        frame={evidence.start}
                        className="hl-source-link"
                      >
                        Open recording <ArrowUpRight size={15} aria-hidden />
                      </MatchLink>
                    )}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="hl-muted">A supporting clip interval has not been supplied for this insight.</p>
            )}
          </section>
          <section className="hl-detail-section">
            <h3>What supports this?</h3>
            <p className="hl-muted">{insight.support}</p>
            <ul className="hl-requirements">
              {definition.requires.map((requirement) => (
                <li key={requirement}>{requirement}</li>
              ))}
            </ul>
          </section>
          {definition.pickKind && personalPicks.some((pick) => pick.kind === definition.pickKind) && (
            <section className="hl-detail-section">
              <h3>
                {definition.pickKind === "favourite"
                  ? "Your favourites · separate from the longest"
                  : "Personal selections"}
              </h3>
              <ul className="hl-evidence-list">
                {personalPicks
                  .filter((pick) => pick.kind === definition.pickKind)
                  .map((pick) => (
                    <li key={pick.id}>
                      <div>
                        <strong>
                          {collection.participants.find((person) => person.id === pick.selectorId)?.name ??
                            "Player not specified"}
                        </strong>
                        <span>
                          {frameLabel(pick.start, collection.media)}–{frameLabel(pick.end, collection.media)}
                        </span>
                        {pick.note && <p className="hl-muted">{pick.note}</p>}
                      </div>
                    </li>
                  ))}
              </ul>
            </section>
          )}
          <details className="hl-definition">
            <summary>How this insight is defined</summary>
            <p>{definition.definition}</p>
            <p className="hl-caption">
              {collection.example
                ? "Proposed definition · example version 1"
                : "UI definition · production evidence is evaluated separately"}
            </p>
          </details>
          <div className="hl-detail-footer">
            {definition.pickKind && insight.availability !== "not_applicable" && (
              <button
                type="button"
                className="hl-button hl-button-primary"
                onClick={() => onPick(definition.pickKind!, insight.evidence[0])}
              >
                <BookmarkPlus size={16} aria-hidden />
                Make a personal pick
              </button>
            )}
            {!collection.example && (
              <MatchLink id={collection.id} tab="rallies" className="hl-button hl-button-quiet">
                Review the session <ExternalLink size={15} aria-hidden />
              </MatchLink>
            )}
            {collection.example && (
              <p className="hl-caption">Example selections stay separate from your recordings.</p>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
