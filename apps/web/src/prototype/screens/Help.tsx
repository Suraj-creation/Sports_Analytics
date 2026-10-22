import { ChevronLeft } from "lucide-react";
import { Link, useNavigate, useSearch } from "../nav";
import { Button, Card } from "../ui/primitives";
import { Page } from "../ui/shell";

/* ─────────────────────────────────────────────────────────────────────────────
   Help — what every number means, and what the system can't do.

   The limits page is not an apology. It is how a player knows which numbers to lean
   on, which is what makes the rest of the analytics worth reading.
   ───────────────────────────────────────────────────────────────────────────── */

interface Topic {
  id: string;
  title: string;
  summary: string;
  body: string[];
  basis?: string;
  limits?: string[];
}

const TOPICS: Topic[] = [
  {
    id: "rallies",
    title: "Rallies and shots",
    summary: "How a rally is found and how shots are counted inside it.",
    body: [
      "A rally runs from the serve to the shuttle going dead. The system finds the boundaries from the shuttle's motion and the players' contacts, then counts one shot per contact.",
      "Warm-up and replayed exchanges are kept on the timeline but marked 'not counted' — they stay out of the score and out of every statistic.",
    ],
    basis: "Rally-start and rally-end events, with the contact events between them.",
    limits: [
      "A rally the camera could not follow end to end is excluded from every number rather than estimated.",
    ],
  },
  {
    id: "shots",
    title: "Shot names",
    summary: "Smash, drop, clear, lift — how the system decides which is which.",
    body: [
      "Each contact is classified into one of twelve shot types from the shuttle's path before and after it, the hitter's position, and their body position at contact. A smash played off the ground is additionally marked as a jump smash.",
      "This is the youngest part of the pipeline. The classifier is rule-based and has not been validated on this venue's camera angle, so treat each name as the system's best guess rather than a fact.",
    ],
    basis: "Stroke classification over the contact events, with the jump-smash subtype from pose.",
    limits: [
      "Rule-based, not learned from labelled examples.",
      "Close shots — a drop against a slow smash, a push against a drive — are the easiest to get wrong.",
    ],
  },
  {
    id: "court",
    title: "Court maps",
    summary: "Where players stood, hit from, and put the shuttle.",
    body: [
      "The court is calibrated once per venue camera, which lets the system turn pixels into positions on the floor in metres. Positions are then grouped into three depth bands and three width bands per half — the nine zones you see in the tables.",
      "'Where their shots go' is the one to read carefully. We do not reconstruct the shuttle's flight, so that map shows where the receiver met the shuttle, which is close to but not the same as where it would have landed.",
    ],
    basis: "Per-frame foot position projected onto the court plane through the calibration.",
    limits: [
      "Accuracy drops if the camera is moved after calibration.",
      "Landing points are not measured; the receiver's position stands in for them and is named as such.",
    ],
  },
  {
    id: "movement",
    title: "Distance, steps and work rate",
    summary: "What the movement numbers are, and what they are not.",
    body: [
      "Distance is the summed movement of a player's tracked position while the shuttle is in play. Steps are derived from that distance at an average stride of 0.78 m — they are an estimate, not a count of footfalls.",
      "Work rate is distance divided by time the shuttle was actually live, so standing between rallies does not dilute it.",
      "These are useful for comparing players within one match and yourself across matches at the same venue. They are not a fitness measurement, and nothing here should be read as a health or training recommendation.",
    ],
    basis: "Tracked position per frame, summed over rallies the camera followed.",
    limits: [
      "Tracking jitter inflates distance; the figure is better as a comparison than an absolute.",
      "Not comparable across different camera setups.",
    ],
  },
  {
    id: "moments",
    title: "How moments are chosen",
    summary: "Why this rally and not that one.",
    body: [
      "Every counted rally is scored on what actually happened in it: how long it ran, whether it finished with a smash, how many shots a player took from under the shuttle, how long the net exchange was, how many different shots were used, and whether it was played at 20-all or on a game point.",
      "Those parts are kept, not thrown away — the 'Why this was picked' panel on each moment shows the exact decomposition.",
      "The top-scoring rallies are then re-ranked for variety, so the reel is not six smashes in a row. In doubles, a rally both partners built is credited to both.",
    ],
    basis: "The reason decomposition per rally, re-ranked for category diversity.",
  },
  {
    id: "doubles",
    title: "Doubles",
    summary: "What the pair analysis measures.",
    body: [
      "A doubles match tracks four players. Alongside each player's own numbers, the pair gets its own: rallies in which both partners hit the shuttle, times one partner took over after the other played from under the shuttle, rear-court attacks followed by an interception at the net, and how the front and rear of the court were split between you.",
      "Court coverage is shown per player rather than merged, because the shape of a pair is the interesting part.",
      "The system reads what happened on court. It cannot hear you and does not know what either of you intended, so nothing here describes communication or whose 'fault' a point was.",
    ],
    limits: ["Who should have taken a shot is a judgement the system does not make."],
  },
  {
    id: "score",
    title: "The score",
    summary: "How the scoreline is worked out.",
    body: [
      "Each rally's winner is decided from the final contact and the shuttle's outcome, then folded through standard rally scoring to 21, best of three.",
      "If a rally winner is wrong, every score after it is wrong too. That is why correcting one rally re-folds the rest rather than patching a single number.",
    ],
  },
];

