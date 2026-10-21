import { useQuery } from "@tanstack/react-query";
import { Film } from "lucide-react";

interface SpriteMeta {
  interval_s: number;
  tile: number;
  thumb_w: number;
  thumb_h: number;
  count: number;
  sheets: string[];
}

export function useSprite(sessionId: string, enabled = true) {
  return useQuery({
    queryKey: ["sprite", sessionId],
    enabled,
    // sprites are built after the proxy finishes: keep asking until they exist, then cache for good
    staleTime: (q) => (q.state.data ? Number.POSITIVE_INFINITY : 0),
    refetchInterval: (q) => (q.state.data ? false : 5000),
    queryFn: async (): Promise<SpriteMeta | null> => {
      const r = await fetch(`/api/sessions/${sessionId}/sprite/sprite.json`, { credentials: "same-origin" });
      return r.ok ? ((await r.json()) as SpriteMeta) : null;
    },
  });
}

/** CSS for one thumbnail cell of the sprite sheets, at media time `t` seconds. */
export function spriteStyle(sessionId: string, m: SpriteMeta, t: number): React.CSSProperties | null {
  if (!m.count || !m.sheets.length) return null;
  const idx = Math.max(0, Math.min(m.count - 1, Math.floor(t / m.interval_s)));
  const perSheet = m.tile * m.tile;
  const sheet = m.sheets[Math.floor(idx / perSheet)];
  if (!sheet) return null;
  const cell = idx % perSheet;
  const col = cell % m.tile;
  const row = Math.floor(cell / m.tile);
  return {
    backgroundImage: `url(/api/sessions/${sessionId}/sprite/${sheet})`,
    backgroundSize: `${m.tile * 100}% ${m.tile * 100}%`,
    backgroundPosition: `${(col / (m.tile - 1)) * 100}% ${(row / (m.tile - 1)) * 100}%`,
  };
}

/** Poster for a session card: a frame ~a third of the way in (past intros and warm-ups). */
export function Thumb({
  sessionId,
  durationS,
  ready,
}: {
  sessionId: string;
  durationS: number;
  ready: boolean;
}) {
  const sprite = useSprite(sessionId, ready);
  const style = sprite.data ? spriteStyle(sessionId, sprite.data, durationS * 0.35) : null;
  return (
    <div
      className="relative aspect-video overflow-hidden rounded-t-[13px] bg-mat-deep"
      style={style ?? undefined}
    >
      {!style && (
        <div className="absolute inset-0 grid place-items-center text-line-3">
          <Film className="size-6" aria-hidden />
        </div>
      )}
    </div>
  );
}
