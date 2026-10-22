import { ArrowRight, Clapperboard, ShieldCheck, TrendingUp, Users } from "lucide-react";
import { readyMatches, VENUE, youIn } from "../data/fixtures";
import { Link } from "../nav";
import { StatTile } from "../ui/analytics";
import { Logo } from "../ui/art";
import { Button, Card } from "../ui/primitives";

/* ─────────────────────────────────────────────────────────────────────────────
   Landing.

   The venue films the court; you do not upload anything. The page leads with the
   analysis rather than a promise about it, because the analysis is the product and
   the audience can read it.
   ───────────────────────────────────────────────────────────────────────────── */

export function WelcomeScreen() {
  const sample = readyMatches.find((m) => m.discipline === "doubles") ?? readyMatches[0];
  const st = sample ? sample.stats[youIn(sample).id] : undefined;

  return (
    <div className="min-h-full bg-canvas">
      <header className="mx-auto flex max-w-[1120px] items-center justify-between px-4 py-5 md:px-6">
        <span className="flex items-center gap-2.5">
          <Logo className="size-8" />
          <span className="text-lg font-[700] tracking-tight text-ink">Rally</span>
        </span>
        <Link to="/">
          <Button variant="ghost">Sign in</Button>
        </Link>
      </header>

      <section className="mx-auto max-w-[1120px] px-4 pb-14 pt-6 md:px-6 md:pt-10">
        <p className="condensed text-xs uppercase tracking-[0.12em] text-muted">{VENUE} · Courts 1–6</p>
        <h1 className="mt-4 max-w-[18ch] text-[length:var(--text-3xl)] font-[700] leading-[1.1] tracking-tight text-ink md:text-[3.25rem]">
          The cameras were already running.
        </h1>
        <p className="measure mt-6 text-lg text-muted">
          Every match on these courts is filmed and analysed. Rallies, shots, court position, distance
          covered, who built which point — singles and doubles. You do not upload anything; your match is
          waiting when you finish playing.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/">
            <Button variant="primary" size="lg">
              Open your matches
              <ArrowRight className="size-4" aria-hidden />
            </Button>
          </Link>
          {sample && (
            <Link to="/matches/$matchId" params={{ matchId: sample.id }} search={{ tab: "overview" }}>
              <Button variant="secondary" size="lg">
                See a real analysis
              </Button>
            </Link>
          )}
        </div>
        <p className="mt-4 text-sm text-faint">
          Private by default. Nothing is shared unless you choose to share it. Adults only, for now.
        </p>
      </section>

      {/* Show the depth rather than describe it. */}
      {sample && st && (
        <section className="border-y border-edge bg-surface/40">
          <div className="mx-auto max-w-[1120px] px-4 py-12 md:px-6">
            <h2 className="text-xl font-[650] text-ink">What one match gives you</h2>
            <p className="measure mt-1 text-muted">
              From {sample.title.toLowerCase()} — {sample.rallies.filter((r) => r.official).length} rallies,
              all of it traceable back to the rally it came from.
            </p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatTile
                value={Math.max(...sample.rallies.filter((r) => r.official).map((r) => r.shots.length))}
                unit="shots"
                label="Longest rally"
              />
              <StatTile
                value={st.shotsPlayed}
                unit="shots"
                label="You played"
                sub={`${st.repertoire} types`}
              />
              <StatTile
                value={st.distanceM}
                unit="m"
                label="You covered"
                sub={`${st.steps.toLocaleString()} steps`}
              />
              <StatTile value={sample.highlights.length} unit="moments" label="Picked out for you" />
            </div>
          </div>
        </section>
      )}

      <section className="mx-auto max-w-[1120px] px-4 py-14 md:px-6">
        <div className="grid gap-5 md:grid-cols-3">
          {[
            {
              icon: Clapperboard,
              title: "Ten views of one match",
              body: "Moments, rallies shot by shot, shot mix and effectiveness, tactics, five court maps, movement, head to head, your pair, and a chat that cites its evidence.",
            },
            {
              icon: Users,
              title: "Singles and doubles",
              body: "Four players tracked, each with their own numbers — plus the pair: who covered whom, who took the front, which rallies you built together.",
            },
            {
              icon: TrendingUp,
              title: "Against your own history",
              body: "Trends, personal bests and a shot repertoire that grows. Never a ranking against anybody else.",
            },
          ].map((f) => (
            <Card key={f.title} className="flex flex-col gap-2">
              <f.icon className="size-5 text-primary" aria-hidden />
              <h3 className="text-lg font-[650] text-ink">{f.title}</h3>
              <p className="text-muted">{f.body}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="border-t border-edge bg-surface/40">
        <div className="mx-auto max-w-[1120px] px-4 py-14 md:px-6">
          <h2 className="flex items-center gap-2 text-xl font-[650] text-ink">
            <ShieldCheck className="size-5 text-muted" aria-hidden />
            Where it stops being reliable
          </h2>
          <p className="measure mt-1 text-muted">
            You would find this out eventually. Better now — knowing where a number gets soft is what makes
            the rest of them worth reading.
          </p>
          <ul className="measure mt-5 flex list-disc flex-col gap-2.5 pl-5 text-muted">
            <li>
              <strong className="text-ink">Shot names are a guess.</strong> The classifier is rule-based and
              has not been validated on these cameras. Counts are solid; names are candidates.
            </li>
            <li>
              <strong className="text-ink">We do not track the shuttle's flight.</strong> "Where your shots
              went" is where the other player met them, which is close but not the same.
            </li>
            <li>
              <strong className="text-ink">Distance carries jitter.</strong> Useful for comparing within a
              match or against your own history; not a fitness measurement.
            </li>
            <li>
              <strong className="text-ink">Rallies we could not follow are left out</strong> of every figure
              rather than estimated, and each match says how many that was.
            </li>
          </ul>
          <div className="mt-7">
            <Link to="/help">
              <Button variant="secondary">Read how each number is measured</Button>
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-edge">
        <div className="mx-auto flex max-w-[1120px] flex-wrap items-center gap-x-6 gap-y-2 px-4 py-8 text-sm text-muted md:px-6">
          <span className="flex items-center gap-2">
            <Logo className="size-5" /> Rally
          </span>
          <Link to="/settings" search={{ s: "privacy" }} className="hover:text-ink hover:underline">
            Privacy
          </Link>
          <Link to="/help" className="hover:text-ink hover:underline">
            Help
          </Link>
          <span className="text-faint">A design prototype. Nothing here was measured.</span>
        </div>
      </footer>
    </div>
  );
}
