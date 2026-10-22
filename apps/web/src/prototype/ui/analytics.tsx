import { clsx } from "clsx";
import { Play } from "lucide-react";
import { type ReactNode, useId, useState } from "react";
import type {
  Heatmap,
  HeatmapKind,
  Insight,
  Match,
  MomentumPoint,
  Player,
  PlayerId,
  PlayerStats,
  Rally,
  Zone,
} from "../data/types";
import { STROKE_LABEL, ZONES } from "../data/types";
import { usePlayer } from "../player/store";
import { Button } from "./primitives";

/* ─────────────────────────────────────────────────────────────────────────────
   The analytics components.

   Three rules hold across all of them:
     1. Every panel states the question it answers, not a noun.
     2. Every panel carries narration generated from its own numbers, with a Watch
        button that seeks the player to the evidence.
     3. Series are separated by shape and pattern as well as colour, and every chart
        has a table behind it.
   ───────────────────────────────────────────────────────────────────────────── */

export const ROLE_VAR: Record<string, string> = {
  you: "var(--c-you)",
  partner: "var(--c-partner)",
  "opponent-1": "var(--c-other)",
  "opponent-2": "color-mix(in oklab, var(--c-other) 55%, var(--c-canvas))",
};

export function roleColour(p: Player | undefined): string {
  return ROLE_VAR[p?.colour ?? "opponent-1"] ?? "var(--c-other)";
}

/** Shape redundancy: you = circle, partner = diamond, opponents = square / triangle. */
export function RoleGlyph({ player, className }: { player: Player | undefined; className?: string }) {
  const c = roleColour(player);
  const role = player?.colour ?? "opponent-1";
  const common = { className: clsx("inline-block shrink-0", className ?? "size-2.5"), style: { color: c } };
  if (role === "you")
    return (
      <svg viewBox="0 0 10 10" {...common} aria-hidden>
        <circle cx="5" cy="5" r="4.5" fill="currentColor" />
      </svg>
    );
  if (role === "partner")
    return (
      <svg viewBox="0 0 10 10" {...common} aria-hidden>
        <path d="M5 0.5 9.5 5 5 9.5 0.5 5Z" fill="currentColor" />
      </svg>
    );
  if (role === "opponent-2")
    return (
      <svg viewBox="0 0 10 10" {...common} aria-hidden>
        <path d="M5 0.5 9.5 9.5H0.5Z" fill="currentColor" />
      </svg>
    );
  return (
    <svg viewBox="0 0 10 10" {...common} aria-hidden>
      <rect x="0.7" y="0.7" width="8.6" height="8.6" rx="1" fill="currentColor" />
    </svg>
  );
}

/* ───────────────────────── panel ───────────────────────── */

export function Panel({
  question,
  hint,
  tag,
  insights,
  table,
  actions,
  basis,
  className,
  children,
}: {
  question: string;
  hint?: string;
  tag?: ReactNode;
  insights?: Insight[];
  table?: ReactNode;
  actions?: ReactNode;
  /** What this chart was measured over — sample size, coverage, exclusions.
      Required by the source blueprint on every chart, and it is the line that
      makes a number arguable rather than something to be taken on faith. */
  basis?: string;
  className?: string;
  children: ReactNode;
}) {
  const [showTable, setShowTable] = useState(false);
  const id = useId();
  return (
    <section
      aria-labelledby={id}
      className={clsx("flex flex-col rounded-[14px] border border-edge bg-surface", className)}
    >
      <header className="flex flex-wrap items-start justify-between gap-2 border-b border-edge px-4 py-3">
        <div className="min-w-0">
          <h3 id={id} className="text-base font-[650] leading-snug text-ink">
            {question}
          </h3>
          {hint && <p className="mt-0.5 text-sm text-muted">{hint}</p>}
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {tag}
          {table && (
            <Button size="sm" variant="ghost" onClick={() => setShowTable((v) => !v)}>
              {showTable ? "Chart" : "Table"}
            </Button>
          )}
          {actions}
        </div>
      </header>
      <div className="flex-1 p-4">{showTable && table ? table : children}</div>
      {basis && <p className="border-t border-edge px-4 py-2 text-xs text-faint">Measured over {basis}.</p>}
      {insights && insights.length > 0 && <InsightList insights={insights} />}
    </section>
  );
}

