import { ArrowRight, Play, Users } from "lucide-react";
import { journey, matches, people, readyMatches, records, trends, youIn } from "../data/fixtures";
import type { Match } from "../data/types";
import { longDate, relativeDate } from "../lib/format";
import { Link } from "../nav";
import { RoleGlyph, StatTile, TrendLine } from "../ui/analytics";
import { Button, Card } from "../ui/primitives";
import { Page } from "../ui/shell";
import { MatchStatusChip } from "../ui/states";

/* ─────────────────────────────────────────────────────────────────────────────
   Home.

   One job: get you to the thing worth looking at. The latest match leads with its
   real numbers — not a teaser — because the analytics are the product, and a player
   who can see them from here has a reason to open the match.
   ───────────────────────────────────────────────────────────────────────────── */

export function HomeScreen() {
  const latest = readyMatches[0] as Match | undefined;
  const analysing = matches.find((m) => m.status === "analysing");
  const me = latest ? youIn(latest) : undefined;
  const st = latest && me ? latest.stats[me.id] : undefined;
  const hero = latest?.highlights[0];
  const weekMatches = readyMatches.slice(0, 3);
  const weekDistance = weekMatches.reduce((a, m) => a + (m.stats[youIn(m).id]?.distanceM ?? 0), 0);
  const weekSteps = weekMatches.reduce((a, m) => a + (m.stats[youIn(m).id]?.steps ?? 0), 0);
  const weekRallies = weekMatches.reduce((a, m) => a + m.rallies.filter((r) => r.official).length, 0);
  const weekMinutes = weekMatches.reduce((a, m) => a + m.activePlayS / 60, 0);

  return (
    <Page title="Good to see you" lead="Alex · Smash Point Arena">
      <div className="flex flex-col gap-6">
        {analysing && (
          <Link
            to="/matches/$matchId"
            params={{ matchId: analysing.id }}
            search={{ tab: "overview" }}
            className="flex items-center justify-between gap-4 rounded-[14px] border border-edge bg-surface px-4 py-3 hover:border-edge-strong"
          >
            <div className="min-w-0">
              <p className="truncate font-[600] text-ink">{analysing.title}</p>
              <p className="text-sm text-muted">We're still watching this one.</p>
            </div>
            <MatchStatusChip status="analysing" progress={analysing.progress} />
          </Link>
        )}

        {latest && me && st && (
          <Card className="flex flex-col gap-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-faint">
                  {relativeDate(latest.date)} · {latest.court} · {latest.discipline}
                </p>
                <h2 className="mt-1 text-2xl font-[700] text-ink">{latest.title}</h2>
                <p className="mt-1 text-sm text-muted">
                  {latest.sides.A.label} vs {latest.sides.B.label} ·{" "}
                  {latest.games.map(([a, b]) => `${a}–${b}`).join(", ")}
                </p>
              </div>
              <Link to="/matches/$matchId" params={{ matchId: latest.id }} search={{ tab: "overview" }}>
                <Button variant="primary">
                  Open the match
                  <ArrowRight className="size-4" aria-hidden />
                </Button>
              </Link>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatTile
                hero
                value={Math.max(...latest.rallies.filter((r) => r.official).map((r) => r.shots.length))}
                unit="shots"
                label="Longest rally"
              />
              <StatTile
                value={st.shotsPlayed}
                unit="shots"
                label="You played"
                sub={`${st.repertoire} shot types`}
              />
              <StatTile
                value={st.distanceM}
                unit="m"
                label="You covered"
                sub={`${st.steps.toLocaleString()} steps`}
              />
              <StatTile
                value={st.winners}
                unit="winners"
                label="Rallies you finished"
                sub={`${st.defensiveSaves} defensive saves`}
              />
            </div>

            {hero && (
              <Link
                to="/matches/$matchId"
                params={{ matchId: latest.id }}
                search={{ tab: "moments", f: hero.frames[0] }}
                className="flex items-center gap-4 rounded-[10px] border border-edge bg-surface-raised px-4 py-3 hover:border-edge-strong"
              >
                <span
                  aria-hidden
                  className="flex size-11 shrink-0 items-center justify-center rounded-full bg-primary text-on-primary"
                >
                  <Play className="size-5 translate-x-px fill-current" />
                </span>
                <span className="min-w-0">
                  <span className="block font-[600] text-ink">{hero.title}</span>
                  <span className="block truncate text-sm text-muted">{hero.why}</span>
                </span>
              </Link>
            )}
          </Card>
        )}

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
          <Card className="flex flex-col gap-4">
            <h2 className="text-lg font-[650] text-ink">Your last three matches</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Figure value={weekRallies} label="rallies" />
              <Figure value={Math.round(weekMinutes)} label="minutes in play" />
              <Figure value={`${(weekDistance / 1000).toFixed(1)}`} label="km covered" />
              <Figure value={weekSteps.toLocaleString()} label="steps" />
            </div>
            <div className="grid gap-5 md:grid-cols-2">
              {trends.slice(0, 2).map((t) => (
                <div key={t.id} className="flex flex-col gap-1">
                  <p className="text-sm font-[600] text-ink">{t.label}</p>
                  <TrendLine points={t.points} unit={t.unit} label={t.label} />
                </div>
              ))}
            </div>
            <Link to="/progress" search={{ tab: "overview" }} className="w-fit">
              <Button variant="ghost">
                All your progress
                <ArrowRight className="size-4" aria-hidden />
              </Button>
            </Link>
          </Card>

          <div className="flex flex-col gap-5">
            <Card className="flex flex-col gap-3">
              <h2 className="text-lg font-[650] text-ink">Best so far</h2>
              <ul className="flex flex-col gap-2.5">
                {records.slice(0, 4).map((r) => (
                  <li key={r.id} className="flex items-baseline justify-between gap-3">
                    <span className="text-sm text-muted">{r.label}</span>
                    <span className="tabular shrink-0 text-sm font-[600] text-ink">
                      {r.value.toLocaleString()} {r.unit}
                    </span>
                  </li>
                ))}
              </ul>
              <Link to="/progress" search={{ tab: "records" }} className="w-fit">
                <Button size="sm" variant="ghost">
                  See all records
                </Button>
              </Link>
            </Card>

            <Card className="flex flex-col gap-3">
              <h2 className="flex items-center gap-2 text-lg font-[650] text-ink">
                <Users className="size-4 text-muted" aria-hidden />
                People you play with
              </h2>
              <ul className="flex flex-col gap-2.5">
                {people.slice(0, 4).map((p) => (
                  <li key={p.id} className="flex items-center justify-between gap-3 text-sm">
                    <span className="flex items-center gap-2 text-ink">
                      <RoleGlyph
                        player={{
                          id: p.id,
                          name: p.name,
                          short: p.name,
                          side: "A",
                          end: "near",
                          isYou: false,
                          colour: p.role === "partner" ? "partner" : "opponent-1",
                        }}
                      />
                      {p.name}
                    </span>
                    <span className="text-muted">
                      {p.role === "partner" ? "partner" : "opponent"} · {p.matches}
                    </span>
                  </li>
                ))}
              </ul>
              <Link to="/people" className="w-fit">
                <Button size="sm" variant="ghost">
                  Everyone
                </Button>
              </Link>
            </Card>
          </div>
        </div>

        <Card className="flex flex-col gap-3">
          <h2 className="text-lg font-[650] text-ink">Lately</h2>
          <ol className="flex flex-col gap-3">
            {journey.slice(0, 4).map((j) => (
              <li key={j.id} className="flex gap-3">
                <span className="w-24 shrink-0 text-xs text-faint">{longDate(j.date).slice(0, 12)}</span>
                <span className="min-w-0">
                  <span className="block text-sm font-[600] text-ink">{j.title}</span>
                  <span className="block text-sm text-muted">{j.detail}</span>
                </span>
              </li>
            ))}
          </ol>
        </Card>
      </div>
    </Page>
  );
}

function Figure({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="rounded-[10px] bg-surface-raised px-3 py-2.5">
      <p className="numerals text-2xl leading-none text-ink">{value}</p>
      <p className="mt-1 text-xs text-muted">{label}</p>
    </div>
  );
}
