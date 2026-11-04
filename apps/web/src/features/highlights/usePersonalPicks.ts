import { useEffect, useState } from "react";
import type { HighlightCollection, PersonalPick, PickKind } from "./types";

const kinds: PickKind[] = ["favourite", "smile", "save", "partnership"];
interface DraftState {
  key: string;
  rows: PersonalPick[];
  issue: string | null;
  writable: boolean;
}

function validPick(value: unknown): value is PersonalPick {
  if (!value || typeof value !== "object") return false;
  const pick = value as Partial<PersonalPick>;
  return (
    pick.version === 1 &&
    typeof pick.id === "string" &&
    pick.id.length < 200 &&
    (pick.namespace === "example" || pick.namespace === "recording") &&
    typeof pick.sessionId === "string" &&
    pick.sessionId.length <= 256 &&
    typeof pick.sourceKey === "string" &&
    pick.sourceKey.length <= 1024 &&
    typeof pick.revision === "number" &&
    Number.isInteger(pick.revision) &&
    pick.revision >= 0 &&
    kinds.includes(pick.kind as PickKind) &&
    (pick.selectorId === null || typeof pick.selectorId === "string") &&
    (pick.rallyId === null || typeof pick.rallyId === "string") &&
    typeof pick.start === "number" &&
    Number.isInteger(pick.start) &&
    pick.start >= 0 &&
    typeof pick.end === "number" &&
    Number.isInteger(pick.end) &&
    pick.end >= pick.start &&
    typeof pick.note === "string" &&
    pick.note.length <= 1000 &&
    pick.privacy === "private" &&
    typeof pick.createdAt === "string" &&
    Number.isFinite(Date.parse(pick.createdAt))
  );
}

function readDrafts(key: string): DraftState {
  if (!key) return { key, rows: [], issue: null, writable: false };
  try {
    const saved = localStorage.getItem(key);
    if (!saved) return { key, rows: [], issue: null, writable: true };
    if (saved.length > 1_000_000)
      return {
        key,
        rows: [],
        issue:
          "The existing draft file is too large to read safely. It is left untouched; new picks will last for this visit only.",
        writable: false,
      };
    const data: unknown = JSON.parse(saved);
    if (
      !data ||
      typeof data !== "object" ||
      !("version" in data) ||
      data.version !== 1 ||
      !("picks" in data) ||
      !Array.isArray(data.picks) ||
      data.picks.length > 200 ||
      !data.picks.every(validPick)
    ) {
      return {
        key,
        rows: [],
        issue:
          "Existing drafts could not be read. They have been left untouched; new picks will last for this visit only.",
        writable: false,
      };
    }
    return { key, rows: data.picks, issue: null, writable: true };
  } catch {
    return {
      key,
      rows: [],
      issue: "Device storage is unavailable. Picks will last for this visit only.",
      writable: false,
    };
  }
}

export function usePersonalPicks(collection: HighlightCollection | null) {
  const key = collection
    ? `rally-highlight-picks-v1:${collection.example ? "example" : "recording"}:${collection.id}`
    : "";
  const [state, setState] = useState<DraftState>(() => readDrafts(key));
  useEffect(() => {
    setState(readDrafts(key));
    const onStorage = (event: StorageEvent) => {
      if (event.key === key || event.key === null) setState(readDrafts(key));
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [key]);
  const rows = state.key === key ? state.rows : [];
  const picks = collection
    ? rows.filter(
        (pick) =>
          pick.sessionId === collection.id &&
          pick.sourceKey === collection.sourceKey &&
          pick.revision === collection.revision &&
          pick.namespace === (collection.example ? "example" : "recording") &&
          (!collection.media || pick.end < collection.media.n_frames),
      )
    : [];

  function persist(next: PersonalPick[]) {
    let issue = state.issue;
    let writable = state.writable;
    if (writable) {
      try {
        localStorage.setItem(key, JSON.stringify({ version: 1, picks: next }));
      } catch {
        issue = "Device storage could not save this change. It is kept for this visit only.";
        writable = false;
      }
    }
    setState({ key, rows: next, issue, writable });
  }

  function add(input: Pick<PersonalPick, "kind" | "selectorId" | "rallyId" | "start" | "end" | "note">) {
    if (!collection || state.key !== key) return "This session is still opening. Try again.";
    if (rows.length >= 200)
      return "This session has reached the 200-draft limit. Remove a draft before adding another.";
    if (
      !Number.isInteger(input.start) ||
      !Number.isInteger(input.end) ||
      input.start < 0 ||
      input.end < input.start ||
      (collection.media && input.end >= collection.media.n_frames)
    )
      return "Choose a valid interval inside this recording.";
    if (
      !collection.media &&
      !collection.rallies.some(
        (rally) => rally.id === input.rallyId && rally.start === input.start && rally.end === input.end,
      )
    )
      return "Choose an existing rally interval; this recording's full media range is unknown.";
    if (input.selectorId && !collection.participants.some((person) => person.id === input.selectorId))
      return "Choose a participant in this session, or leave the player unknown.";
    if (input.kind === "partnership" && collection.format !== "doubles")
      return "A partnership memory requires a confirmed doubles session.";
    const pick: PersonalPick = {
      ...input,
      note: input.note.trim().slice(0, 1000),
      version: 1,
      id: crypto.randomUUID(),
      namespace: collection.example ? "example" : "recording",
      sessionId: collection.id,
      sourceKey: collection.sourceKey,
      revision: collection.revision,
      privacy: "private",
      createdAt: new Date().toISOString(),
    };
    persist([...rows, pick]);
    return null;
  }

  return {
    picks,
    archivedPicks: rows.filter((pick) => !picks.includes(pick)),
    staleCount: rows.length - picks.length,
    issue: state.key === key ? state.issue : null,
    add,
    remove: (id: string) => persist(rows.filter((pick) => pick.id !== id)),
    restore: (pick: PersonalPick) => {
      if (!collection || pick.sessionId !== collection.id || rows.length >= 200)
        return "This draft could not be restored in the current session.";
      if (!rows.some((row) => row.id === pick.id)) persist([...rows, pick]);
      return null;
    },
  };
}