export function InsightList({ insights }: { insights: Insight[] }) {
  const seek = usePlayer((s) => s.seek);
  return (
    <ul className="flex flex-col divide-y divide-edge border-t border-edge">
      {insights.map((i) => (
        <li key={i.text} className="flex items-start gap-3 px-4 py-2.5">
          <span
            aria-hidden
            className={clsx(
              "mt-[7px] size-1.5 shrink-0 rounded-full",
              i.tone === "strength" && "bg-strength",
              i.tone === "watch" && "bg-opportunity",
              i.tone === "neutral" && "bg-muted",
            )}
          />
          <p className="min-w-0 flex-1 text-sm text-muted">{i.text}</p>
          {i.frame !== undefined && (
            <button
              type="button"
              onClick={() => seek(i.frame ?? 0, i.text)}
              className="inline-flex shrink-0 items-center gap-1 rounded-full border border-evidence/40 bg-evidence/8 px-2.5 py-1 text-xs font-medium text-evidence hover:bg-evidence/15"
            >
              <Play className="size-3 fill-current" aria-hidden />
              Watch
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}

/* ───────────────────────── stat tiles ───────────────────────── */

export function StatTile({
  value,
  unit,
  label,
  sub,
  delta,
  hero,
  onWatch,
}: {
  value: string | number;
  unit?: string;
  label: string;
  sub?: string;
  delta?: { value: number; unit: string };
  hero?: boolean;
  onWatch?: () => void;
}) {
  const seekable = Boolean(onWatch);
  return (
    <div className="flex flex-col gap-1 rounded-[14px] border border-edge bg-surface p-4">
      <span className="flex items-baseline gap-1.5">
        <span className={clsx("numerals leading-none text-ink", hero ? "text-[2.75rem]" : "text-3xl")}>
          {value}
        </span>
        {unit && <span className="text-sm text-muted">{unit}</span>}
      </span>
      <span className="text-sm font-[600] text-ink">{label}</span>
      {sub && <span className="text-xs text-faint">{sub}</span>}
      {delta && (
        <span className={clsx("tabular text-xs", delta.value === 0 ? "text-faint" : "text-muted")}>
          {delta.value > 0 ? "+" : ""}
          {delta.value} {delta.unit} since your last match
        </span>
      )}
      {seekable && (
        <button
          type="button"
          onClick={onWatch}
          className="mt-1 inline-flex w-fit items-center gap-1 text-xs font-medium text-evidence hover:underline"
        >
          <Play className="size-3 fill-current" aria-hidden />
          Watch
        </button>
      )}
    </div>
  );
}

/* ───────────────────────── head to head ─────────────────────────
   Two or four players, mirrored bars. Works for singles and doubles by
   summing a side when there are two players on it. */

export interface H2HRow {
  label: string;
  get: (s: PlayerStats) => number;
  fmt?: (v: number) => string;
  /** Lower is not "worse" — we never colour a row good or bad. */
  hint?: string;
}

export const H2H_ROWS: H2HRow[] = [
  { label: "Points won", get: (s) => s.pointsWon },
  { label: "Winners", get: (s) => s.winners, hint: "Rallies you finished with a shot they couldn't return" },
  { label: "Ended long or wide", get: (s) => s.errorsOut },
  { label: "Ended in the net", get: (s) => s.errorsNet },
  { label: "Shots played", get: (s) => s.shotsPlayed },
  { label: "Returns kept in play", get: (s) => s.returnsMade },
  { label: "Smashes", get: (s) => s.smashes },
  { label: "Jump smashes", get: (s) => s.jumpSmashes },
  { label: "Points won with a smash", get: (s) => s.smashPoints },
  { label: "Net shots", get: (s) => s.netShots },
  { label: "Defensive saves", get: (s) => s.defensiveSaves },
  { label: "Points won at 20-all or on a game point", get: (s) => s.pointsWonUnderPressure },
  { label: "Distance covered", get: (s) => s.distanceM, fmt: (v) => `${Math.round(v)} m` },
  { label: "Steps", get: (s) => s.steps, fmt: (v) => Math.round(v).toLocaleString() },
];

export function HeadToHead({ match, rows = H2H_ROWS }: { match: Match; rows?: H2HRow[] }) {
  const left = match.players.filter((p) => p.side === "A");
  const right = match.players.filter((p) => p.side === "B");

  const sum = (ps: Player[], get: (s: PlayerStats) => number) =>
    ps.reduce((a, p) => a + (match.stats[p.id] ? get(match.stats[p.id] as PlayerStats) : 0), 0);

  return (
    <table className="w-full text-sm">
      <caption className="sr-only">Statistics per side</caption>
      <thead>
        <tr className="text-xs text-faint">
          <th className="w-16 pb-2 text-right font-[600]">
            <span className="flex items-center justify-end gap-1">
              {left.map((p) => (
                <RoleGlyph key={p.id} player={p} />
              ))}
            </span>
          </th>
          <th className="pb-2" />
          <th className="pb-2 text-center font-[600]">
            <span className="text-ink">{match.sides.A.label}</span>
            <span className="px-2 text-faint">vs</span>
            <span className="text-ink">{match.sides.B.label}</span>
          </th>
          <th className="pb-2" />
          <th className="w-16 pb-2 text-left font-[600]">
            <span className="flex items-center gap-1">
              {right.map((p) => (
                <RoleGlyph key={p.id} player={p} />
              ))}
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => {
          const a = sum(left, r.get);
          const b = sum(right, r.get);
          const max = Math.max(a, b, 1);
          const fmt = r.fmt ?? ((v: number) => String(Math.round(v)));
          return (
            <tr key={r.label} className="border-b border-edge last:border-0">
              <td className="tabular py-1.5 pr-2 text-right font-[600] text-ink">{fmt(a)}</td>
              <td className="w-[26%] py-1.5">
                <span className="flex justify-end">
                  <span className="h-2.5 rounded-l-sm bg-you" style={{ width: `${(a / max) * 100}%` }} />
                </span>
              </td>
              <th
                scope="row"
                className="whitespace-nowrap px-3 py-1.5 text-center text-xs font-normal text-muted"
                title={r.hint}
              >
                {r.label}
              </th>
              <td className="w-[26%] py-1.5">
                <span
                  className="block h-2.5 rounded-r-sm bg-other"
                  style={{
                    width: `${(b / max) * 100}%`,
                    backgroundImage:
                      "repeating-linear-gradient(45deg, transparent 0 3px, rgb(255 255 255 / .22) 3px 4px)",
                  }}
                />
              </td>
              <td className="tabular py-1.5 pl-2 font-[600] text-ink">{fmt(b)}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

/* ───────────────────────── shot mix ───────────────────────── */

export function StrokeMix({ match, ids }: { match: Match; ids: PlayerId[] }) {
  const keys = new Set<string>();
  for (const id of ids) for (const k of Object.keys(match.stats[id]?.strokes ?? {})) keys.add(k);
  const list = [...keys]
    .filter((k) => k !== "jump_smash")
    .sort((x, y) => total(match, ids, y) - total(match, ids, x));
  const max = Math.max(1, ...list.flatMap((k) => ids.map((id) => match.stats[id]?.strokes[k] ?? 0)));

  return (
    <div className="flex flex-col gap-3">
      <ul className="flex flex-col gap-2.5">
        {list.map((k) => (
          <li key={k} className="grid grid-cols-[96px_1fr] items-center gap-3">
            <span className="truncate text-sm text-ink" title={STROKE_LABEL[k] ?? k}>
              {STROKE_LABEL[k] ?? k}
            </span>
            <span className="flex flex-col gap-1">
              {ids.map((id) => {
                const p = match.players.find((x) => x.id === id);
                const v = match.stats[id]?.strokes[k] ?? 0;
                return (
                  <span key={id} className="flex items-center gap-2">
                    <span
                      className="h-2.5 rounded-sm"
                      style={{
                        width: `${(v / max) * 100}%`,
                        minWidth: v ? 3 : 0,
                        background: roleColour(p),
                      }}
                    />
                    <span className="tabular text-xs text-muted">{v}</span>
                  </span>
                );
              })}
            </span>
          </li>
        ))}
      </ul>
      <Legend match={match} ids={ids} />
    </div>
  );
}

function total(match: Match, ids: PlayerId[], k: string) {
  return ids.reduce((a, id) => a + (match.stats[id]?.strokes[k] ?? 0), 0);
}

export function Legend({ match, ids }: { match: Match; ids: PlayerId[] }) {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-muted">
      {ids.map((id) => {
        const p = match.players.find((x) => x.id === id);
        return (
          <li key={id} className="flex items-center gap-1.5">
            <RoleGlyph player={p} />
            {p?.short}
            {p?.isYou && " (you)"}
          </li>
        );
      })}
    </ul>
  );
}

/* ───────────────────────── attack / neutral / defend ───────────────────────── */

export function FamilySplit({ match, ids }: { match: Match; ids: PlayerId[] }) {
  return (
    <div className="flex flex-col gap-4">
      {ids.map((id) => {
        const st = match.stats[id];
        const p = match.players.find((x) => x.id === id);
        if (!st) return null;
        const f = st.familySplit;
        const t = Math.max(1, f.attack + f.neutral + f.defend + f.serve);
        const parts = [
          { k: "Attacking", v: f.attack, cls: "bg-you" },
          { k: "Neutral", v: f.neutral, cls: "bg-muted" },
          { k: "Defending", v: f.defend, cls: "bg-other" },
          { k: "Serves", v: f.serve, cls: "bg-edge-strong" },
        ];
        return (
          <div key={id} className="flex flex-col gap-1.5">
            <span className="flex items-center gap-1.5 text-sm font-[600] text-ink">
              <RoleGlyph player={p} />
              {p?.short}
            </span>
            <span className="flex h-6 overflow-hidden rounded-[6px]">
              {parts.map((part) => (
                <span
                  key={part.k}
                  className={clsx(part.cls, "flex items-center justify-center")}
                  style={{ width: `${(part.v / t) * 100}%` }}
                  title={`${part.k}: ${part.v}`}
                >
                  {part.v / t > 0.12 && (
                    <span className="tabular text-[11px] font-[600] text-canvas">
                      {Math.round((part.v / t) * 100)}%
                    </span>
                  )}
                </span>
              ))}
            </span>
            <span className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
              {parts.map((part) => (
                <span key={part.k} className="flex items-center gap-1.5">
                  <span aria-hidden className={clsx("size-2.5 rounded-sm", part.cls)} />
                  {part.k} {part.v}
                </span>
              ))}
            </span>
          </div>
        );
      })}
    </div>
  );
}

/* ───────────────────────── court heatmap ─────────────────────────
   Top-down, near end at the bottom, always. The heat is the player's own colour
   at a single-hue ramp; cells below the sample floor are hatched, not blank. */

export function CourtHeatmap({
  heat,
  player,
  kind,
  width = 220,
}: {
  heat: Heatmap | undefined;
  player: Player | undefined;
  kind: HeatmapKind;
  width?: number;
}) {
  if (!heat) return null;
  const rows = heat.values.length;
  const cols = heat.values[0]?.length ?? 7;
  const cw = 100 / cols;
  const ch = 190 / rows;
  const colour = roleColour(player);
  const cells = heat.values.flatMap((row, y) => row.map((v, x) => ({ id: `r${y}c${x}`, y, x, v })));
  // `targeting` and `landing` describe the other half, so flip the emphasis.
  const otherHalf = kind === "targeting" || kind === "landing";

  return (
    <div className="flex flex-col items-center gap-2" style={{ width }}>
      <svg viewBox="0 0 110 206" className="w-full" role="img" aria-label={`${kind} map`}>
        <rect x="5" y="8" width="100" height="190" className="fill-court-floor" />
        {cells.map((c) =>
          c.v <= 0.02 ? (
            <rect
              key={c.id}
              x={5 + c.x * cw}
              y={8 + c.y * ch}
              width={cw}
              height={ch}
              className="hatch"
              fill="transparent"
              opacity="0.5"
            />
          ) : (
            <rect
              key={c.id}
              x={5 + c.x * cw}
              y={8 + c.y * ch}
              width={cw + 0.3}
              height={ch + 0.3}
              fill={colour}
              opacity={0.1 + 0.8 * Math.sqrt(c.v)}
            />
          ),
        )}
        {/* court lines on top so the heat never hides them */}
        <g className="stroke-court-line" strokeWidth="1.1" fill="none">
          <rect x="5" y="8" width="100" height="190" strokeWidth="1.6" />
          <line x1="5" y1="103" x2="105" y2="103" strokeWidth="2" />
          <line x1="5" y1="70" x2="105" y2="70" />
          <line x1="5" y1="136" x2="105" y2="136" />
          <line x1="5" y1="19" x2="105" y2="19" opacity="0.7" />
          <line x1="5" y1="187" x2="105" y2="187" opacity="0.7" />
          <line x1="55" y1="8" x2="55" y2="70" />
          <line x1="55" y1="136" x2="55" y2="198" />
          <line x1="12.5" y1="8" x2="12.5" y2="198" opacity="0.5" />
          <line x1="97.5" y1="8" x2="97.5" y2="198" opacity="0.5" />
        </g>
        <text x="55" y="5" textAnchor="middle" fontSize="5" className="fill-faint">
          {otherHalf ? "their half" : "far end"}
        </text>
        <text x="55" y="204" textAnchor="middle" fontSize="5" className="fill-faint">
          {otherHalf ? "" : "near end — your side"}
        </text>
      </svg>
      <div className="flex w-full items-center gap-2 text-[11px] text-muted">
        <span>less</span>
        <span
          aria-hidden
          className="h-2 flex-1 rounded-full"
          style={{ background: `linear-gradient(90deg, transparent, ${colour})` }}
        />
        <span>more</span>
      </div>
    </div>
  );
}

/** The 3x3 zone counts behind a heatmap — the numbers, for whoever wants them. */
export function ZoneTable({ counts, title }: { counts: Record<Zone, number>; title: string }) {
  const rows: [string, Zone[]][] = [
    ["Front", ["front-left", "front-centre", "front-right"]],
    ["Middle", ["mid-left", "mid-centre", "mid-right"]],
    ["Rear", ["rear-left", "rear-centre", "rear-right"]],
  ];
  const total = ZONES.reduce((a, z) => a + counts[z], 0) || 1;
  return (
    <table className="w-full text-sm">
      <caption className="sr-only">{title}</caption>
      <thead>
        <tr className="text-xs text-faint">
          <th className="py-1 text-left font-[600]" />
          <th className="py-1 text-right font-[600]">Left</th>
          <th className="py-1 text-right font-[600]">Centre</th>
          <th className="py-1 text-right font-[600]">Right</th>
        </tr>
      </thead>
      <tbody className="tabular">
        {rows.map(([label, zs]) => (
          <tr key={label} className="border-t border-edge">
            <th scope="row" className="py-1.5 text-left font-[600] text-ink">
              {label}
            </th>
            {zs.map((z) => (
              <td key={z} className="py-1.5 text-right text-muted">
                {counts[z]}
                <span className="ml-1 text-xs text-faint">{Math.round((counts[z] / total) * 100)}%</span>
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* ───────────────────────── momentum ───────────────────────── */

export function MomentumChart({ match }: { match: Match }) {
  const seek = usePlayer((s) => s.seek);
  const [hover, setHover] = useState<number | null>(null);
  const pts: MomentumPoint[] = match.momentum;
  if (pts.length < 3) return <p className="text-sm text-muted">Not enough points yet.</p>;
  const W = 640;
  const H = 150;
  const pad = { l: 8, r: 8, t: 10, b: 20 };
  const X = (i: number) => pad.l + (i / (pts.length - 1)) * (W - pad.l - pad.r);
  const Y = (v: number) => pad.t + ((1 - v) / 2) * (H - pad.t - pad.b);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(p.value).toFixed(1)}`).join("");

  const area = `${line}L${X(pts.length - 1)},${Y(0)}L${X(0)},${Y(0)}Z`;
  const shifts = new Set(match.momentumShifts);
  const hp = hover != null ? pts[hover] : undefined;
  const score = hp ? match.scoreTimeline.find((s) => s.rallyNo === hp.rallyNo) : undefined;

  return (
    <div className="relative">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label="Run of play through the match"
        onMouseMove={(e) => {
          const r = e.currentTarget.getBoundingClientRect();
          const fx = ((e.clientX - r.left) / r.width) * W;
          const i = Math.round(((fx - pad.l) / (W - pad.l - pad.r)) * (pts.length - 1));
          setHover(Math.max(0, Math.min(pts.length - 1, i)));
        }}
        onMouseLeave={() => setHover(null)}
      >
        <defs>
          <clipPath id="mom-up">
            <rect x="0" y="0" width={W} height={Y(0)} />
          </clipPath>
          <clipPath id="mom-dn">
            <rect x="0" y={Y(0)} width={W} height={H} />
          </clipPath>
        </defs>
        {[-1, -0.5, 0.5, 1].map((v) => (
          <line key={v} x1={pad.l} x2={W - pad.r} y1={Y(v)} y2={Y(v)} className="stroke-edge" />
        ))}
        <path d={area} className="fill-you" fillOpacity={0.25} clipPath="url(#mom-up)" />
        <path d={area} className="fill-other" fillOpacity={0.25} clipPath="url(#mom-dn)" />
        <path d={line} fill="none" className="stroke-you" strokeWidth="2" clipPath="url(#mom-up)" />
        <path d={line} fill="none" className="stroke-other" strokeWidth="2" clipPath="url(#mom-dn)" />
        <line x1={pad.l} x2={W - pad.r} y1={Y(0)} y2={Y(0)} className="stroke-edge-strong" />
        {pts.map((p, i) =>
          shifts.has(p.rallyNo) ? (
            <circle
              key={p.rallyNo}
              cx={X(i)}
              cy={Y(p.value)}
              r="4"
              className="fill-surface stroke-ink"
              strokeWidth="2"
            />
          ) : null,
        )}
        {hp && hover != null && (
          <g>
            <line x1={X(hover)} x2={X(hover)} y1={pad.t} y2={H - pad.b} className="stroke-muted" />
            <circle cx={X(hover)} cy={Y(hp.value)} r="4" className="fill-ink" />
          </g>
        )}
      </svg>
      {match.momentumShifts.length > 0 && (
        <div className="mb-2 flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-muted">Jump to a lead change:</span>
          {match.momentumShifts.slice(0, 10).map((no) => {
            const r = match.rallies.find((x) => x.no === no);
            return (
              <button
                key={no}
                type="button"
                onClick={() => r && seek(r.frames[0], `Lead changed at rally ${no}`)}
                className="rounded-full border border-edge px-2 py-0.5 text-xs text-muted hover:border-edge-strong hover:text-ink"
              >
                {no}
              </button>
            );
          })}
        </div>
      )}
      <div className="flex justify-between text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="size-2.5 rounded-full bg-you" /> {match.sides.A.label} ahead
        </span>
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="size-2.5 rounded-sm bg-other" /> {match.sides.B.label} ahead
        </span>
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="size-2.5 rounded-full border border-ink" /> lead changed
        </span>
      </div>
      {hp && hover != null && (
        <div
          className="pointer-events-none absolute top-0 z-10 -translate-x-1/2 rounded-[10px] border border-edge bg-surface px-2 py-1 text-xs shadow-[var(--shadow-pop)]"
          style={{ left: `${(X(hover) / W) * 100}%` }}
        >
          <p className="font-[600] text-ink">Rally {hp.rallyNo}</p>
          {score && (
            <p className="tabular text-muted">
              Game {score.game} · {score.score.A}–{score.score.B}
            </p>
          )}
          {hp.run.length > 1 && (
            <p className="text-muted">
              {match.sides[hp.run.side].label} on a run of {hp.run.length}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

/* ───────────────────────── rally length distribution ───────────────────────── */

export function RallyHistogram({ match }: { match: Match }) {
  const playClip = usePlayer((s) => s.playClip);
  const offs = match.rallies.filter((r) => r.official);
  const buckets = [
    { label: "1–3", min: 1, max: 3 },
    { label: "4–7", min: 4, max: 7 },
    { label: "8–11", min: 8, max: 11 },
    { label: "12–15", min: 12, max: 15 },
    { label: "16+", min: 16, max: 999 },
  ];
  const counts = buckets.map((b) => ({
    ...b,
    rallies: offs.filter((r) => r.shots.length >= b.min && r.shots.length <= b.max),
  }));
  const max = Math.max(1, ...counts.map((c) => c.rallies.length));

  return (
    <div className="flex items-end gap-3" style={{ height: 160 }}>
      {counts.map((c) => (
        <div key={c.label} className="flex flex-1 flex-col items-center justify-end gap-1.5">
          <span className="tabular text-sm font-[600] text-ink">{c.rallies.length}</span>
          <button
            type="button"
            disabled={c.rallies.length === 0}
            onClick={() => {
              const r = c.rallies[0];
              if (r) playClip(r.frames[0], r.frames[1], `A ${r.shots.length}-shot rally`);
            }}
            aria-label={`${c.rallies.length} rallies of ${c.label} shots — watch the first`}
            className="w-full rounded-t-[4px] bg-you transition-opacity hover:opacity-80 disabled:opacity-25"
            style={{ height: `${(c.rallies.length / max) * 110 + 4}px` }}
          />
          <span className="text-xs text-muted">{c.label}</span>
        </div>
      ))}
    </div>
  );
}

/* ───────────────────────── work rate ───────────────────────── */

export function WorkRate({ match, ids }: { match: Match; ids: PlayerId[] }) {
  const max = Math.max(1, ...ids.map((id) => match.stats[id]?.distanceM ?? 0));
  return (
    <ul className="flex flex-col gap-4">
      {ids.map((id) => {
        const st = match.stats[id];
        const p = match.players.find((x) => x.id === id);
        if (!st) return null;
        const mins = st.activeS / 60;
        return (
          <li key={id} className="flex flex-col gap-1.5">
            <span className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 text-sm font-[600] text-ink">
                <RoleGlyph player={p} />
                {p?.short}
              </span>
              <span className="tabular text-sm text-ink">
                {st.distanceM} m<span className="text-faint"> · {st.steps.toLocaleString()} steps</span>
              </span>
            </span>
            <span
              className="h-3 rounded-sm"
              style={{ width: `${(st.distanceM / max) * 100}%`, background: roleColour(p) }}
            />
            <span className="flex flex-wrap gap-x-4 text-xs text-muted">
              <span>{mins.toFixed(1)} min of play</span>
              <span>{(st.distanceM / Math.max(1, mins)).toFixed(0)} m per minute</span>
              <span>{(st.distanceM / Math.max(1, st.ralliesPlayed)).toFixed(1)} m per rally</span>
            </span>
          </li>
        );
      })}
    </ul>
  );
}

/* ───────────────────────── across matches ───────────────────────── */

export function TrendLine({
  points,
  unit,
  label,
}: {
  points: { date: string; value: number; discipline: string; matchId: string }[];
  unit: string;
  label: string;
}) {
  if (points.length < 2) return <p className="text-sm text-muted">One match so far.</p>;
  const W = 420;
  const H = 120;
  const pad = 20;
  const max = Math.max(...points.map((p) => p.value)) * 1.15;
  const X = (i: number) => pad + (i / (points.length - 1)) * (W - pad * 2);
  const Y = (v: number) => H - pad - (v / Math.max(1, max)) * (H - pad * 2);
  const d = points.map((p, i) => `${i ? "L" : "M"}${X(i)},${Y(p.value)}`).join("");
  return (
    <div className="flex flex-col gap-1">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={`${label} over time`}>
        <line x1={pad} y1={H - pad} x2={W - pad} y2={H - pad} className="stroke-edge" />
        <path d={d} fill="none" className="stroke-you" strokeWidth="2" />
        {points.map((p, i) => (
          <g key={p.matchId}>
            {p.discipline === "doubles" ? (
              <path
                d={`M${X(i)} ${Y(p.value) - 5} L${X(i) + 5} ${Y(p.value)} L${X(i)} ${Y(p.value) + 5} L${X(i) - 5} ${Y(p.value)} Z`}
                className="fill-you"
              />
            ) : (
              <circle cx={X(i)} cy={Y(p.value)} r="4.5" className="fill-you" />
            )}
            <text x={X(i)} y={Y(p.value) - 10} textAnchor="middle" fontSize="11" className="fill-ink tabular">
              {p.value}
            </text>
          </g>
        ))}
      </svg>
      <div className="flex justify-between text-xs text-faint">
        {points.map((p) => (
          <span key={p.matchId}>
            {p.date.slice(8)}/{p.date.slice(5, 7)}
          </span>
        ))}
      </div>
      <p className="text-xs text-muted">
        Measured in {unit}. Circles are singles, diamonds are doubles — they are not the same kind of match,
        so read them separately.
      </p>
    </div>
  );
}

/* ───────────────────────── rally list ───────────────────────── */

export function RallyList({
  match,
  rallies,
  expanded,
  onExpand,
  extra,
}: {
  match: Match;
  rallies: Rally[];
  expanded: number | null;
  onExpand: (n: number | null) => void;
  /** Rendered inside an expanded row — this is where corrections live. */
  extra?: (r: Rally) => ReactNode;
}) {
  const seek = usePlayer((s) => s.seek);
  const playClip = usePlayer((s) => s.playClip);
  const frame = usePlayer((s) => s.frame);
  return (
    <ul className="divide-y divide-edge rounded-[10px] border border-edge">
      {rallies.map((r) => {
        const live = frame >= r.frames[0] && frame <= r.frames[1];
        const open = expanded === r.no;
        const winnerSide = r.winner ? match.sides[r.winner].label : null;
        return (
          <li key={r.no} className={clsx(live && "bg-surface-raised")}>
            <div className="flex flex-wrap items-center gap-3 px-3 py-2">
              <button
                type="button"
                onClick={() => playClip(r.frames[0], r.frames[1], `Rally ${r.no}`)}
                className="tabular w-11 shrink-0 text-left text-xs text-muted hover:text-ink"
                aria-label={`Play rally ${r.no}`}
              >
                {mmss(r.frames[0], match.fps)}
              </button>
              <span className="w-16 shrink-0 text-sm font-[600] text-ink">
                {r.official ? `Rally ${r.no}` : "Warm-up"}
              </span>
              <span className="tabular w-16 shrink-0 text-sm text-muted">{r.shots.length} shots</span>
              <span className="min-w-0 flex-1 truncate text-sm text-muted">
                {winnerSide ? `${winnerSide} — ${r.endReason}` : "not counted"}
              </span>
              {r.pressure && (
                <span className="shrink-0 rounded-full bg-opportunity/12 px-2 py-0.5 text-xs text-opportunity">
                  pressure
                </span>
              )}
              <button
                type="button"
                onClick={() => onExpand(open ? null : r.no)}
                aria-expanded={open}
                className="shrink-0 rounded-[8px] px-2 py-1 text-xs text-muted hover:bg-surface-raised hover:text-ink"
              >
                {open ? "Hide shots" : "Shots"}
              </button>
            </div>
            {open && (
              <div className="flex flex-col gap-2 px-3 pb-3 pl-[7rem]">
                <ol className="flex flex-wrap gap-1.5">
                  {r.shots.map((s) => {
                    const p = match.players.find((x) => x.id === s.player);
                    return (
                      <li key={s.id}>
                        <button
                          type="button"
                          onClick={() =>
                            seek(s.frame, `${STROKE_LABEL[s.subtype ?? s.stroke]} by ${p?.short}`)
                          }
                          className="flex items-center gap-1.5 rounded-full border border-edge px-2.5 py-1 text-xs text-ink hover:border-edge-strong"
                        >
                          <RoleGlyph player={p} className="size-2" />
                          <span className="tabular text-faint">{s.n}</span>
                          {STROKE_LABEL[s.subtype ?? s.stroke]}
                        </button>
                      </li>
                    );
                  })}
                </ol>
                <p className="text-xs text-muted">
                  Served by {match.players.find((p) => p.id === r.server)?.short} · ended because{" "}
                  {r.endReason} · score after: {r.scoreAfter.A}–{r.scoreAfter.B}
                </p>
                {extra?.(r)}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}

export function mmss(frame: number, fps: number) {
  const t = Math.max(0, frame) / fps;
  return `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, "0")}`;
}
