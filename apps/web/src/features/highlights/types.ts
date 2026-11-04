import type { MatchSummary } from "@/features/product/types";
import type { MediaInfo } from "@/lib/types";
import type { ReactNode } from "react";

export type HighlightGroup = "moments" | "patterns" | "history";
export type HighlightAvailability = "available" | "review" | "missing" | "not_applicable";
export type PickKind = "favourite" | "smile" | "save" | "partnership";

export interface HighlightDefinition {
  id: string;
  title: string;
  group: HighlightGroup;
  question: string;
  definition: string;
  requires: string[];
  pickKind?: PickKind;
}

export interface HighlightEvidence {
  id: string;
  label: string;
  start: number;
  end: number;
  shotCount: number | null;
  outcome: string | null;
  eventStatus?: string;
  evidenceBand?: string;
  modelScore?: number | null;
  scoreAvailable?: boolean;
}

export interface HighlightMetric {
  label: string;
  value: string;
  detail?: string;
}

export type HighlightVisual =
  | { kind: "diagram"; variant: string; illustrated: boolean }
  | { kind: "scores"; points: { label: string; value: string }[] }
  | {
      kind: "bars";
      rows: { label: string; value: number; max: number; display: string; detail?: string }[];
    }
  | { kind: "record"; previous: number; current: number; unit: string }
  | { kind: "invitation"; label: string };

export interface HighlightInsight {
  definitionId: string;
  headline: string;
  summary: string;
  availability: HighlightAvailability;
  origin: "example" | "observed" | "player";
  support: string;
  /** Explicit person:<id> and team:<id> namespaces keep people apart from scoring sides. */
  subjectIds: string[];
  metrics: HighlightMetric[];
  evidence: HighlightEvidence[];
  visual: HighlightVisual;
}

export interface HighlightCollection {
  id: string;
  sport: string;
  title: string;
  format: "singles" | "doubles" | "unknown";
  example: boolean;
  revision: number;
  sourceKey: string;
  media: MediaInfo | null;
  participants: { id: string; name: string; teamId: string | null }[];
  teams: { id: string; name: string }[];
  definitions: HighlightDefinition[];
  insights: HighlightInsight[];
  rallies: HighlightEvidence[];
  scope: string;
}

/** UI providers interpret existing responses; they never execute an analysis stage. */
export interface HighlightProvider {
  sport: string;
  example: (format: "singles" | "doubles") => HighlightCollection;
  fromRecording: (match: MatchSummary, snapshot: unknown, subjectId: string) => HighlightCollection;
  renderDiagram: (variant: string, format: HighlightCollection["format"]) => ReactNode;
}

export interface PersonalPick {
  version: 1;
  id: string;
  namespace: "example" | "recording";
  sessionId: string;
  sourceKey: string;
  revision: number;
  kind: PickKind;
  selectorId: string | null;
  rallyId: string | null;
  start: number;
  end: number;
  note: string;
  privacy: "private";
  createdAt: string;
}

export const PICK_LABELS: Record<PickKind, string> = {
  favourite: "Favourite rally",
  smile: "Made me smile",
  save: "My best save",
  partnership: "Partnership memory",
};

export const GROUP_LABELS: Record<HighlightGroup, string> = {
  moments: "Moments to keep",
  patterns: "The shape of your game",
  history: "A little history",
};

export function frameLabel(frame: number, media: MediaInfo | null): string {
  if (!media || media.fps_num <= 0 || media.fps_den <= 0) return `Frame ${frame.toLocaleString()}`;
  const seconds = Math.floor((frame * media.fps_den) / media.fps_num);
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours ? `${hours}:` : ""}${hours ? String(minutes).padStart(2, "0") : minutes}:${String(seconds % 60).padStart(2, "0")}`;
}
