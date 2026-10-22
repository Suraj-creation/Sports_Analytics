import { clsx } from "clsx";
import { Heart, Play } from "lucide-react";
import { getMatch, readyMatches } from "../data/fixtures";
import { CATEGORY_LABEL, type HighlightCategory } from "../data/types";
import { relativeDate } from "../lib/format";
import { Link, useNavigate, useSearch } from "../nav";
import { useStore } from "../store";
import { mmss, RoleGlyph } from "../ui/analytics";
import { Button, Chip } from "../ui/primitives";
import { Page } from "../ui/shell";
import { StateShell } from "../ui/states";

/* ─────────────────────────────────────────────────────────────────────────────
   Moments, across every match.

   A card here links straight into the match with the frame in the URL, so the player
   opens already seeked to the rally. Each card keeps the ranker's own reasons, because
   "why was this picked" is the thing that makes a highlight reel trustworthy.
   ───────────────────────────────────────────────────────────────────────────── */

export function MomentsScreen() {
  const { lens, who } = useSearch<{ lens?: string; who?: string }>({ from: "/moments" });
  const navigate = useNavigate();
  const saved = useStore((s) => s.savedMoments);
  const toggleSaved = useStore((s) => s.toggleSaved);

  const all = readyMatches.flatMap((m) => m.highlights.map((h) => ({ h, m })));
  const cats = [...new Set(all.flatMap(({ h }) => h.categories))];
  const names = [...new Map(readyMatches.flatMap((m) => m.players.map((p) => [p.id, p] as const))).values()];

  const shown = all.filter(({ h }) => {
    if (lens === "saved") return saved.includes(h.id);
    if (lens && !h.categories.includes(lens as HighlightCategory)) return false;
    if (who && !h.credits.includes(who)) return false;
    return true;
  });

  const set = (patch: { lens?: string; who?: string }) =>
    navigate({ to: ".", search: { lens, who, ...patch } });

  return (
    <Page
      title="Moments"
      lead="Every rally the ranker picked out, across all your matches. Each one says why it was chosen."
    >
      <div className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 quiet-scroll sm:mx-0 sm:flex-wrap sm:px-0">
            <Chip selected={!lens} onClick={() => set({ lens: undefined })}>
              All {all.length}
            </Chip>
            <Chip selected={lens === "saved"} onClick={() => set({ lens: "saved" })}>
              <Heart className="size-3.5" aria-hidden /> Saved {saved.length}
            </Chip>
            {cats.map((c) => (
              <Chip key={c} selected={lens === c} onClick={() => set({ lens: c })}>
                {CATEGORY_LABEL[c]}
              </Chip>
            ))}
          </div>
          <div className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 quiet-scroll sm:mx-0 sm:flex-wrap sm:px-0">
            <Chip selected={!who} onClick={() => set({ who: undefined })}>
              Anyone
            </Chip>
            {names.map((p) => (
              <Chip key={p.id} selected={who === p.id} onClick={() => set({ who: p.id })}>
                <RoleGlyph player={p} />
                {p.short}
                {p.isYou && " (you)"}
              </Chip>
            ))}
          </div>
        </div>

        {shown.length === 0 ? (
          <StateShell
            kind="empty"
            title={lens === "saved" ? "You haven't saved anything yet" : "Nothing under this filter"}
            reason={
              lens === "saved"
                ? "Tap the heart on any moment and it will be here."
                : "No rally from any match matched. That's a normal result, not a failure."
            }
            action={
              <Button variant="primary" onClick={() => set({ lens: undefined, who: undefined })}>
                Show everything
              </Button>
            }
          />
        ) : (
          <ul className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {shown.map(({ h, m }) => {
              const isSaved = saved.includes(h.id);
              return (
                <li key={h.id} className="flex flex-col rounded-[14px] border border-edge bg-surface">
                  <div className="flex flex-1 flex-col gap-2 p-4">
                    <div className="flex flex-wrap items-center gap-1.5">
                      {h.categories.slice(0, 2).map((c) => (
                        <span
                          key={c}
                          className="rounded-full bg-surface-raised px-2 py-0.5 text-xs font-medium text-ink"
                        >
                          {CATEGORY_LABEL[c]}
                        </span>
                      ))}
                      <span className="ml-auto text-xs text-faint">{h.durationS}s</span>
                    </div>
                    <p className="text-base font-[650] leading-snug text-ink">{h.title}</p>
                    <p className="text-sm text-muted">{h.why}</p>
                    <p className="flex flex-wrap items-center gap-1.5 text-xs text-faint">
                      {h.credits.map((id) => {
                        const p = getMatch(m.id)?.players.find((x) => x.id === id);
                        return (
                          <span key={id} className="inline-flex items-center gap-1">
                            <RoleGlyph player={p} className="size-2" />
                            {p?.short}
                          </span>
                        );
                      })}
                    </p>
                    <Link
                      to="/matches/$matchId"
                      params={{ matchId: m.id }}
                      search={{ tab: "overview" }}
                      className="mt-auto text-xs text-muted hover:text-ink hover:underline"
                    >
                      {m.title} · {relativeDate(m.date)} · rally {h.rallyNo} at {mmss(h.frames[0], m.fps)}
                    </Link>
                  </div>
                  <div className="flex items-center gap-1 border-t border-edge px-3 py-2">
                    <Link
                      to="/matches/$matchId"
                      params={{ matchId: m.id }}
                      search={{ tab: "moments", f: h.frames[0] }}
                    >
                      <Button size="sm" variant="primary">
                        <Play className="size-4 fill-current" aria-hidden />
                        Watch
                      </Button>
                    </Link>
                    <Button size="sm" variant="ghost" onClick={() => toggleSaved(h.id)}>
                      <Heart className={clsx("size-4", isSaved && "fill-you text-you")} aria-hidden />
                      {isSaved ? "Saved" : "Save"}
                    </Button>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </Page>
  );
}
