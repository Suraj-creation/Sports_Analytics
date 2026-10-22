import { clsx } from "clsx";
import { Check, Compass, Play, X } from "lucide-react";
import { readyMatches, youIn } from "../data/fixtures";
import { ZONES } from "../data/types";
import { Link } from "../nav";
import { type FocusStatus, useStore } from "../store";
import { Button, Card } from "./primitives";

/* ─────────────────────────────────────────────────────────────────────────────
   Focus and challenges.

   Both are optional, both are dismissible, and neither is allowed to claim progress
   the data does not show. The status ladder comes from the Front-End Blueprint §7.11:
   reviewed → practised → seen again in play, and a step is never skipped. Watching a
   clip is not practising, and practising is not having changed.
   ───────────────────────────────────────────────────────────────────────────── */

const LADDER: { id: FocusStatus; label: string; meaning: string }[] = [
  { id: "reviewed", label: "Reviewed", meaning: "You've looked at the evidence." },
  { id: "practised", label: "Practised", meaning: "You've worked on it away from a match." },
  { id: "seen_again", label: "Seen again in play", meaning: "It showed up in a later match." },
];

export function FocusList() {
  const focus = useStore((s) => s.focus);
  const advance = useStore((s) => s.advanceFocus);
  const drop = useStore((s) => s.dropFocus);

  if (focus.length === 0) {
    return (
      <Card className="flex flex-col gap-2">
        <p className="font-[600] text-ink">No focus set</p>
        <p className="measure text-sm text-muted">
          A focus is one thing you've decided to pay attention to — you set it yourself from anything in a
          match that caught your eye. There is no suggested one, because a focus you didn't choose isn't a
          focus.
        </p>
      </Card>
    );
  }

  return (
    <ul className="flex flex-col gap-3">
      {focus.map((f) => {
        const step = LADDER.findIndex((l) => l.id === f.status);
        const atEnd = step === LADDER.length - 1;
        return (
          <Card as="li" key={f.id} className="flex flex-col gap-3">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="font-[650] text-ink">{f.title}</p>
                <p className="mt-0.5 text-sm text-muted">{f.why}</p>
              </div>
              <button
                type="button"
                onClick={() => drop(f.id)}
                aria-label="Drop this focus"
                className="shrink-0 rounded-[8px] p-1.5 text-muted hover:bg-surface-raised hover:text-ink"
              >
                <X className="size-4" aria-hidden />
              </button>
            </div>

            {/* The ladder. Each rung says what it actually means. */}
            <ol className="flex flex-col gap-1.5">
              {LADDER.map((l, i) => (
                <li key={l.id} className="flex items-start gap-2.5">
                  <span
                    aria-hidden
                    className={clsx(
                      "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border text-[10px]",
                      i <= step ? "border-you bg-you text-canvas" : "border-edge-strong text-faint",
                    )}
                  >
                    {i <= step ? <Check className="size-3" /> : i + 1}
                  </span>
                  <span className="min-w-0">
                    <span className={clsx("block text-sm", i <= step ? "font-[600] text-ink" : "text-muted")}>
                      {l.label}
                    </span>
                    <span className="block text-xs text-faint">{l.meaning}</span>
                  </span>
                </li>
              ))}
            </ol>

            <div className="flex flex-wrap gap-2">
              {f.frame !== null && (
                <Link
                  to="/matches/$matchId"
                  params={{ matchId: f.matchId }}
                  search={{ tab: "overview", f: f.frame }}
                >
                  <Button size="sm" variant="secondary">
                    <Play className="size-4 fill-current" aria-hidden />
                    Watch why
                  </Button>
                </Link>
              )}
              {!atEnd && (
                <Button size="sm" variant="primary" onClick={() => advance(f.id)}>
                  {step === 0 ? "I've practised this" : "I saw it in a match"}
                </Button>
              )}
              {atEnd && (
                <span className="self-center text-sm text-strength">
                  ✓ You've taken this all the way through.
                </span>
              )}
            </div>
            {!atEnd && step === 1 && (
              <p className="text-xs text-faint">
                Marking it practised doesn't mean it worked. The last rung is for when it turns up in a match
                on its own.
              </p>
            )}
          </Card>
        );
      })}
    </ul>
  );
}

