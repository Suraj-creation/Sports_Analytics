import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "@tanstack/react-router";
import { clsx } from "clsx";
import { ArrowLeft, Check, ChevronLeft, ChevronRight, RotateCcw, Sparkles, Undo2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { Button, ErrorNote, Spinner } from "@/components/ui";
import { useHls } from "@/features/player/useHls";
import { api } from "@/lib/api";
import { COURT_LINES, NET, project } from "@/lib/court";
import { fps as fpsOf } from "@/lib/format";
import { fitHomography, reprojectionError } from "@/lib/homography";

type P = [number, number];

/** Points in the order we ask for them. The first six define the court; the rest refine it. */
const ORDER: { id: string; label: string; required?: boolean }[] = [
  { id: "near_left", label: "Near left corner", required: true },
  { id: "near_right", label: "Near right corner", required: true },
  { id: "far_right", label: "Far right corner", required: true },
  { id: "far_left", label: "Far left corner", required: true },
  { id: "net_left", label: "Net post, left — where it meets the floor" },
  { id: "net_right", label: "Net post, right — where it meets the floor" },
  { id: "near_short_left", label: "Near short service line, left end" },
  { id: "near_short_right", label: "Near short service line, right end" },
  { id: "far_short_left", label: "Far short service line, left end" },
  { id: "far_short_right", label: "Far short service line, right end" },
];
const LOUPE = 132;
const ZOOM = 3;

export function CalibratePage() {
  const { sessionId } = useParams({ from: "/sessions/$sessionId/calibrate" });
  const navigate = useNavigate();
  const qc = useQueryClient();
  const session = useQuery({ queryKey: ["session", sessionId], queryFn: () => api.session(sessionId) });
  const [segment, setSegment] = useState(0);
  const prop = useQuery({
    queryKey: ["calibration-proposal", sessionId, segment],
    queryFn: () => api.calibrationProposal(sessionId, segment),
    enabled: session.data?.media != null,
  });

  const [video, setVideo] = useState<HTMLVideoElement | null>(null);
  const hls = useHls(video, sessionId, session.data?.media != null);
  const fps = fpsOf(session.data?.media);
  const [points, setPoints] = useState<Record<string, P>>({});
  const [history, setHistory] = useState<Record<string, P>[]>([]);
  const [active, setActive] = useState<string>("near_left");
  const [drag, setDrag] = useState<string | null>(null);
  const [cursor, setCursor] = useState<{ x: number; y: number; px: number; py: number } | null>(null);
  const boxRef = useRef<HTMLDivElement>(null);
  const loupeRef = useRef<HTMLCanvasElement>(null);
  const seeded = useRef(false);

  const W = prop.data?.width ?? session.data?.media?.width ?? 1280;
  const H = prop.data?.height ?? session.data?.media?.height ?? 720;
  const ref = prop.data?.reference_points ?? {};

  // show the proposal's frame, paused
  useEffect(() => {
    if (!video || hls !== "ready" || !prop.data) return;
    video.pause();
    video.currentTime = (prop.data.frame + 0.5) / fps;
  }, [video, hls, prop.data, fps]);

  // seed from the existing calibration, else the automatic proposal (once)
  useEffect(() => {
    if (seeded.current || !prop.data) return;
    seeded.current = true;
    const cur = prop.data.current?.H;
    if (cur) {
      const pts: Record<string, P> = {};
      for (const o of ORDER.slice(0, 6)) {
        const c = prop.data.reference_points[o.id];
        if (c) pts[o.id] = project(cur, c);
      }
      setPoints(pts);
    } else if (prop.data.proposal) {
      setPoints(prop.data.proposal.points);
    }
  }, [prop.data]);

  const fit = useMemo(() => {
    const ids = Object.keys(points).filter((k) => ref[k]);
    if (ids.length < 4) return null;
    const court = ids.map((k) => ref[k] as P);
    const img = ids.map((k) => points[k] as P);
    const Hm = fitHomography(court, img);
    return Hm ? { H: Hm, err: reprojectionError(Hm, court, img), n: ids.length } : null;
  }, [points, ref]);

  const save = useMutation({
    mutationFn: () => api.calibrate(sessionId, points),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["session", sessionId] });
      navigate({ to: "/sessions/$sessionId", params: { sessionId } });
    },
  });

  const toImage = (clientX: number, clientY: number): P | null => {
    const el = boxRef.current;
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return [((clientX - r.left) / r.width) * W, ((clientY - r.top) / r.height) * H];
  };
  const commit = (next: Record<string, P>) => {
    setHistory((h) => [...h.slice(-30), points]);
    setPoints(next);
  };
  const nextMissing = (after: Record<string, P>) => ORDER.find((o) => !after[o.id])?.id ?? active;

  // magnifier: draw the frame region around the cursor at 3×
  useEffect(() => {
    const c = loupeRef.current;
    if (!c || !video || !cursor) return;
    const dpr = window.devicePixelRatio || 1;
    c.width = LOUPE * dpr;
    c.height = LOUPE * dpr;
    const g = c.getContext("2d");
    if (!g) return;
    const src = LOUPE / ZOOM;
    const sx = (cursor.x / W) * video.videoWidth - src / 2;
    const sy = (cursor.y / H) * video.videoHeight - src / 2;
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    try {
      g.drawImage(video, sx, sy, src, src, 0, 0, LOUPE, LOUPE);
    } catch {
      /* frame not decoded yet */
    }
    g.strokeStyle = "#3ddc97";
    g.lineWidth = 1;
    g.beginPath();
    g.moveTo(LOUPE / 2, 0);
    g.lineTo(LOUPE / 2, LOUPE);
    g.moveTo(0, LOUPE / 2);
    g.lineTo(LOUPE, LOUPE / 2);
    g.stroke();
  }, [cursor, video, W, H]);

  if (session.isPending) return <Spinner className="m-10" />;
  if (session.error) return <ErrorNote error={session.error} />;
  const s = session.data;
  const nSeg = s?.media ? Math.ceil(s.media.n_frames / Number(s.meta.frames_per_segment ?? 60)) : 1;
  const stroke = 1.5 * (W / 1000);

  return (
    <div className="mx-auto max-w-[1500px] space-y-4 px-4 py-4 sm:px-6">
      <div className="flex flex-wrap items-center gap-3">
        <Link
          to="/sessions/$sessionId"
          params={{ sessionId }}
          aria-label="Back to the match"
          className="grid size-9 place-items-center rounded-lg text-line-2 hover:bg-stand-raised hover:text-line"
        >
          <ArrowLeft className="size-5" />
        </Link>
        <div>
          <h1 className="text-lg font-semibold">Calibrate the court</h1>
          <p className="text-sm text-line-2">
            Click each point on the floor where the lines meet. Drag a point to adjust it.
          </p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-2">
          <div
            ref={boxRef}
            className="relative w-full cursor-crosshair touch-none overflow-hidden rounded-[var(--radius-card)] border border-seam bg-black select-none"
            style={{ aspectRatio: `${W} / ${H}` }}
            onPointerMove={(e) => {
              const p = toImage(e.clientX, e.clientY);
              if (!p) return;
              const r = (e.currentTarget as HTMLElement).getBoundingClientRect();
              setCursor({ x: p[0], y: p[1], px: e.clientX - r.left, py: e.clientY - r.top });
              if (drag) setPoints((cur) => ({ ...cur, [drag]: p }));
            }}
            onPointerLeave={() => setCursor(null)}
            onPointerUp={() => setDrag(null)}
            onPointerDown={(e) => {
              if (drag) return;
              const p = toImage(e.clientX, e.clientY);
              if (!p) return;
              const next = { ...points, [active]: p };
              commit(next);
              setActive(nextMissing(next));
            }}
          >
            <video ref={setVideo} className="absolute inset-0 size-full" muted playsInline preload="auto" />
            {(hls !== "ready" || prop.isPending) && (
              <div className="absolute inset-0 grid place-items-center bg-mat-deep/80">
                <Spinner className="size-6" />
              </div>
            )}
            <svg viewBox={`0 0 ${W} ${H}`} className="absolute inset-0 size-full" aria-hidden>
              {fit && (
                <g stroke="#3ddc97" strokeWidth={stroke} fill="none" opacity={0.9}>
                  {COURT_LINES.map(([a, b], i) => {
                    const pa = project(fit.H, a);
                    const pb = project(fit.H, b);
                    // biome-ignore lint/suspicious/noArrayIndexKey: fixed line list
                    return <line key={i} x1={pa[0]} y1={pa[1]} x2={pb[0]} y2={pb[1]} />;
                  })}
                  {(() => {
                    const a = project(fit.H, NET[0]);
                    const b = project(fit.H, NET[1]);
                    return (
                      <line
                        x1={a[0]}
                        y1={a[1]}
                        x2={b[0]}
                        y2={b[1]}
                        strokeDasharray={`${stroke * 4} ${stroke * 3}`}
                      />
                    );
                  })()}
                </g>
              )}
              {Object.entries(points).map(([id, [x, y]]) => (
                <g
                  key={id}
                  className="cursor-grab"
                  onPointerDown={(e) => {
                    e.stopPropagation();
                    setHistory((h) => [...h.slice(-30), points]);
                    setDrag(id);
                    setActive(id);
                  }}
                >
                  <circle cx={x} cy={y} r={14 * (W / 1000)} fill="transparent" />
                  <circle
                    cx={x}
                    cy={y}
                    r={5 * (W / 1000)}
                    fill={id === active ? "#3ddc97" : "#ffffff"}
                    stroke="#0c2620"
                    strokeWidth={stroke}
                  />
                </g>
              ))}
            </svg>
            {cursor && (
              <canvas
                ref={loupeRef}
                className="pointer-events-none absolute rounded-full border-2 border-signal shadow-xl"
                style={{
                  width: LOUPE,
                  height: LOUPE,
                  left: cursor.px + 20,
                  top: cursor.py - LOUPE - 20 < 0 ? cursor.py + 20 : cursor.py - LOUPE - 20,
                }}
              />
            )}
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Button
              size="sm"
              variant="ghost"
              disabled={segment <= 0}
              onClick={() => setSegment((x) => Math.max(0, x - 10))}
            >
              <ChevronLeft className="size-4" /> Earlier frame
            </Button>
            <Button
              size="sm"
              variant="ghost"
              disabled={segment >= nSeg - 1}
              onClick={() => setSegment((x) => Math.min(nSeg - 1, x + 10))}
            >
              Later frame <ChevronRight className="size-4" />
            </Button>
            <span className="text-xs text-line-3">
              Pick a frame where the whole court is visible and no one blocks a corner.
            </span>
          </div>
        </div>

        <aside className="panel flex flex-col gap-4 p-4">
          <ol className="space-y-1">
            {ORDER.map((o, i) => (
              <li key={o.id}>
                <button
                  type="button"
                  onClick={() => setActive(o.id)}
                  className={clsx(
                    "flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-left text-sm",
                    active === o.id ? "bg-stand-raised text-line" : "text-line-2 hover:bg-stand-raised/60",
                  )}
                >
                  <span
                    className={clsx(
                      "grid size-5 shrink-0 place-items-center rounded-full text-[11px] font-semibold",
                      points[o.id] ? "bg-signal text-mat-deep" : "border border-seam text-line-3",
                    )}
                  >
                    {points[o.id] ? <Check className="size-3" /> : i + 1}
                  </span>
                  <span className="flex-1">{o.label}</span>
                  {!o.required && <span className="text-xs text-line-3">optional</span>}
                </button>
              </li>
            ))}
          </ol>
          <div className="flex flex-wrap gap-2">
            <Button
              size="sm"
              variant="ghost"
              disabled={!history.length}
              onClick={() => {
                const prev = history[history.length - 1];
                if (prev) {
                  setPoints(prev);
                  setHistory((h) => h.slice(0, -1));
                }
              }}
            >
              <Undo2 className="size-4" /> Undo
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => commit({})}
              disabled={!Object.keys(points).length}
            >
              <RotateCcw className="size-4" /> Clear
            </Button>
            {prop.data?.proposal && (
              <Button size="sm" variant="ghost" onClick={() => commit(prop.data?.proposal?.points ?? {})}>
                <Sparkles className="size-4" /> Use detected
              </Button>
            )}
          </div>
          <div className="mt-auto space-y-3 border-t border-seam pt-4">
            {prop.data?.proposal && (
              <p className="text-xs text-line-3">
                Automatic detection confidence: {Math.round(prop.data.proposal.score * 100)}%
              </p>
            )}
            {fit ? (
              <p className={clsx("text-sm", fit.err > 8 ? "text-caution" : "text-line-2")}>
                Fit error {fit.err.toFixed(1)} px from {fit.n} points
                {fit.err > 8 && " — a point is probably off; check the green lines against the court"}
              </p>
            ) : (
              <p className="text-sm text-line-3">Place the four corners to preview the court.</p>
            )}
            <ErrorNote error={save.error} />
            <Button
              variant="primary"
              className="w-full"
              disabled={!fit}
              busy={save.isPending}
              onClick={() => save.mutate()}
            >
              Save calibration
            </Button>
            <p className="text-xs text-line-3">
              Saving applies from where the analysis has reached. To re-measure the whole match with it,
              choose “Analyse again” on the match page.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
