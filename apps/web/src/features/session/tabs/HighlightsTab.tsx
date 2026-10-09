import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Download, Play } from "lucide-react";
import { useState } from "react";
import { Empty, ErrorNote, PlayerDot, Spinner } from "@/components/ui";
import { api, exportUrl } from "@/lib/api";
import { CATEGORY_LABEL, clock, fps as fpsOf, shortName } from "@/lib/format";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

const REASON_LABEL: Record<string, string> = {
  length: "long rally",
  smash_winner: "smash winner",
  jump_smash: "jump smash",
  defence: "defence",
  net_play: "net play",
  variety: "shot variety",
  pressure: "pressure point",
  momentum: "momentum shift",
  comeback: "comeback",
  deuce: "deuce",
};

export function HighlightsTab({ session }: { session: Session }) {
  const [player, setPlayer] = useState<PlayerId | undefined>();
  const v = useSession((s) => s.analyticsVersion);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const video = usePlayback((s) => s.video);
  const fps = fpsOf(session.media);
  const q = useQuery({
    queryKey: ["highlights", session.session_id, player, v],
    queryFn: () => api.highlights(session.session_id, 12, player),
    placeholderData: (p) => p,
  });

  return (
    <div className="space-y-4">
      <fieldset className="flex items-center gap-2">
        <legend className="sr-only">Whose highlights</legend>
        {([undefined, "P1", "P2"] as (PlayerId | undefined)[]).map((p) => (
          <button
            key={p ?? "all"}
            type="button"
            aria-pressed={player === p}
            onClick={() => setPlayer(p)}
            className={clsx(
              "flex h-8 items-center gap-2 rounded-full border px-3 text-sm transition-colors",
              player === p ? "border-line bg-line text-mat-deep" : "border-seam text-line-2 hover:text-line",
            )}
          >
            {p && <PlayerDot pid={p} />}
            {p ? shortName(session, p) : "Both players"}
          </button>
        ))}
        <span className="ml-auto text-xs text-line-3">Ranked by excitement, kept varied</span>
      </fieldset>
      {q.isPending && <Spinner />}
      <ErrorNote error={q.error} />
      {q.data?.highlights.length === 0 && (
        <Empty title="No highlights yet">The best rallies are picked as soon as they finish.</Empty>
      )}
      <ol className="grid gap-2 md:grid-cols-2">
        {q.data?.highlights.map((h, i) => (
          <li key={h.rally_id} className="panel flex items-start gap-3 p-3">
            <span className="numerals w-6 pt-0.5 text-lg text-line-3">{i + 1}</span>
            <div className="min-w-0 flex-1 space-y-1.5">
              <div className="flex flex-wrap items-center gap-1.5">
                {h.categories.map((c) => (
                  <span key={c} className="rounded-full bg-line/10 px-2 py-0.5 text-xs font-medium">
                    {CATEGORY_LABEL[c] ?? c}
                  </span>
                ))}
              </div>
              <p className="text-sm text-line-2">
                Rally {h.rally_no} · {clock(h.frame_start, session.media)}
                {h.player && (
                  <>
                    {" · "}
                    <PlayerDot pid={h.player} className="mx-0.5 align-middle" />{" "}
                    {shortName(session, h.player)}
                  </>
                )}
              </p>
              <p className="text-xs text-line-3">
                Why:{" "}
                {Object.entries(h.reasons)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 3)
                  .map(([k]) => REASON_LABEL[k] ?? k.replace(/_/g, " "))
                  .join(", ")}
              </p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="numerals text-lg">{h.score.toFixed(1)}</span>
              <div className="flex gap-1">
                <button
                  type="button"
                  aria-label={`Play rally ${h.rally_no}`}
                  className="grid size-8 place-items-center rounded-lg bg-line text-mat-deep hover:bg-white"
                  onClick={() => {
                    seekFrame(Math.max(0, h.frame_start - Math.round(fps)), fps);
                    void video?.play().catch(() => {});
                  }}
                >
                  <Play className="size-4" />
                </button>
                <a
                  aria-label={`Download rally ${h.rally_no} as a clip`}
                  href={`${exportUrl(session.session_id, "clip.mp4")}?from=${h.frame_start}&to=${h.frame_end}`}
                  className="grid size-8 place-items-center rounded-lg border border-seam text-line-2 hover:text-line"
                  download
                >
                  <Download className="size-4" />
                </a>
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
