import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Empty, ErrorNote, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { STROKE_LABEL, shortName } from "@/lib/format";
import type { Analytics, PlayerId, PlayerStats, Session } from "@/lib/types";
import { useSession } from "@/stores/session";

export function useAnalytics(sessionId: string) {
  const v = useSession((s) => s.analyticsVersion);
  return useQuery({
    queryKey: ["analytics", sessionId, v],
    queryFn: () => api.analytics(sessionId),
    placeholderData: (prev) => prev,
  });
}

interface Row {
  label: string;
  get: (s: PlayerStats) => number;
  fmt?: (v: number) => string;
}

const ROWS: Row[] = [
  { label: "Points won", get: (s) => s.points_won },
  { label: "Winners", get: (s) => s.winners },
  { label: "Errors (out)", get: (s) => s.errors_out },
  { label: "Errors (net)", get: (s) => s.errors_net },
  { label: "Smashes", get: (s) => s.smashes },
  { label: "Jump smashes", get: (s) => s.jump_smashes },
  { label: "Points won with a smash", get: (s) => s.smash_points },
  { label: "Points won on serve", get: (s) => s.serve_points_won },
  { label: "Points won under pressure", get: (s) => s.points_won_under_pressure },
  { label: "Distance covered", get: (s) => s.distance_m, fmt: (v) => `${Math.round(v)} m` },
];

export function StatsTab({ session }: { session: Session }) {
  const q = useAnalytics(session.session_id);
  if (q.isPending) return <Spinner className="m-6" />;
  if (q.error) return <ErrorNote error={q.error} />;
  const a = q.data;
  if (!a || a.rallies === 0) {
    return <Empty title="No completed rallies yet">Statistics build up as rallies finish.</Empty>;
  }
  const p1 = a.players.P1;
  const p2 = a.players.P2;
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <section aria-labelledby="h2h" className="space-y-3">
        <div className="flex items-baseline justify-between">
          <h3 id="h2h" className="font-semibold">
            Head to head
          </h3>
          <span className="text-xs text-line-3">
            {a.rallies} rallies · {a.avg_rally_shots ?? "—"} shots on average · longest{" "}
            {a.longest_rally_shots}
          </span>
        </div>
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-x-3 text-xs text-line-2">
          <span className="text-right font-medium text-line">{shortName(session, "P1")}</span>
          <span />
          <span className="font-medium text-line">{shortName(session, "P2")}</span>
        </div>
        <table className="w-full text-sm">
          <caption className="sr-only">Statistics per player</caption>
          <tbody>
            {ROWS.map((r) => (
              <H2HRow key={r.label} row={r} a={p1} b={p2} />
            ))}
          </tbody>
        </table>
      </section>
      <section aria-labelledby="mom" className="space-y-3">
        <h3 id="mom" className="font-semibold">
          Momentum
        </h3>
        <Momentum a={a} session={session} />
        <StrokeMix a={a} session={session} />
      </section>
    </div>
  );
}

function H2HRow({ row, a, b }: { row: Row; a?: PlayerStats; b?: PlayerStats }) {
  const va = a ? row.get(a) : 0;
  const vb = b ? row.get(b) : 0;
  const max = Math.max(va, vb, 1e-9);
  const fmt = row.fmt ?? ((v: number) => String(v));
  return (
    <tr className="border-b border-seam/60 last:border-0">
      <td className="tabular w-14 py-1.5 pr-2 text-right">{fmt(va)}</td>
      <td className="w-[30%] py-1.5">
        <div className="flex justify-end">
          <div className="h-2 rounded-l-[4px] bg-p1" style={{ width: `${(va / max) * 100}%` }} />
        </div>
      </td>
      <th scope="row" className="px-3 py-1.5 text-center text-xs font-normal whitespace-nowrap text-line-2">
        {row.label}
      </th>
      <td className="w-[30%] py-1.5">
        <div className="h-2 rounded-r-[4px] bg-p2" style={{ width: `${(vb / max) * 100}%` }} />
      </td>
      <td className="tabular w-14 py-1.5 pl-2">{fmt(vb)}</td>
    </tr>
  );
}