export function HelpScreen() {
  const { topic } = useSearch<{ topic?: string }>({ from: "/help" });
  const navigate = useNavigate();
  const article = TOPICS.find((t) => t.id === topic);

  if (article) {
    return (
      <Page title={article.title} width="form">
        <div className="flex flex-col gap-6">
          <button
            type="button"
            onClick={() => navigate({ to: ".", search: {} })}
            className="inline-flex w-fit items-center gap-1 text-sm text-muted hover:text-ink"
          >
            <ChevronLeft className="size-4" aria-hidden />
            All help
          </button>
          <div className="measure flex flex-col gap-4 text-base text-muted">
            {article.body.map((p) => (
              <p key={p}>{p}</p>
            ))}
          </div>
          {article.basis && (
            <Card className="flex flex-col gap-2">
              <p className="font-[600] text-ink">What it is measured from</p>
              <p className="text-sm text-muted">{article.basis}</p>
            </Card>
          )}
          {article.limits && (
            <Card className="flex flex-col gap-2">
              <p className="font-[600] text-ink">Known limits</p>
              <ul className="flex list-disc flex-col gap-1.5 pl-5 text-sm text-muted">
                {article.limits.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </Page>
    );
  }

  return (
    <Page
      title="Help"
      lead="What every number on your matches means, how it is measured, and where it stops being reliable."
    >
      <ul className="grid gap-3 md:grid-cols-2">
        {TOPICS.map((t) => (
          <li key={t.id}>
            <Link
              to="/help"
              search={{ topic: t.id }}
              className="flex h-full flex-col gap-1.5 rounded-[14px] border border-edge bg-surface p-4 hover:border-edge-strong"
            >
              <span className="font-[600] text-ink">{t.title}</span>
              <span className="text-sm text-muted">{t.summary}</span>
            </Link>
          </li>
        ))}
      </ul>
      <Card className="mt-6 flex flex-col gap-3">
        <p className="font-[600] text-ink">Something look wrong?</p>
        <p className="measure text-sm text-muted">
          If a number doesn't match what you remember, that's worth telling us — it's usually the fastest way
          we find a detection problem.
        </p>
        <div>
          <Button variant="secondary">Report a problem</Button>
        </div>
        <p className="text-xs text-faint">
          In this prototype that button does nothing — there is no intake queue behind it yet, and a form that
          silently drops your message would be worse than no form.
        </p>
      </Card>
    </Page>
  );
}