/** Set a focus from anywhere — an insight, a rally, a shot that caught your eye. */
export function SetFocusButton({
  title,
  why,
  matchId,
  frame,
}: {
  title: string;
  why: string;
  matchId: string;
  frame: number | null;
}) {
  const addFocus = useStore((s) => s.addFocus);
  const focus = useStore((s) => s.focus);
  const already = focus.some((f) => f.title === title);
  return (
    <Button
      size="sm"
      variant="ghost"
      disabled={already}
      onClick={() => addFocus({ title, why, matchId, frame })}
    >
      {already ? "Already a focus" : "Make this my focus"}
    </Button>
  );
}

/* ───────────────────────── optional challenges ─────────────────────────
   Progress is computed from the matches, never awarded for opening a screen.
   Nothing here penalises a gap, and every one can be ignored. */

interface Challenge {
  id: string;
  name: string;
  goal: string;
  have: number;
  need: number;
  note: string;
}

export function challenges(): Challenge[] {
  const matches = readyMatches;
  const longest = Math.max(
    0,
    ...matches.flatMap((m) => m.rallies.filter((r) => r.official).map((r) => r.shots.length)),
  );
  const repertoire = new Set(matches.flatMap((m) => Object.keys(m.stats[youIn(m).id]?.strokes ?? {}))).size;
  const zonesUsed = new Set(
    matches.flatMap((m) => {
      const st = m.stats[youIn(m).id];
      return st ? ZONES.filter((z) => st.originZones[z] > 0) : [];
    }),
  ).size;
  const doublesRallies = matches
    .filter((m) => m.discipline === "doubles")
    .reduce((a, m) => a + (m.pairs?.[youIn(m).side]?.bothContributed ?? 0), 0);

  return [
    {
      id: "rally-explorer",
      name: "Rally Explorer",
      goal: "Keep a rally going for 12 shots",
      have: Math.min(longest, 12),
      need: 12,
      note: `Your longest so far is ${longest} shots.`,
    },
    {
      id: "shot-explorer",
      name: "Shot Explorer",
      goal: "Be seen playing 10 different shots",
      have: Math.min(repertoire, 10),
      need: 10,
      note: `${repertoire} so far. Shot naming is a Preview, so treat this as a nudge rather than a record.`,
    },
    {
      id: "court-explorer",
      name: "Court Explorer",
      goal: "Hit from all nine zones of your half",
      have: zonesUsed,
      need: 9,
      note: `You've played from ${zonesUsed} of them.`,
    },
    {
      id: "doubles-duo",
      name: "Doubles Duo",
      goal: "Build 50 rallies where both of you hit",
      have: Math.min(doublesRallies, 50),
      need: 50,
      note: `${doublesRallies} so far across your doubles matches.`,
    },
    {
      id: "showed-up",
      name: "Just Showed Up",
      goal: "Play five analysed matches",
      have: Math.min(matches.length, 5),
      need: 5,
      note: "Turning up counts. Nothing here is lost if you take a month off.",
    },
  ];
}

export function Challenges() {
  const dismissed = useStore((s) => s.dismissed);
  const dismiss = useStore((s) => s.dismiss);
  const list = challenges().filter((c) => !dismissed.includes(c.id));

  if (list.length === 0) {
    return <p className="text-sm text-muted">You've dismissed all of these. Nothing is missing.</p>;
  }

  return (
    <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {list.map((c) => {
        const done = c.have >= c.need;
        return (
          <Card as="li" key={c.id} className="flex flex-col gap-2">
            <div className="flex items-start justify-between gap-2">
              <span className="flex items-center gap-2 text-sm font-[650] text-ink">
                <Compass className="size-4 text-muted" aria-hidden />
                {c.name}
              </span>
              <button
                type="button"
                onClick={() => dismiss(c.id)}
                aria-label={`Hide ${c.name}`}
                className="shrink-0 rounded p-1 text-faint hover:text-ink"
              >
                <X className="size-3.5" aria-hidden />
              </button>
            </div>
            <p className="text-sm text-muted">{c.goal}</p>
            <div className="flex items-center gap-2">
              <span className="h-2 flex-1 overflow-hidden rounded-full bg-surface-raised">
                <span
                  className={done ? "block h-full bg-strength" : "block h-full bg-you"}
                  style={{ width: `${(c.have / c.need) * 100}%` }}
                />
              </span>
              <span className="tabular shrink-0 text-xs text-muted">
                {c.have} / {c.need}
              </span>
            </div>
            <p className="text-xs text-faint">{c.note}</p>
            {done && <p className="text-xs text-strength">✓ Done — nothing to claim, it just is.</p>}
          </Card>
        );
      })}
    </ul>
  );
}
