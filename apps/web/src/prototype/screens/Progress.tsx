import { clsx } from "clsx";
import { Star } from "lucide-react";
import { useState } from "react";
import {
  comparableMatches,
  excludedMatches,
  getMatch,
  journey,
  readyMatches,
  records,
  trends,
  youIn,
} from "../data/fixtures";
import { STROKE_LABEL } from "../data/types";
import { longDate, relativeDate } from "../lib/format";
import { Link, useNavigate, useSearch } from "../nav";
import { Panel, StatTile, TrendLine } from "../ui/analytics";
import { Challenges, FocusList } from "../ui/focus";
import { Button, Card } from "../ui/primitives";
import { Page } from "../ui/shell";

/* ─────────────────────────────────────────────────────────────────────────────
   Progress.

   Compared only with your own history, and only across matches measured the same way.
   Singles and doubles are plotted with different marks because they are not the
   same kind of match and averaging them would be a lie.
   ───────────────────────────────────────────────────────────────────────────── */

const TABS = [
  { id: "overview", label: "Trends" },
  { id: "records", label: "Personal bests" },
  { id: "shots", label: "Shot repertoire" },
  { id: "focus", label: "Focus & challenges" },
  { id: "story", label: "Your story" },
] as const;

type Tab = (typeof TABS)[number]["id"];

export function ProgressScreen() {
  const { tab } = useSearch<{ tab: Tab }>({ from: "/progress" });
  const navigate = useNavigate();
  const active = tab ?? "overview";

  return (
    <Page
      title="Your progress"
      lead={`Across ${comparableMatches.length} comparable matches at Smash Point Arena. Everything here compares you with your own history.`}
    >
      <div className="flex flex-col gap-5">
        <nav
          aria-label="Progress sections"
          className="-mx-4 flex gap-1 overflow-x-auto border-b border-edge px-4 quiet-scroll sm:mx-0 sm:px-0"
        >
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              aria-current={active === t.id ? "page" : undefined}
              onClick={() => navigate({ to: ".", search: { tab: t.id } })}
              className={clsx(
                "-mb-px shrink-0 border-b-2 px-3.5 py-3 text-sm transition-colors",
                active === t.id
                  ? "border-ink font-[600] text-ink"
                  : "border-transparent text-muted hover:text-ink",
              )}
            >
              {t.label}
            </button>
          ))}
        </nav>

        {active === "overview" && <Trends />}
        {active === "records" && <Records />}
        {active === "shots" && <Repertoire />}
        {active === "focus" && <FocusTab />}
        {active === "story" && <Story />}
      </div>
    </Page>
  );
}

