import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";
import { useEffect, useMemo, useRef, useState } from "react";
import { Empty, ErrorNote } from "@/components/ui";
import { CourtView, prepareCanvas } from "@/features/court/geometry";
import { api } from "@/lib/api";
import { PLAYER_HEX, shortName } from "@/lib/format";
import type { Heatmap, PlayerId, Session } from "@/lib/types";
import { useSession } from "@/stores/session";

const KINDS: { id: string; label: string; hint: string }[] = [
  { id: "presence", label: "Where they stand", hint: "Time spent in each part of the court during rallies" },
  { id: "movement", label: "Movement", hint: "Distance covered, by area" },
  { id: "origin", label: "Where they hit from", hint: "Position at each shot" },
  {
    id: "landing",
    label: "Where their shots go",
    hint: "Where the opponent played each shot back (or it landed)",
  },
  { id: "targeting", label: "Targeting", hint: "Areas of the opponent's court this player attacks" },
];

export function HeatmapsTab({ session }: { session: Session }) {
  const [kind, setKind] = useState("presence");
  const v = useSession((s) => s.analyticsVersion);
  const calibrated = useSession((s) => s.calibration != null);
  if (!calibrated) {
    return (
      <Empty title="Heatmaps need the court">
        Calibrate the court so positions can be measured in metres on the floor.
      </Empty>
    );
  }
  const k = KINDS.find((x) => x.id === kind) ?? KINDS[0];
  return (
    <div className="space-y-4">
      <fieldset className="flex flex-wrap items-center gap-2">
        <legend className="sr-only">Heatmap type</legend>
        {KINDS.map((x) => (
          <button
            key={x.id}
            type="button"
            aria-pressed={kind === x.id}
            onClick={() => setKind(x.id)}
            className={clsx(
              "h-8 rounded-full border px-3 text-sm transition-colors",
              kind === x.id ? "border-line bg-line text-mat-deep" : "border-seam text-line-2 hover:text-line",
            )}
          >
            {x.label}
          </button>
        ))}
      </fieldset>
      <p className="text-sm text-line-2">{k?.hint}</p>
      <div className="grid gap-4 lg:grid-cols-2">
        {(["P1", "P2"] as PlayerId[]).map((pid) => (
          <HeatmapCard key={pid} session={session} pid={pid} kind={kind} version={v} />
        ))}
      </div>
    </div>
  );
}

function HeatmapCard({
  session,
  pid,
  kind,
  version,
}: {
  session: Session;
  pid: PlayerId;
  kind: string;
  version: number;
}) {
  const q = useQuery({
    queryKey: ["heatmap", session.session_id, pid, kind, version],
    queryFn: () => api.heatmap(session.session_id, pid, kind),
    placeholderData: (p) => p,
  });
  return (
    <figure className="space-y-2">
      <figcaption className="flex items-center gap-2 text-sm font-medium">
        <span className="size-2 rounded-full" style={{ background: PLAYER_HEX[pid] }} aria-hidden />
        {shortName(session, pid)}
        {q.data && (
          <span className="text-xs font-normal text-line-3">{Math.round(q.data.total)} samples</span>
        )}
      </figcaption>
      <ErrorNote error={q.error} />
      {q.data && <HeatCanvas h={q.data} color={PLAYER_HEX[pid]} />}
      <div className="flex items-center gap-2 text-[11px] text-line-3">
        less
        <span
          className="h-2 w-24 rounded-full"
          style={{ background: `linear-gradient(90deg, transparent, ${PLAYER_HEX[pid]})` }}
          aria-hidden
        />
        more
      </div>
    </figure>
  );
}

/** Sequential single-hue ramp (the player's colour), drawn over the top-down court. */
function HeatCanvas({ h, color }: { h: Heatmap; color: string }) {
  const wrap = useRef<HTMLDivElement>(null);
  const ref = useRef<HTMLCanvasElement>(null);
  const [width, setWidth] = useState(420);
  const [tip, setTip] = useState<string | null>(null);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setWidth(Math.max(220, Math.floor(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const view = useMemo(() => new CourtView(width), [width]);
  useEffect(() => {
    const c = ref.current;
    if (!c) return;
    const g = prepareCanvas(c, view.width, view.height);
    if (!g) return;
    view.drawCourt(g, { floor: "#123128" });
    const [ny, nx] = h.shape;
    const [ox, oy] = h.origin_m;
    const cs = h.cell_m;
    for (let j = 0; j < ny; j++) {
      const row = h.values[j];
      if (!row) continue;
      for (let i = 0; i < nx; i++) {
        const v = row[i] ?? 0;
        if (v <= 0.02) continue;
        // cell (i: across x, j: along y) → screen rect
        const [sx0, sy0] = view.map(ox + i * cs, oy + j * cs);
        const [sx1, sy1] = view.map(ox + (i + 1) * cs, oy + (j + 1) * cs);
        g.fillStyle = color;
        g.globalAlpha = 0.12 + 0.78 * Math.sqrt(v);
        g.fillRect(
          Math.min(sx0, sx1),
          Math.min(sy0, sy1),
          Math.abs(sx1 - sx0) + 0.5,
          Math.abs(sy1 - sy0) + 0.5,
        );
      }
    }
    g.globalAlpha = 1;
    // court lines on top so the heat never hides them
    view.drawCourt(g, { floor: "transparent", lines: "rgba(232,239,234,0.5)" });
  }, [h, color, view]);

  return (
    <div ref={wrap} className="relative">
      <canvas
        ref={ref}
        style={{ width: view.width, height: view.height }}
        className="block rounded-lg bg-mat-deep"
        role="img"
        aria-label={`${h.kind} heatmap`}
        onMouseMove={(e) => {
          const r = e.currentTarget.getBoundingClientRect();
          const px = e.clientX - r.left;
          const py = e.clientY - r.top;
          const [x, y] = view.unmap(px, py);
          const i = Math.floor((x - h.origin_m[0]) / h.cell_m);
          const j = Math.floor((y - h.origin_m[1]) / h.cell_m);
          const v = h.values[j]?.[i];
          setTip(v != null ? `${Math.round(v * 100)}% of the busiest area` : null);
        }}
        onMouseLeave={() => setTip(null)}
      />
      {tip && (
        <p className="absolute top-2 right-2 rounded bg-mat-deep/90 px-2 py-0.5 text-xs text-line-2">{tip}</p>
      )}
    </div>
  );
}
