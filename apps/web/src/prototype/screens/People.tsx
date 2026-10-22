import { people, readyMatches, youIn } from "../data/fixtures";
import type { Match, PlayerId } from "../data/types";
import { relativeDate } from "../lib/format";
import { Link } from "../nav";
import { Panel, RoleGlyph, StatTile } from "../ui/analytics";
import { Card } from "../ui/primitives";
import { Page } from "../ui/shell";

/* ─────────────────────────────────────────────────────────────────────────────
   People.

   Doubles makes this a real surface rather than a nicety: a player wants to know how
   a pair works, not only how they played. Partners get chemistry; opponents get a
   neutral record of what happened — never a ranking, never a verdict.
   ───────────────────────────────────────────────────────────────────────────── */

export function PeopleScreen() {
  const partners = people.filter((p) => p.role === "partner");
  const opponents = people.filter((p) => p.role === "opponent");

  return (
    <Page
      title="People you play with"
      lead="Partners and opponents across your analysed matches. Nobody is ranked against anybody."
    >
      <div className="flex flex-col gap-8">
        <section className="flex flex-col gap-4">
          <h2 className="text-xl font-[650] text-ink">Partners</h2>
          {partners.length === 0 ? (
            <p className="text-sm text-muted">No doubles matches analysed yet.</p>
          ) : (
            <div className="grid gap-5 lg:grid-cols-2">
              {partners.map((row) => (
                <PartnerCard key={row.id} id={row.id} name={row.name} />
              ))}
            </div>
          )}
        </section>

        <section className="flex flex-col gap-4">
          <h2 className="text-xl font-[650] text-ink">Opponents</h2>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {opponents.map((row) => {
              const played = readyMatches.filter((m) => m.players.some((p) => p.id === row.id));
              const rallies = played.reduce((a, m) => a + m.rallies.filter((r) => r.official).length, 0);
              return (
                <Card as="li" key={row.id} className="flex flex-col gap-2">
                  <span className="flex items-center gap-2 text-base font-[650] text-ink">
                    <RoleGlyph
                      player={{
                        id: row.id,
                        name: row.name,
                        short: row.name,
                        side: "B",
                        end: "far",
                        isYou: false,
                        colour: "opponent-1",
                      }}
                    />
                    {row.name}
                  </span>
                  <p className="text-sm text-muted">
                    {played.length} {played.length === 1 ? "match" : "matches"} · {rallies} rallies · last
                    played {relativeDate(row.lastPlayed)}
                  </p>
                  <ul className="flex flex-col gap-1 text-sm text-muted">
                    {played.map((m) => (
                      <li key={m.id}>
                        <Link
                          to="/matches/$matchId"
                          params={{ matchId: m.id }}
                          search={{ tab: "h2h" }}
                          className="hover:text-ink hover:underline"
                        >
                          {m.title} — {m.games.map(([a, b]) => `${a}–${b}`).join(", ")}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </Card>
              );
            })}
          </ul>
        </section>
      </div>
    </Page>
  );
}

function PartnerCard({ id, name }: { id: PlayerId; name: string }) {
  const played = readyMatches.filter((m) => m.discipline === "doubles" && m.players.some((p) => p.id === id));
  const match = played[0] as Match | undefined;
  if (!match) return null;
  const me = youIn(match);
  const pair = match.pairs?.[me.side];
  const partner = match.players.find((p) => p.id === id);
  if (!pair || !partner) return null;

  const mine = pair.frontRear[me.id] ?? { front: 0, rear: 0 };
  const theirs = pair.frontRear[id] ?? { front: 0, rear: 0 };
  const myFront = mine.front / Math.max(1, mine.front + mine.rear);
  const theirFront = theirs.front / Math.max(1, theirs.front + theirs.rear);

  return (
    <Panel
      question={`You and ${name}`}
      hint={`${played.length} ${played.length === 1 ? "match" : "matches"} together · ${pair.pointsWon} points won as a pair`}
      insights={[
        {
          text: `You both hit the shuttle in ${pair.bothContributed} rallies, and the longest you built together ran to ${pair.longestSharedRally} shots.`,
          tone: "strength",
        },
        {
          text:
            Math.abs(myFront - theirFront) > 0.18
              ? `You covered the ${myFront > theirFront ? "front" : "rear"} more; ${name} took the other. That is a shape, not a mistake.`
              : `You split front and rear court fairly evenly with ${name}.`,
          tone: "neutral",
        },
      ]}
    >
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-3 gap-3">
          <StatTile value={pair.bothContributed} unit="rallies" label="Both of you hit" />
          <StatTile value={pair.rescues} unit="times" label="Covered each other" />
          <StatTile value={pair.attackCombos} unit="combos" label="Attack then net" />
        </div>
        <ul className="flex flex-col gap-2 text-sm">
          {played.map((m) => (
            <li key={m.id}>
              <Link
                to="/matches/$matchId"
                params={{ matchId: m.id }}
                search={{ tab: "pair" }}
                className="text-primary underline underline-offset-2"
              >
                {m.title} — open your pair analysis
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </Panel>
  );
}
