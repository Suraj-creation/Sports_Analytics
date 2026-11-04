import * as Dialog from "@radix-ui/react-dialog";
import { LockKeyhole, X } from "lucide-react";
import { useId, useState } from "react";
import type { HighlightCollection, HighlightEvidence, PersonalPick, PickKind } from "./types";
import { frameLabel, PICK_LABELS } from "./types";

export function PersonalPickDialog({
  collection,
  initialKind,
  initialEvidence,
  open,
  onOpenChange,
  onSave,
  restoreFocus,
}: {
  collection: HighlightCollection;
  initialKind: PickKind;
  initialEvidence?: HighlightEvidence;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (
    input: Pick<PersonalPick, "kind" | "selectorId" | "rallyId" | "start" | "end" | "note">,
  ) => string | null;
  restoreFocus: HTMLElement | null;
}) {
  const id = useId();
  const [kind, setKind] = useState(initialKind);
  const initialRally = collection.rallies.find((row) => row.id === initialEvidence?.id);
  const [rallyId, setRally] = useState(
    initialRally?.id ?? (initialEvidence ? "custom" : (collection.rallies[0]?.id ?? "custom")),
  );
  const [selectorId, setSelector] = useState("");
  const [start, setStart] = useState(String(initialEvidence?.start ?? 0));
  const [end, setEnd] = useState(String(initialEvidence?.end ?? 0));
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const rally = collection.rallies.find((row) => row.id === rallyId);
  const from = rally?.start ?? Number(start);
  const through = rally?.end ?? Number(end);
  const canSelect = Boolean(collection.media?.n_frames || collection.rallies.length);
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="hl-overlay" />
        <Dialog.Content
          className="hl-pick-dialog"
          aria-describedby={`${id}-description`}
          onCloseAutoFocus={(event) => {
            event.preventDefault();
            if (restoreFocus?.isConnected) restoreFocus.focus({ preventScroll: true });
          }}
        >
          <div className="hl-dialog-heading">
            <Dialog.Title>Keep a moment</Dialog.Title>
            <Dialog.Close className="hl-icon-button" aria-label="Close moment form">
              <X size={20} aria-hidden />
            </Dialog.Close>
          </div>
          <Dialog.Description id={`${id}-description`} className="hl-muted">
            Your reason is enough. This is a private draft on this device
            {collection.example ? ", using example data" : ""}.
          </Dialog.Description>
          <form
            className="hl-pick-form"
            onSubmit={(event) => {
              event.preventDefault();
              if (!canSelect) return;
              const issue = onSave({
                kind,
                selectorId: selectorId || null,
                rallyId: rally?.id ?? null,
                start: from,
                end: through,
                note,
              });
              if (issue) setError(issue);
              else onOpenChange(false);
            }}
          >
            <label htmlFor={`${id}-kind`}>What are you keeping?</label>
            <select
              id={`${id}-kind`}
              value={kind}
              onChange={(event) => setKind(event.target.value as PickKind)}
            >
              {(Object.entries(PICK_LABELS) as [PickKind, string][])
                .filter(([value]) => value !== "partnership" || collection.format === "doubles")
                .map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
            </select>
            <label htmlFor={`${id}-rally`}>Choose the moment</label>
            <select id={`${id}-rally`} value={rallyId} onChange={(event) => setRally(event.target.value)}>
              {collection.rallies.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.label} · {frameLabel(row.start, collection.media)}
                  {row.shotCount !== null ? ` · ${row.shotCount} shots` : ""}
                </option>
              ))}
              <option value="custom">Choose a custom interval</option>
            </select>
            {!rally && (
              <div className="hl-range-inputs">
                <label htmlFor={`${id}-start`}>
                  Start frame
                  <input
                    id={`${id}-start`}
                    type="number"
                    min={0}
                    step={1}
                    max={collection.media ? collection.media.n_frames - 1 : undefined}
                    required
                    value={start}
                    onChange={(event) => setStart(event.target.value)}
                  />
                </label>
                <label htmlFor={`${id}-end`}>
                  End frame
                  <input
                    id={`${id}-end`}
                    type="number"
                    min={Math.max(0, Number(start))}
                    step={1}
                    max={collection.media ? collection.media.n_frames - 1 : undefined}
                    required
                    value={end}
                    onChange={(event) => setEnd(event.target.value)}
                  />
                </label>
              </div>
            )}
            <p className="hl-caption">
              {Number.isFinite(from) && Number.isFinite(through)
                ? `${frameLabel(from, collection.media)}–${frameLabel(through, collection.media)} · canonical video frames`
                : "Enter a valid interval."}
            </p>
            <label htmlFor={`${id}-person`}>Who picked this?</label>
            <select
              id={`${id}-person`}
              value={selectorId}
              onChange={(event) => setSelector(event.target.value)}
            >
              <option value="">Player not specified</option>
              {collection.participants.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.name}
                </option>
              ))}
            </select>
            <label htmlFor={`${id}-note`}>
              Why this one? <span className="hl-muted">Optional</span>
            </label>
            <textarea
              id={`${id}-note`}
              rows={3}
              maxLength={1000}
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Something you'd like to remember…"
            />
            <p className="hl-private">
              <LockKeyhole size={15} aria-hidden /> Private · saved on this device · no sharing
            </p>
            {!canSelect && (
              <p className="hl-form-error">
                A recording with a known interval is needed before you can keep a clip.
              </p>
            )}
            {error && (
              <p className="hl-form-error" role="alert">
                {error}
              </p>
            )}
            <div className="hl-form-actions">
              <Dialog.Close type="button" className="hl-button hl-button-quiet">
                Cancel
              </Dialog.Close>
              <button type="submit" className="hl-button hl-button-primary" disabled={!canSelect}>
                Keep this moment
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
