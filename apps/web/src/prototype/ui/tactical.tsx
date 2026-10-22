import { Play } from "lucide-react";
import type { ReceiveRow, Sequence, ServeRow, ShotEffect, Transitions } from "../data/analysis";
import { counterexamples } from "../data/analysis";
import type { Match, PlayerId } from "../data/types";
import { usePlayer } from "../player/store";
import { mmss } from "./analytics";

/* ─────────────────────────────────────────────────────────────────────────────
   Tactical views, drawn from the source blueprints in `Design/`.

   They exist to answer the questions the raw counts cannot: not "how many smashes"
   but "what happened after one", not "which shot ended the rally" but "what built it".
   ───────────────────────────────────────────────────────────────────────────── */

function WatchButton({ frame, label }: { frame: number; label: string }) {
  const seek = usePlayer((s) => s.seek);
  return (
    <button
      type="button"
      onClick={() => seek(frame, label)}
      aria-label={`Watch: ${label}`}
      className="inline-flex shrink-0 items-center gap-1 rounded-full border border-evidence/40 bg-evidence/8 px-2 py-0.5 text-xs font-medium text-evidence hover:bg-evidence/15"
    >
      <Play className="size-3 fill-current" aria-hidden />
      Watch
    </button>
  );
}

/* ───────────────────────── shot effectiveness ─────────────────────────
   Counts AND rates, every rate with its denominator. A shot played four times
   and a shot played sixty times are not comparable, and the table says so. */

