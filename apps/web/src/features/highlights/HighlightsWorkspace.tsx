import { ArrowRight, Bookmark, Check, LockKeyhole, Search, X } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { MatchLink } from "@/features/product/ui";
import { HighlightCard } from "./HighlightCard";
import { HighlightDetails } from "./HighlightDetails";
import { PersonalPickDialog } from "./PersonalPickDialog";
import { frameLabel, GROUP_LABELS, PICK_LABELS } from "./types";
import type {
  HighlightCollection,
  HighlightEvidence,
  HighlightGroup,
  HighlightInsight,
  PersonalPick,
  PickKind,
} from "./types";
import { usePersonalPicks } from "./usePersonalPicks";

type CollectionView = "all" | "picks" | "review";

export function HighlightsWorkspace({
  collection,
  subjectId,
}: {
  collection: HighlightCollection;
  subjectId: string;
}) {
  const id = useId();
  const [view, setView] = useState<CollectionView>("all");
  const [group, setGroup] = useState<HighlightGroup | "all">("all");
  const [search, setSearch] = useState("");
  const [selectedId, setSelected] = useState<string | null>(null);
  const [pickKind, setPickKind] = useState<PickKind | null>(null);
  const [pickNonce, setPickNonce] = useState(0);
  const [pickEvidence, setPickEvidence] = useState<HighlightEvidence | undefined>();
  const [notice, setNotice] = useState("");
  const [removed, setRemoved] = useState<PersonalPick | null>(null);
  const undoControl = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    if (removed) undoControl.current?.focus({ preventScroll: true });
  }, [removed]);
  const returnFocus = useRef<HTMLElement | null>(null);
  const drafts = usePersonalPicks(collection);
  const subjectPerson = collection.participants.find((person) => `person:${person.id}` === subjectId);
  const subjectTeamId = subjectId.startsWith("team:") ? subjectId.slice(5) : subjectPerson?.teamId;
  const subjectMembers = collection.participants
    .filter((person) => person.teamId === subjectTeamId)
    .map((person) => person.id);
  const matchesPickScope = (pick: PersonalPick) =>
    !subjectId ||
    pick.selectorId === subjectPerson?.id ||
    (subjectId.startsWith("team:") && pick.selectorId !== null && subjectMembers.includes(pick.selectorId));
  const matchesSubject = (ids: string[]) =>
    !subjectId ||
    !ids.length ||
    ids.includes(subjectId) ||
    Boolean(subjectPerson?.teamId && ids.includes(`team:${subjectPerson.teamId}`)) ||
    (subjectId.startsWith("team:") && subjectMembers.some((member) => ids.includes(`person:${member}`)));
  const insights = collection.insights.map((insight): HighlightInsight => {
    const definition = collection.definitions.find((entry) => entry.id === insight.definitionId);
    if (
      !definition?.pickKind ||
      definition.pickKind === "favourite" ||
      insight.availability === "not_applicable"
    )
      return insight;
    const pick = drafts.picks
      .filter((entry) => entry.kind === definition.pickKind && matchesPickScope(entry))
      .at(-1);
    if (!pick) return insight;
    const person = collection.participants.find((entry) => entry.id === pick.selectorId);
    return {
      ...insight,
      origin: "player",
      subjectIds: person ? [`person:${person.id}`, ...(person.teamId ? [`team:${person.teamId}`] : [])] : [],
      availability: definition.pickKind === "smile" ? "available" : "review",
      headline:
        definition.pickKind === "smile"
          ? "A moment you chose to keep."
          : `Your pick: ${definition.title.toLocaleLowerCase()}.`,
      summary:
        pick.note || "A private personal selection. It does not verify the shot, hitter or rally outcome.",
      support: `Private local draft · picked by ${person?.name ?? "an unspecified player"}${definition.pickKind !== "smile" ? " · sporting evidence still needs review" : ""}`,
      metrics: [],
      evidence: [
        {
          id: pick.rallyId ?? pick.id,
          label: collection.rallies.find((entry) => entry.id === pick.rallyId)?.label ?? "Custom moment",
          start: pick.start,
          end: pick.end,
          shotCount: null,
          outcome: null,
        },
      ],
      visual: { kind: "invitation", label: PICK_LABELS[pick.kind] },
    };
  });
  const term = search.trim().toLocaleLowerCase();
  const matching = insights.filter((insight) => {
    const definition = collection.definitions.find((entry) => entry.id === insight.definitionId);
    return (
      definition &&
      matchesSubject(insight.subjectIds) &&
      (group === "all" || definition.group === group) &&
      (view !== "review" || insight.availability === "review" || insight.availability === "missing") &&
      (!term ||
        `${definition.title} ${insight.headline} ${insight.summary}`.toLocaleLowerCase().includes(term))
    );
  });
  const visiblePicks = drafts.picks.filter(
    (pick) =>
      matchesPickScope(pick) &&
      (!term ||
        `${PICK_LABELS[pick.kind]} ${pick.note} ${collection.participants.find((person) => person.id === pick.selectorId)?.name ?? ""}`
          .toLocaleLowerCase()
          .includes(term)),
  );
  const featured = insights.find((insight) => insight.definitionId === "rally");
  const featureDefinition = collection.definitions.find(
    (definition) => definition.id === featured?.definitionId,
  );
  const shortlist = insights
    .filter(
      (insight) =>
        insight.definitionId !== "rally" &&
        insight.availability !== "not_applicable" &&
        insight.availability !== "missing",
    )
    .slice(0, 3);
  const selected = insights.find((insight) => insight.definitionId === selectedId);
  const selectedDefinition = collection.definitions.find((definition) => definition.id === selectedId);
  const openDetail = (target: string) => {
    returnFocus.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setSelected(target);
  };
  const openPick = (kind: PickKind, evidence?: HighlightEvidence) => {
    if (document.activeElement instanceof HTMLElement && !document.activeElement.closest(".hl-detail"))
      returnFocus.current = document.activeElement;
    setSelected(null);
    setPickEvidence(evidence);
    setPickNonce((n) => n + 1);
    setPickKind(kind);
  };
  const reset = () => {
    setGroup("all");
    setSearch("");
    setView("all");
  };

  return (
    <>
      <div className="hl-session-heading">
        <div>
          <h2>{collection.title}</h2>
          <p>{collection.scope}</p>
        </div>
        <button type="button" className="hl-button hl-button-primary" onClick={() => openPick("smile")}>
          <Bookmark size={16} aria-hidden />
          Add a moment
        </button>
      </div>
      {view === "all" && !term && group === "all" && !subjectId && featured && featureDefinition && (
        <section className="hl-feature-layout" aria-label="Featured highlights">
          <HighlightCard
            featured
            insight={featured}
            definition={featureDefinition}
            collection={collection}
            onInspect={openDetail}
            onPick={openPick}
          />
          <aside className="hl-shortlist">
            <h2>Worth another look</h2>
            <p className="hl-muted">A few different ways to remember the game.</p>
            <div className="hl-shortlist-items">
              {shortlist.map((insight) => {
                const definition = collection.definitions.find((entry) => entry.id === insight.definitionId);
                return definition ? (
                  <HighlightCard
                    compact
                    key={definition.id}
                    insight={insight}
                    definition={definition}
                    collection={collection}
                    onInspect={openDetail}
                    onPick={openPick}
                  />
                ) : null;
              })}
            </div>
            {!shortlist.length && (
              <p className="hl-muted hl-shortlist-empty">
                More moments will appear here when their supporting evidence is available. You can also make a
                personal pick.
              </p>
            )}
            <div className="hl-shortlist-note">
              <LockKeyhole size={16} aria-hidden />
              <p>Your favourite doesn't have to be the longest. Keep the one that means something to you.</p>
            </div>
          </aside>
        </section>
      )}
      <section className="hl-collection" aria-labelledby={`${id}-collection`}>
        <div className="hl-collection-heading">
          <h2 id={`${id}-collection`}>Your highlight collection</h2>
          <p className="hl-caption">Ten kinds of insight. A place for your own picks.</p>
        </div>
        <div className="hl-collection-toolbar">
          <div className="hl-view-tabs" role="group" aria-label="Highlight view">
            {(
              [
                ["all", "All highlights"],
                ["picks", "Your picks"],
                ["review", "Needs attention"],
              ] as const
            ).map(([value, label]) => (
              <button type="button" key={value} aria-pressed={view === value} onClick={() => setView(value)}>
                {label}
                {value === "picks" && <span>{drafts.picks.length}</span>}
              </button>
            ))}
          </div>
          <label className="hl-search" htmlFor={`${id}-search`}>
            <Search size={16} aria-hidden />
            <span className="sr-only">Search highlights and personal picks</span>
            <input
              id={`${id}-search`}
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={view === "picks" ? "Search your picks" : "Find a highlight"}
            />
          </label>
        </div>
        {view !== "picks" && (
          <div className="hl-group-filters" role="group" aria-label="Insight category">
            {(
              [
                ["all", "Everything"],
                ["moments", "Moments"],
                ["patterns", "Match patterns"],
                ["history", "Your history"],
              ] as const
            ).map(([value, label]) => (
              <button
                type="button"
                key={value}
                aria-pressed={group === value}
                onClick={() => setGroup(value)}
              >
                {label}
              </button>
            ))}
          </div>
        )}
        <div className="hl-results-caption">
          <p role="status" aria-live="polite">
            {view === "picks"
              ? `${visiblePicks.length} private ${visiblePicks.length === 1 ? "pick" : "picks"}`
              : `${matching.length} ${matching.length === 1 ? "insight" : "insights"}`}
            {subjectId ? " in this view" : ""}
          </p>
          {(term || group !== "all") && (
            <button type="button" className="hl-text-button" onClick={reset}>
              Clear filters
              <X size={13} aria-hidden />
            </button>
          )}
        </div>
        {drafts.issue && (
          <p className="hl-storage-notice" role="status">
            {drafts.issue}
          </p>
        )}
        {notice && (
          <div className="hl-save-notice" role="status">
            <Check size={15} aria-hidden />
            <span>{notice}</span>
            {removed && (
              <button
                ref={undoControl}
                type="button"
                className="hl-text-button"
                onClick={() => {
                  const issue = drafts.restore(removed);
                  if (issue) setNotice(issue);
                  else {
                    setRemoved(null);
                    setNotice("Moment restored to your private drafts.");
                  }
                }}
              >
                Undo removal
              </button>
            )}
          </div>
        )}
        {view === "picks" ? (
          <>
            <p className="hl-private hl-picks-scope">
              <LockKeyhole size={14} aria-hidden />
              Private drafts · this device only{collection.example ? " · example selections" : ""}
            </p>
            {visiblePicks.length ? (
              <ul className="hl-picks-list">
                {visiblePicks.toReversed().map((pick: PersonalPick) => (
                  <li key={pick.id}>
                    <div className="hl-pick-mark">
                      <Bookmark size={19} strokeWidth={1.5} aria-hidden />
                    </div>
                    <div className="hl-pick-copy">
                      <h3>{PICK_LABELS[pick.kind]}</h3>
                      <p>
                        {collection.rallies.find((rally) => rally.id === pick.rallyId)?.label ??
                          "Custom moment"}{" "}
                        · {frameLabel(pick.start, collection.media)}–{frameLabel(pick.end, collection.media)}
                      </p>
                      {pick.note && <blockquote>{pick.note}</blockquote>}
                      <span className="hl-caption">
                        Picked by{" "}
                        {collection.participants.find((person) => person.id === pick.selectorId)?.name ??
                          "an unspecified player"}
                      </span>
                    </div>
                    <div className="hl-pick-actions">
                      {!collection.example && (
                        <MatchLink
                          id={collection.id}
                          tab="rallies"
                          frame={pick.start}
                          className="hl-text-button"
                        >
                          Open
                          <ArrowRight size={15} aria-hidden />
                        </MatchLink>
                      )}
                      <button
                        type="button"
                        className="hl-icon-button"
                        aria-label={`Remove ${PICK_LABELS[pick.kind]} draft`}
                        onClick={() => {
                          drafts.remove(pick.id);
                          setRemoved(pick);
                          setNotice("Moment removed from your private drafts.");
                        }}
                      >
                        <X size={17} aria-hidden />
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="hl-empty-state">
                <Bookmark size={28} strokeWidth={1.25} aria-hidden />
                <h3>{term || subjectId ? "No picks in this view" : "A favourite is yours to choose."}</h3>
                <p>
                  {term || subjectId
                    ? "Try another player or clear your search. Unknown selectors are kept in the Everyone view."
                    : "Keep a laugh, a long rally or a return that surprised you. Your picks don't need a performance score."}
                </p>
                <button
                  type="button"
                  className="hl-button hl-button-primary"
                  onClick={() => openPick("smile")}
                >
                  Choose a moment
                </button>
              </div>
            )}
            {drafts.staleCount > 0 && (
              <details className="hl-archived-drafts">
                <summary>
                  Manage {drafts.staleCount} older {drafts.staleCount === 1 ? "draft" : "drafts"}
                </summary>
                <p className="hl-caption">
                  Their source or analysis revision differs. These drafts are preserved, kept out of current
                  insights, and can be removed to make room.
                </p>
                <ul className="hl-evidence-list">
                  {drafts.archivedPicks.map((pick) => (
                    <li key={pick.id}>
                      <div>
                        <strong>{PICK_LABELS[pick.kind]}</strong>
                        <span>
                          Analysis revision {pick.revision} · frames {pick.start}–{pick.end}
                        </span>
                        {pick.note && <p className="hl-muted">{pick.note}</p>}
                      </div>
                      <button
                        type="button"
                        className="hl-text-button"
                        onClick={() => {
                          drafts.remove(pick.id);
                          setRemoved(pick);
                          setNotice("Older draft removed. You can undo this removal.");
                        }}
                      >
                        Remove older draft
                      </button>
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </>
        ) : matching.length ? (
          (Object.keys(GROUP_LABELS) as HighlightGroup[]).map((category) => {
            const items = matching.filter(
              (insight) =>
                collection.definitions.find((entry) => entry.id === insight.definitionId)?.group === category,
            );
            if (!items.length) return null;
            return (
              <section className="hl-category-section" key={category} aria-labelledby={`${id}-${category}`}>
                <h3 id={`${id}-${category}`} className="hl-category-title">
                  {GROUP_LABELS[category]}
                </h3>
                <div className="hl-card-grid">
                  {items.map((insight) => {
                    const definition = collection.definitions.find(
                      (entry) => entry.id === insight.definitionId,
                    );
                    return definition ? (
                      <HighlightCard
                        key={definition.id}
                        insight={insight}
                        definition={definition}
                        collection={collection}
                        onInspect={openDetail}
                        onPick={openPick}
                      />
                    ) : null;
                  })}
                </div>
              </section>
            );
          })
        ) : (
          <div className="hl-empty-state">
            <Search size={26} strokeWidth={1.25} aria-hidden />
            <h3>No highlights in this view</h3>
            <p>Try a different category or search. Player and team filters are above the collection.</p>
            <button type="button" className="hl-button hl-button-quiet" onClick={reset}>
              Reset collection filters
            </button>
          </div>
        )}
      </section>
      <footer className="hl-page-footer">
        <span>Every highlight has a source. Every favourite has a person.</span>
        <span>
          {collection.example
            ? "Example collection · no analysis has been run"
            : "Observed results are separate from reviewed evidence"}
        </span>
      </footer>
      {selected && selectedDefinition && (
        <HighlightDetails
          collection={collection}
          insight={selected}
          definition={selectedDefinition}
          personalPicks={drafts.picks.filter(matchesPickScope)}
          onClose={() => setSelected(null)}
          onPick={openPick}
          restoreFocus={returnFocus.current}
        />
      )}
      {pickKind && (
        <PersonalPickDialog
          key={`${collection.id}-${pickNonce}`}
          collection={collection}
          initialKind={pickKind}
          initialEvidence={pickEvidence}
          restoreFocus={returnFocus.current}
          open
          onOpenChange={(open) => {
            if (!open) setPickKind(null);
          }}
          onSave={(input) => {
            const issue = drafts.add(input);
            if (!issue) {
              setRemoved(null);
              setNotice(
                "Moment kept as a private draft. Find it in Your picks; unspecified players appear under Everyone.",
              );
            }
            return issue;
          }}
        />
      )}
    </>
  );
}
