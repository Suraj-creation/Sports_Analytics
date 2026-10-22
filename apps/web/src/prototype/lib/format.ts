import { FPS } from "../data/fixtures";

/** m:ss for clips. Never bare seconds — a player reads a clip as a duration (08 §5). */
export function clock(frames: number): string {
  const total = Math.max(0, Math.round(frames / FPS));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function seconds(s: number): string {
  const m = Math.floor(s / 60);
  const r = Math.round(s % 60);
  return `${m}:${String(r).padStart(2, "0")}`;
}

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

/** "Thursday 15 October" — words, never 15/10/26, which means two things worldwide. */
export function longDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return `${DAYS[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
}

export function shortDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return `${d.getDate()} ${MONTHS[d.getMonth()]?.slice(0, 3)}`;
}

/** "3 days ago" against the fixture set's "today". */
const TODAY = new Date("2026-10-22T12:00:00");

export function relativeDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  const days = Math.round((TODAY.getTime() - d.getTime()) / 86_400_000);
  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 14) return "Last week";
  return `${Math.floor(days / 7)} weeks ago`;
}

/**
 * Rates are `n of m`, with the percentage secondary or absent (08 §5).
 * A bare percentage hides its denominator, which is the whole problem.
 */
export function nOfM(n: number, m: number, noun: string): string {
  return `${n} of ${m} ${noun}`;
}

/** Counts carry their unit noun. */
export function count(n: number, singular: string, plural = `${singular}s`): string {
  return `${n} ${n === 1 ? singular : plural}`;
}

/** "about 12 minutes" — estimates are prefixed and rounded to the data's real precision. */
export function approx(n: number, unit: string): string {
  return `about ${Math.round(n)} ${unit}`;
}

/** Missing is an em dash with a reason, never a zero (08 §5). */
export const MISSING = "—";

export function pct(n: number, m: number): number {
  return m === 0 ? 0 : n / m;
}
