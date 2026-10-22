import type { MatchSummary } from "./types";

export function processingPercent(frame: number, total: number): number | null {
  return total > 0 ? Math.round(Math.min(1, Math.max(0, frame / total)) * 100) : null;
}

export function filterMatches(matches: MatchSummary[], search: string, status: string): MatchSummary[] {
  const needle = search.trim().toLocaleLowerCase();
  return matches.filter(
    ({ session }) =>
      (status === "all" || session.status === status) &&
      (!needle ||
        [session.title, ...session.players.map((player) => player.name ?? "")].some((text) =>
          text.toLocaleLowerCase().includes(needle),
        )),
  );
}

export function dateLabel(date: string): string {
  const value = new Date(date);
  return Number.isFinite(value.getTime())
    ? value.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })
    : "Date unavailable";
}

export function strokeLabel(stroke: string): string {
  return stroke.replaceAll("_", " ").replace(/^./, (letter) => letter.toUpperCase());
}