/** Momentum (EWMA of point winners): above the axis favours P1, below favours P2. */
function Momentum({ a, session }: { a: Analytics; session: Session }) {
  const [hover, setHover] = useState<number | null>(null);
  const pts = a.momentum;
  if (pts.length < 2) return <p className="text-sm text-line-3">Momentum needs a few more points.</p>;
  const W = 520;
  const H = 140;
  const pad = { l: 8, r: 8, t: 10, b: 18 };
  const X = (i: number) => pad.l + (i / (pts.length - 1)) * (W - pad.l - pad.r);
  const Y = (v: number) => pad.t + ((1 - v) / 2) * (H - pad.t - pad.b);
  const line = pts.map((p, i) => `${i ? "L" : "M"}${X(i).toFixed(1)},${Y(p.value).toFixed(1)}`).join("");
  const area = `${line}L${X(pts.length - 1)},${Y(0)}L${X(0)},${Y(0)}Z`;
  const hp = hover != null ? pts[hover] : undefined;
  const score = hp ? a.score_timeline.find((s) => s.rally_no === hp.rally_no) : undefined;
  const shifts = new Set(a.momentum_shifts.map((s) => s.rally_no));

  return (
    <div className="relative">
      <div className="mb-1 flex gap-4 text-xs text-line-2">
        <span className="flex items-center gap-1.5">
          <span className="size-2 rounded-sm bg-p1" aria-hidden /> {shortName(session, "P1")} ahead
        </span>
        <span className="flex items-center gap-1.5">
          <span className="size-2 rounded-sm bg-p2" aria-hidden /> {shortName(session, "P2")} ahead
        </span>
        <span className="flex items-center gap-1.5">
          <span className="size-2 rounded-full border border-line" aria-hidden /> momentum shift
        </span>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label="Momentum over the last points"
        onMouseMove={(e) => {
          const r = e.currentTarget.getBoundingClientRect();
          const fx = ((e.clientX - r.left) / r.width) * W;
          const i = Math.round(((fx - pad.l) / (W - pad.l - pad.r)) * (pts.length - 1));
          setHover(Math.max(0, Math.min(pts.length - 1, i)));
        }}
        onMouseLeave={() => setHover(null)}
      >
        <defs>
          <clipPath id="mom-above">
            <rect x={0} y={0} width={W} height={Y(0)} />
          </clipPath>
          <clipPath id="mom-below">
            <rect x={0} y={Y(0)} width={W} height={H} />
          </clipPath>
        </defs>
        {[-1, -0.5, 0.5, 1].map((v) => (
          <line
            key={v}
            x1={pad.l}
            x2={W - pad.r}
            y1={Y(v)}
            y2={Y(v)}
            stroke="var(--color-seam)"
            strokeWidth={1}
          />
        ))}
        <path d={area} fill="var(--color-p1)" fillOpacity={0.25} clipPath="url(#mom-above)" />
        <path d={area} fill="var(--color-p2)" fillOpacity={0.25} clipPath="url(#mom-below)" />
        <path d={line} fill="none" stroke="var(--color-p1)" strokeWidth={2} clipPath="url(#mom-above)" />
        <path d={line} fill="none" stroke="var(--color-p2)" strokeWidth={2} clipPath="url(#mom-below)" />
        <line x1={pad.l} x2={W - pad.r} y1={Y(0)} y2={Y(0)} stroke="var(--color-line-3)" strokeWidth={1} />
        {pts.map((p, i) =>
          shifts.has(p.rally_no) ? (
            <circle
              key={p.rally_no}
              cx={X(i)}
              cy={Y(p.value)}
              r={4}
              fill="var(--color-stand)"
              stroke="var(--color-line)"
              strokeWidth={2}
            />
          ) : null,
        )}
        {hp && hover != null && (
          <g>
            <line
              x1={X(hover)}
              x2={X(hover)}
              y1={pad.t}
              y2={H - pad.b}
              stroke="var(--color-line-2)"
              strokeWidth={1}
            />
            <circle
              cx={X(hover)}
              cy={Y(hp.value)}
              r={4}
              fill="var(--color-line)"
              stroke="var(--color-stand)"
              strokeWidth={2}
            />
          </g>
        )}
        <text x={pad.l} y={H - 4} fill="var(--color-line-3)" fontSize={10}>
          rally {pts[0]?.rally_no}
        </text>
        <text x={W - pad.r} y={H - 4} fill="var(--color-line-3)" fontSize={10} textAnchor="end">
          rally {pts[pts.length - 1]?.rally_no}
        </text>
      </svg>
      {hp && hover != null && (
        <div
          className="pointer-events-none absolute top-6 z-10 -translate-x-1/2 rounded-md border border-seam bg-stand px-2 py-1 text-xs shadow-lg"
          style={{ left: `${(X(hover) / W) * 100}%` }}
        >
          <p className="font-medium">Rally {hp.rally_no}</p>
          {score && (
            <p className="tabular text-line-2">
              Game {score.game_no} · {score.score.P1}–{score.score.P2} · point{" "}
              {shortName(session, score.winner)}
            </p>
          )}
          {hp.run.length > 1 && (
            <p className="text-line-2">
              {shortName(session, hp.run.player)} on a run of {hp.run.length}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function StrokeMix({ a, session }: { a: Analytics; session: Session }) {
  const kinds = new Set<string>();
  for (const pid of ["P1", "P2"] as PlayerId[])
    for (const k of Object.keys(a.players[pid]?.strokes ?? {})) if (k !== "unknown") kinds.add(k);
  const list = [...kinds].sort(
    (x, y) =>
      (a.players.P1?.strokes[y] ?? 0) +
      (a.players.P2?.strokes[y] ?? 0) -
      ((a.players.P1?.strokes[x] ?? 0) + (a.players.P2?.strokes[x] ?? 0)),
  );
  if (!list.length) return null;
  const max = Math.max(
    1,
    ...list.flatMap((k) => [a.players.P1?.strokes[k] ?? 0, a.players.P2?.strokes[k] ?? 0]),
  );
  return (
    <div className="space-y-2 pt-2">
      <h4 className="text-sm font-medium">Shot mix</h4>
      <table className="w-full text-xs">
        <caption className="sr-only">Shots played per player by type</caption>
        <thead className="sr-only">
          <tr>
            <th>Shot</th>
            <th>{shortName(session, "P1")}</th>
            <th>{shortName(session, "P2")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((k) => {
            const v1 = a.players.P1?.strokes[k] ?? 0;
            const v2 = a.players.P2?.strokes[k] ?? 0;
            return (
              <tr key={k}>
                <th scope="row" className="w-28 py-0.5 pr-2 text-left font-normal text-line-2">
                  {STROKE_LABEL[k] ?? k}
                </th>
                <td className="py-0.5">
                  <div className="flex flex-col gap-[2px]">
                    <Bar v={v1} max={max} color="var(--color-p1)" />
                    <Bar v={v2} max={max} color="var(--color-p2)" />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Bar({ v, max, color }: { v: number; max: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-1.5 rounded-r-[4px]"
        style={{ width: `${(v / max) * 85}%`, background: color, minWidth: v ? 2 : 0 }}
      />
      <span className="tabular text-line-2">{v}</span>
    </div>
  );
}
