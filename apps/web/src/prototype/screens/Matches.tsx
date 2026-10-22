import { useState } from "react";
import { matches, youIn } from "../data/fixtures";
import { longDate, relativeDate } from "../lib/format";
import { Link } from "../nav";
import { RoleGlyph } from "../ui/analytics";
import { Card, Chip } from "../ui/primitives";
import { Page } from "../ui/shell";
import { MatchStatusChip } from "../ui/states";

/* ─────────────────────────────────────────────────────────────────────────────
   Matches.

   The list carries real numbers, not placeholders: a player should be able to decide
   which match to open from here. Processing and failed states are card states, not
   separate pages.
   ───────────────────────────────────────────────────────────────────────────── */

export function MatchesScreen() {
  const [filter, setFilter] = useState<"all" | "singles" | "doubles">("all");
  const shown = matches.filter((m) => filter === "all" || m.discipline === filter);

  return (
    <Page
      title="Your matches"
      lead={`Everything Smash Point Arena has filmed on your courts — ${matches.length} matches.`}
    >
      <div className="flex flex-col gap-5">
        <div className="flex flex-wrap gap-2">
          {(
            [
              ["all", `All ${matches.length}`],
              ["singles", `Singles ${matches.filter((m) => m.discipline === "singles").length}`],
              ["doubles", `Doubles ${matches.filter((m) => m.discipline === "doubles").length}`],
            ] as const
          ).map(([id, label]) => (
            <Chip key={id} selected={filter === id} onClick={() => setFilter(id)}>
              {label}
            </Chip>
          ))}
        </div>

        <ul className="flex flex-col gap-3">
          {shown.map((m) => {
            const me = youIn(m);
            const st = m.stats[me.id];
            const offs = m.rallies.filter((r) => r.official);
            const longest = offs.length ? Math.max(...offs.map((r) => r.shots.length)) : 0;
            const won = m.games.filter(([a, b]) => (me.side === "A" ? a > b : b > a)).length;
            const ready = m.status === "ready";
            return (
              <Card as="li" key={m.id} className="flex flex-col gap-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="mb-1.5 flex flex-wrap items-center gap-2">
                      <MatchStatusChip status={m.status} progress={m.progress} />
                      <span className="rounded-full border border-edge px-2 py-0.5 text-xs capitalize text-muted">
                        {m.discipline}
                      </span>
                      <span className="text-xs text-faint">{relativeDate(m.date)}</span>
                    </div>
                    <h2 className="text-lg font-[650] text-ink">
                      <Link
                        to="/matches/$matchId"
                        params={{ matchId: m.id }}
                        search={{ tab: "overview" }}
                        className="hover:underline"
                      >
                        {m.title}
                      </Link>
                    </h2>
                    <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-muted">
                      {m.players.map((p) => (
                        <span key={p.id} className="inline-flex items-center gap-1">
                          <RoleGlyph player={p} className="size-2" />
                          {p.short}
                        </span>
                      ))}
                      <span className="text-faint">·</span>
                      {longDate(m.date)} · {m.court}
                    </p>
                  </div>
                  {ready && (
                    <span className="tabular shrink-0 rounded-[10px] border border-edge px-3 py-1.5 text-sm text-ink">
                      {m.games.map(([a, b]) => `${a}–${b}`).join("  ")}
                      <span className="ml-2 text-xs text-muted">
                        {won} of {m.games.length} games
                      </span>
                    </span>
                  )}
                </div>

                {ready && st ? (
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
                    <Cell value={offs.length} label="rallies" />
                    <Cell value={longest} label="longest rally" />
                    <Cell value={st.shotsPlayed} label="shots you played" />
                    <Cell value={`${st.distanceM} m`} label="you covered" />
                    <Cell value={m.highlights.length} label="moments" />
                  </div>
                ) : (
                  <p className="text-sm text-muted">
                    {m.status === "failed"
                      ? "The recording stopped about four minutes in — there isn't enough footage to analyse."
                      : "Rallies, shots and moments appear as they're found."}
                  </p>
                )}
              </Card>
            );
          })}
        </ul>
      </div>
    </Page>
  );
}

function Cell({ value, label }: { value: string | number; label: string }) {
  return (
    <div className="rounded-[10px] bg-surface-raised px-3 py-2">
      <p className="numerals text-xl leading-none text-ink">{value}</p>
      <p className="mt-1 text-xs text-muted">{label}</p>
    </div>
  );
}