export function ShotEffectiveness({ rows }: { rows: ShotEffect[] }) {
  const maxPlayed = Math.max(1, ...rows.map((r) => r.played));
  return (
    <div className="flex flex-col gap-3">
      <table className="w-full text-sm">
        <caption className="sr-only">Shots played, and what happened in those rallies</caption>
        <thead>
          <tr className="text-xs text-faint">
            <th className="pb-2 text-left font-[600]">Shot</th>
            <th className="pb-2 text-right font-[600]">Played</th>
            <th className="pb-2 text-right font-[600]">Finished a rally</th>
            <th className="pb-2 text-right font-[600]">Rallies won after playing it</th>
            <th className="pb-2" />
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const rate = r.ralliesWith > 0 ? r.ralliesWon / r.ralliesWith : 0;
            // Below five opportunities the rate is noise, and we say so instead of drawing it.
            const thin = r.ralliesWith < 5;
            return (
              <tr key={r.stroke} className="border-t border-edge">
                <th scope="row" className="py-2 text-left font-normal text-ink">
                  <span className="flex items-center gap-2">
                    {r.label}
                    <span
                      aria-hidden
                      className="h-1.5 rounded-full bg-you/50"
                      style={{ width: `${(r.played / maxPlayed) * 60}px` }}
                    />
                  </span>
                </th>
                <td className="tabular py-2 text-right text-ink">{r.played}</td>
                <td className="tabular py-2 text-right text-muted">
                  {r.finishedWin + r.finishedLoss > 0 ? (
                    <>
                      {r.finishedWin}
                      <span className="text-faint"> won</span> · {r.finishedLoss}
                      <span className="text-faint"> lost</span>
                    </>
                  ) : (
                    <span className="text-faint">—</span>
                  )}
                </td>
                <td className="tabular py-2 text-right">
                  {thin ? (
                    <span className="text-faint" title="Too few opportunities to read as a rate">
                      {r.ralliesWon} of {r.ralliesWith}
                    </span>
                  ) : (
                    <span className="text-ink">
                      {r.ralliesWon} of {r.ralliesWith}
                      <span className="ml-1.5 text-xs text-muted">{Math.round(rate * 100)}%</span>
                    </span>
                  )}
                </td>
                <td className="py-2 pl-2 text-right">
                  {r.exampleFrame !== null && (
                    <WatchButton frame={r.exampleFrame} label={`A ${r.label.toLowerCase()}`} />
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="text-xs text-faint">
        "Rallies won after playing it" counts rallies in which the shot appeared at all — it is an
        association, not a cause. A rate is left as a bare fraction where there were fewer than five
        opportunities.
      </p>
    </div>
  );
}

/* ───────────────────────── build-up ─────────────────────────
   The Front-End Blueprint is explicit that crediting only the last stroke misleads.
   These are the three-shot sequences that ended rallies, split by who won them. */

export function BuildUp({
  won,
  lost,
  sampleWon,
  sampleLost,
}: {
  won: Sequence[];
  lost: Sequence[];
  sampleWon: number;
  sampleLost: number;
}) {
  return (
    <div className="grid gap-5 md:grid-cols-2">
      <SequenceColumn title="Before the points you won" sample={sampleWon} rows={won} tone="you" />
      <SequenceColumn title="Before the points you lost" sample={sampleLost} rows={lost} tone="other" />
    </div>
  );
}

function SequenceColumn({
  title,
  sample,
  rows,
  tone,
}: {
  title: string;
  sample: number;
  rows: Sequence[];
  tone: "you" | "other";
}) {
  const max = Math.max(1, ...rows.map((r) => r.n));
  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm font-[600] text-ink">{title}</p>
      <p className="text-xs text-faint">{sample} rallies</p>
      {rows.length === 0 ? (
        <p className="text-sm text-muted">No sequence appeared often enough to list.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {rows.map((r) => (
            <li key={r.key} className="flex items-center gap-2">
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm text-ink" title={r.label}>
                  {r.label}
                </span>
                <span
                  className={
                    tone === "you"
                      ? "mt-1 block h-1.5 rounded-full bg-you"
                      : "mt-1 block h-1.5 rounded-full bg-other"
                  }
                  style={{ width: `${(r.n / max) * 100}%` }}
                />
              </span>
              <span className="tabular shrink-0 text-sm text-muted">{r.n}×</span>
              <WatchButton frame={r.exampleFrame} label={r.label} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

/* ───────────────────────── serve and receive ───────────────────────── */

export function ServeReceive({ serving, receiving }: { serving: ServeRow[]; receiving: ReceiveRow[] }) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="flex flex-col gap-2">
        <p className="text-sm font-[600] text-ink">When you served</p>
        {serving.length === 0 ? (
          <p className="text-sm text-muted">You didn't serve in a counted rally.</p>
        ) : (
          <ul className="flex flex-col gap-2.5">
            {serving.map((r) => (
              <li key={r.stroke} className="flex items-center gap-3">
                <span className="w-24 shrink-0 text-sm text-ink">{r.label}</span>
                <span className="flex h-5 flex-1 overflow-hidden rounded-[4px] bg-surface-raised">
                  <span className="bg-you" style={{ width: `${(r.won / Math.max(1, r.served)) * 100}%` }} />
                </span>
                <span className="tabular w-20 shrink-0 text-right text-sm text-muted">
                  {r.won} of {r.served}
                </span>
                {r.exampleFrame !== null && (
                  <WatchButton frame={r.exampleFrame} label={`Your ${r.label.toLowerCase()}`} />
                )}
              </li>
            ))}
          </ul>
        )}
        <p className="text-xs text-faint">Rallies won, of rallies you served.</p>
      </div>

      <div className="flex flex-col gap-2">
        <p className="text-sm font-[600] text-ink">When you received</p>
        {receiving.length === 0 ? (
          <p className="text-sm text-muted">You didn't take a serve in a counted rally.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {receiving.map((r) => (
              <li key={r.against} className="flex flex-col gap-1.5">
                <span className="flex items-center justify-between gap-2">
                  <span className="text-sm text-ink">Against a {r.againstLabel.toLowerCase()}</span>
                  <span className="tabular text-sm text-muted">
                    {r.won} of {r.received}
                  </span>
                </span>
                <span className="flex flex-wrap gap-1.5">
                  {r.replies.slice(0, 5).map((reply) => (
                    <span
                      key={reply.stroke}
                      className="rounded-full border border-edge px-2 py-0.5 text-xs text-muted"
                    >
                      {reply.label} ×{reply.n}
                    </span>
                  ))}
                  {r.exampleFrame !== null && (
                    <WatchButton
                      frame={r.exampleFrame}
                      label={`Receiving a ${r.againstLabel.toLowerCase()}`}
                    />
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
        <p className="text-xs text-faint">What you played with the return, and how those rallies went.</p>
      </div>
    </div>
  );
}

/* ───────────────────────── attack / defence transitions ───────────────────────── */

export function TransitionsPanel({ t }: { t: Transitions }) {
  const rows = [
    {
      label: "You were defending, then attacked",
      n: t.defenceToAttack,
      won: t.defenceToAttackWon,
    },
    {
      label: "You were attacking, then had to defend",
      n: t.attackToDefence,
      won: t.attackToDefenceWon,
    },
  ];
  const max = Math.max(1, ...rows.map((r) => r.n));
  return (
    <div className="flex flex-col gap-4">
      <ul className="flex flex-col gap-3">
        {rows.map((r) => (
          <li key={r.label} className="flex flex-col gap-1.5">
            <span className="flex items-baseline justify-between gap-3">
              <span className="text-sm text-ink">{r.label}</span>
              <span className="tabular shrink-0 text-sm text-muted">
                {r.n} rallies · won {r.won}
              </span>
            </span>
            <span className="flex h-2.5 overflow-hidden rounded-full bg-surface-raised">
              <span className="bg-you" style={{ width: `${(r.won / max) * 100}%` }} />
              <span className="bg-other/50" style={{ width: `${((r.n - r.won) / max) * 100}%` }} />
            </span>
          </li>
        ))}
      </ul>
      {t.examples.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs text-muted">Watch a turnaround:</span>
          {t.examples.map((e) => (
            <WatchButton key={e.frame} frame={e.frame} label={e.label} />
          ))}
        </div>
      )}
      <p className="text-xs text-faint">
        Counted over the {t.sample} rallies where you played at least two shots. Turning defence into attack
        is a description of what happened, not a judgement about how well you did it.
      </p>
    </div>
  );
}

/* ───────────────────────── counterexamples ─────────────────────────
   A highlight reel is selected for being good. This is the other half. */

export function Counterexamples({ match, pid }: { match: Match; pid: PlayerId }) {
  const rows = counterexamples(match, pid);
  if (rows.length === 0) {
    return (
      <p className="text-sm text-muted">
        No long rally this match ended on your racket — unusual, and worth noting.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-3">
      <ul className="flex flex-col gap-2">
        {rows.map((r) => (
          <li key={r.rallyNo} className="flex items-center gap-3">
            <span className="tabular w-11 shrink-0 text-xs text-faint">{mmss(r.frame, match.fps)}</span>
            <span className="min-w-0 flex-1 text-sm text-ink">
              Rally {r.rallyNo} — {r.reason}
            </span>
            <WatchButton frame={r.frame} label={`Rally ${r.rallyNo}`} />
          </li>
        ))}
      </ul>
      <p className="text-xs text-faint">
        The moments reel picks rallies for being good. These are long rallies that ended on your racket, shown
        so the picture isn't only the flattering half.
      </p>
    </div>
  );
}
