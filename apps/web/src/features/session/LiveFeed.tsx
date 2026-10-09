import { clsx } from "clsx";
import { Flag, Sparkles, Trophy, Zap } from "lucide-react";
import { useMemo } from "react";
import { BandChip, Empty, PlayerDot } from "@/components/ui";
import {
  CATEGORY_LABEL,
  clock,
  fps as fpsOf,
  OUTCOME_LABEL,
  playerColor,
  shortName,
  strokeLabel,
} from "@/lib/format";
import type { BaiEvent, PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

const TYPES = ["rally_end", "stroke", "highlight", "game_end", "match_end", "interval", "side_switch"];
const LIMIT = 60;

/** What has happened up to the playhead, newest first. Nothing after the playhead is shown. */
export function LiveFeed({ session }: { session: Session }) {
  const frame = usePlayback((s) => s.frame);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const fps = fpsOf(session.media);
  // recompute twice a second of video, not every UI tick
  const bucket = Math.floor(frame / Math.max(1, Math.round(fps / 2)));

  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation; bucket throttles
  const items = useMemo(() => {
    const out: BaiEvent[] = [];
    for (const e of events.ofType(...TYPES)) {
      const at = e.type === "rally_end" ? e.frame_end : e.frame_start;
      if (at > frame) continue;
      // the feed lists notable shots only; every shot is on the timeline
      if (e.type === "stroke" && e.payload.stroke !== "smash") continue;
      out.push(e);
    }
    return out.sort((a, b) => feedFrame(b) - feedFrame(a)).slice(0, LIMIT);
  }, [events, eventsVersion, bucket]);

  if (!items.length) {
    return (
      <Empty title="Nothing yet">
        Rallies, smashes and game events appear here as the video reaches them.
      </Empty>
    );
  }
  return (
    <ol className="space-y-1" aria-label="Match events">
      {items.map((e) => (
        <li key={e.event_id}>
          <button
            type="button"
            onClick={() => seekFrame(Math.max(0, e.frame_start - Math.round(fps)), fps)}
            className={clsx(
              "flex w-full items-start gap-3 rounded-lg px-2.5 py-2 text-left transition-colors hover:bg-stand-raised",
              events.recentlyCorrected.has(e.event_id) && "animate-[corrected_900ms_ease-out]",
            )}
          >
            <span className="tabular w-11 shrink-0 pt-px text-xs text-line-3">
              {clock(feedFrame(e), session.media)}
            </span>
            <FeedItem e={e} session={session} />
          </button>
        </li>
      ))}
    </ol>
  );
}

const feedFrame = (e: BaiEvent) => (e.type === "rally_end" ? e.frame_end : e.frame_start);

function FeedItem({ e, session }: { e: BaiEvent; session: Session }) {
  const pid = e.actors.player_id as PlayerId | null;
  const corrected = e.status === "corrected" || e.status === "human_verified";
  switch (e.type) {
    case "rally_end": {
      const w = e.payload.winner as PlayerId | null;
      const outcome = e.payload.outcome as string | undefined;
      return (
        <span className="min-w-0 flex-1 text-sm">
          <span className="flex items-center gap-2">
            <PlayerDot pid={w} />
            <span className="font-medium">
              Rally {e.payload.rally_no} · {w ? `${shortName(session, w)} wins` : "winner unclear"}
            </span>
            {corrected && <span className="text-xs text-signal">corrected</span>}
          </span>
          <span className="block text-xs text-line-2">
            {e.payload.n_shots ?? 0} shots
            {outcome && ` · shuttle ${OUTCOME_LABEL[outcome] ?? outcome}`}
            {e.band !== "confirmed" && ` · ${e.band}`}
          </span>
        </span>
      );
    }
    case "stroke":
      return (
        <span className="flex min-w-0 flex-1 items-center gap-2 text-sm">
          <Zap className="size-3.5 shrink-0" style={{ color: playerColor(pid) }} aria-hidden />
          <BandChip band={e.band} color={playerColor(pid)}>
            {strokeLabel(e.payload)}
          </BandChip>
          <span className="truncate text-line-2">{shortName(session, pid)}</span>
        </span>
      );
    case "highlight": {
      const cats = (e.payload.categories as string[] | undefined) ?? [];
      return (
        <span className="flex min-w-0 flex-1 items-center gap-2 text-sm">
          <Sparkles className="size-3.5 shrink-0 text-line" aria-hidden />
          <span className="truncate">
            {cats.map((c) => CATEGORY_LABEL[c] ?? c).join(" · ") || "Highlight"}
          </span>
        </span>
      );
    }
    case "game_end":
    case "match_end": {
      const w = (e.payload.winner as PlayerId | undefined) ?? null;
      const score = e.payload.score as [number, number] | undefined;
      const games = e.payload.games as [number, number][] | undefined;
      return (
        <span className="flex min-w-0 flex-1 items-center gap-2 text-sm font-medium">
          <Trophy className="size-3.5 shrink-0 text-line" aria-hidden />
          {e.type === "match_end" ? "Match" : `Game ${e.payload.game_no ?? ""}`} to {shortName(session, w)}
          <span className="numerals text-line-2">
            {e.type === "match_end" ? games?.map((g) => g.join("–")).join(", ") : score?.join("–")}
          </span>
        </span>
      );
    }
    default:
      return (
        <span className="flex min-w-0 flex-1 items-center gap-2 text-sm text-line-2">
          <Flag className="size-3.5 shrink-0" aria-hidden />
          {e.type === "interval" ? "Interval" : "Players change ends"}
        </span>
      );
  }
}