function Trends() {
  const totalDistance = comparableMatches.reduce((a, m) => a + (m.stats[youIn(m).id]?.distanceM ?? 0), 0);
  const totalSteps = comparableMatches.reduce((a, m) => a + (m.stats[youIn(m).id]?.steps ?? 0), 0);
  const totalRallies = comparableMatches.reduce((a, m) => a + m.rallies.filter((r) => r.official).length, 0);
  const totalShots = comparableMatches.reduce((a, m) => a + (m.stats[youIn(m).id]?.shotsPlayed ?? 0), 0);

  return (
    <div className="flex flex-col gap-5">
      {excludedMatches.length > 0 && (
        <div className="flex items-start gap-3 rounded-[14px] border border-edge bg-surface-raised p-4">
          <span aria-hidden className="mt-0.5 text-muted">
            ⌀
          </span>
          <div>
            <p className="text-sm font-[600] text-ink">
              {excludedMatches.length === 1 ? "One match is" : `${excludedMatches.length} matches are`} left
              out of these trends
            </p>
            <ul className="mt-1 flex flex-col gap-1 text-sm text-muted">
              {excludedMatches.map((m) => (
                <li key={m.id}>
                  <Link
                    to="/matches/$matchId"
                    params={{ matchId: m.id }}
                    search={{ tab: "overview" }}
                    className="text-primary underline underline-offset-2"
                  >
                    {m.title}
                  </Link>{" "}
                  — we followed {m.coverage.followed} of {m.coverage.total} rallies. Still worth watching; not
                  comparable with the rest.
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile value={totalRallies} unit="rallies" label="Played and counted" />
        <StatTile value={totalShots} unit="shots" label="You hit" />
        <StatTile value={(totalDistance / 1000).toFixed(1)} unit="km" label="Covered on court" />
        <StatTile value={totalSteps.toLocaleString()} unit="steps" label="Taken in play" />
      </div>
      <p className="measure text-sm text-muted">
        Singles and doubles are plotted separately. They are not the same game — a doubles rally is shorter
        and the court is shared — so averaging them together would describe neither.
      </p>
      <div className="grid gap-5 lg:grid-cols-2">
        {trends.map((t) => {
          const singles = t.points.filter((x) => x.discipline === "singles");
          const doubles = t.points.filter((x) => x.discipline === "doubles");
          return (
            <Panel
              key={t.id}
              question={t.label}
              hint={t.definition}
              basis={`${singles.length} singles and ${doubles.length} doubles matches at one venue`}
            >
              <div className="flex flex-col gap-4">
                <div>
                  <p className="mb-1 text-xs font-[600] uppercase tracking-wide text-faint">Singles</p>
                  {singles.length >= 2 ? (
                    <TrendLine points={singles} unit={t.unit} label={`${t.label}, singles`} />
                  ) : (
                    <p className="text-sm text-muted">
                      {singles.length === 1
                        ? "One singles match so far — that is the baseline, not a trend."
                        : "No singles matches yet."}
                    </p>
                  )}
                </div>
                <div className="border-t border-edge pt-3">
                  <p className="mb-1 text-xs font-[600] uppercase tracking-wide text-faint">Doubles</p>
                  {doubles.length >= 2 ? (
                    <TrendLine points={doubles} unit={t.unit} label={`${t.label}, doubles`} />
                  ) : (
                    <p className="text-sm text-muted">
                      {doubles.length === 1
                        ? "One doubles match so far — that is the baseline, not a trend."
                        : "No doubles matches yet."}
                    </p>
                  )}
                </div>
              </div>
            </Panel>
          );
        })}
      </div>
    </div>
  );
}

function Records() {
  const [open, setOpen] = useState<string | null>(null);
  return (
    <div className="flex flex-col gap-4">
      <p className="measure text-sm text-muted">
        A best only means something if you know exactly what was counted — so each one carries its definition.
      </p>
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {records.map((r) => {
          const m = getMatch(r.matchId);
          return (
            <Card as="li" key={r.id} className="flex flex-col gap-3">
              <div className="flex items-start gap-3">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-full border border-edge">
                  <Star className="size-5 text-you" aria-hidden />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-[600] text-ink">{r.label}</p>
                  <p className="flex items-baseline gap-1.5">
                    <span className="numerals text-3xl leading-tight text-ink">
                      {r.value.toLocaleString()}
                    </span>
                    <span className="text-sm text-muted">{r.unit}</span>
                  </p>
                  {r.previous !== null && (
                    <p className="text-xs text-faint">
                      Previously {r.previous.toLocaleString()} {r.unit}
                    </p>
                  )}
                </div>
              </div>
              <button
                type="button"
                onClick={() => setOpen(open === r.id ? null : r.id)}
                className="w-fit text-sm text-primary underline underline-offset-2"
              >
                {open === r.id ? "Hide what counts" : "What counts"}
              </button>
              {open === r.id && <p className="text-sm text-muted">{r.definition}</p>}
              {m && (
                <Link
                  to="/matches/$matchId"
                  params={{ matchId: m.id }}
                  search={{ tab: "overview" }}
                  className="text-sm text-muted hover:text-ink hover:underline"
                >
                  {m.title} · {relativeDate(r.date)}
                </Link>
              )}
            </Card>
          );
        })}
      </ul>
    </div>
  );
}

function Repertoire() {
  // Every stroke you have been seen to play, across every analysed match.
  const counts = new Map<string, { total: number; matches: Set<string>; first: string }>();
  for (const m of readyMatches.slice().sort((a, b) => (a.date < b.date ? -1 : 1))) {
    const st = m.stats[youIn(m).id];
    if (!st) continue;
    for (const [k, v] of Object.entries(st.strokes)) {
      const row = counts.get(k) ?? { total: 0, matches: new Set<string>(), first: m.date };
      row.total += v;
      row.matches.add(m.id);
      counts.set(k, row);
    }
  }
  const list = [...counts.entries()].sort((a, b) => b[1].total - a[1].total);
  const max = Math.max(1, ...list.map(([, v]) => v.total));

  return (
    <div className="flex flex-col gap-4">
      <Panel
        question="Which shots have you been seen to play?"
        hint="Across every analysed match. A shot appearing here means the classifier labelled it, not that you have mastered it."
      >
        <ul className="flex flex-col gap-2.5">
          {list.map(([k, v]) => (
            <li key={k} className="grid grid-cols-[130px_1fr_auto] items-center gap-3">
              <span className="text-sm text-ink">{STROKE_LABEL[k] ?? k}</span>
              <span className="h-3 rounded-sm bg-you" style={{ width: `${(v.total / max) * 100}%` }} />
              <span className="tabular text-sm text-muted">
                {v.total}
                <span className="ml-2 text-xs text-faint">
                  in {v.matches.size} {v.matches.size === 1 ? "match" : "matches"}
                </span>
              </span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

function FocusTab() {
  return (
    <div className="flex flex-col gap-6">
      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-[650] text-ink">Your focus</h2>
        <p className="measure text-sm text-muted">
          One thing at a time, chosen by you, with a ladder that does not let watching a clip count as having
          practised something.
        </p>
        <FocusList />
      </section>
      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-[650] text-ink">Optional challenges</h2>
        <p className="measure text-sm text-muted">
          Entirely optional and dismissible. Progress is computed from your matches — nothing here is awarded
          for opening a screen, and nothing is lost if you take a month off.
        </p>
        <Challenges />
      </section>
    </div>
  );
}

function Story() {
  return (
    <ol className="relative flex flex-col border-l border-edge pl-6">
      {journey.map((j) => (
        <li key={j.id} className="relative pb-7">
          <span
            aria-hidden
            className={clsx(
              "absolute -left-[29px] top-1 size-3 rounded-full border-2",
              j.kind === "record"
                ? "border-you bg-canvas"
                : j.kind === "partner"
                  ? "border-partner bg-canvas"
                  : "border-edge-strong bg-edge-strong",
            )}
          />
          <p className="text-xs text-faint">{longDate(j.date)}</p>
          <p className="mt-0.5 font-[600] text-ink">{j.title}</p>
          <p className="mt-0.5 text-sm text-muted">{j.detail}</p>
          {j.matchId && (
            <Link
              to="/matches/$matchId"
              params={{ matchId: j.matchId }}
              search={{ tab: "overview" }}
              className="mt-1 inline-block text-sm text-primary underline underline-offset-2"
            >
              Open the match
            </Link>
          )}
        </li>
      ))}
    </ol>
  );
}

export { Button };
