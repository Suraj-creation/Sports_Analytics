import { clsx } from "clsx";
import { ArrowLeft, Download, Heart, Play, Send, Share2, ShieldCheck, UserRound } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  buildUp,
  SCORE_STATE_LABEL,
  type ScoreState,
  scoreStateOf,
  serveAndReceive,
  shotEffectiveness,
  transitions,
} from "../data/analysis";
import { applyIdentity, getMatch, opponentsIn, partnerIn, trends, youIn } from "../data/fixtures";
import {
  courtInsights,
  h2hInsights,
  momentumInsights,
  movementInsights,
  overviewInsights,
  pairInsights,
  rallyInsights,
  shotInsights,
} from "../data/insights";
import {
  CATEGORY_LABEL,
  HEATMAP_KINDS,
  type HeatmapKind,
  type Match,
  type PlayerId,
  STROKE_LABEL,
} from "../data/types";
import { longDate } from "../lib/format";
import { Link, useNavigate, useParams, useSearch } from "../nav";
import { MatchPlayer } from "../player/MatchPlayer";
import { usePlayer } from "../player/store";
import { useStore } from "../store";
import {
  CourtHeatmap,
  FamilySplit,
  HeadToHead,
  MomentumChart,
  mmss,
  Panel,
  RallyHistogram,
  RallyList,
  RoleGlyph,
  roleColour,
  StatTile,
  StrokeMix,
  TrendLine,
  WorkRate,
  ZoneTable,
} from "../ui/analytics";
import {
  ChangeSummary,
  CorrectionControls,
  ExportSheet,
  IdentitySheet,
  PlaylistDialog,
  QualityPanel,
  ReflectionPrompt,
  SharePreviewDialog,
} from "../ui/flows";
import { SetFocusButton } from "../ui/focus";
import { Button, Card, Chip } from "../ui/primitives";
import { Page } from "../ui/shell";
import { StateShell } from "../ui/states";
import { BuildUp, Counterexamples, ServeReceive, ShotEffectiveness, TransitionsPanel } from "../ui/tactical";
import { PreviewTag } from "../ui/trust";

/* ─────────────────────────────────────────────────────────────────────────────
   The match workspace.

   One route. The player lives at the top and stays loaded; ten tabs of analysis sit
   beneath it in `?tab=`. Anything you click anywhere in those tabs seeks the player
   and scrolls it into view — the loop the whole product is built around.
   ───────────────────────────────────────────────────────────────────────────── */

type Tab =
  | "overview"
  | "moments"
  | "rallies"
  | "shots"
  | "tactics"
  | "court"
  | "movement"
  | "h2h"
  | "pair"
  | "ask";

interface MatchSearch {
  tab: Tab;
  who?: PlayerId;
  rally?: number;
  kind?: HeatmapKind;
  lens?: string;
  /** Frame deep link — a moment anywhere can open the player already seeked. */
  f?: number;
}

export function MatchScreen() {
  const { matchId } = useParams<{ matchId: string }>({ from: "/matches/$matchId" });
  const search = useSearch<MatchSearch>({ from: "/matches/$matchId" });
  const navigate = useNavigate();
  const base = getMatch(matchId);
  const identity = useStore((st) => st.identity);
  const nicknames = useStore((st) => st.nicknames);
  // Everything below works on the identity-centred view, so "you" means who you said.
  const match = useMemo(
    () => (base ? applyIdentity(base, identity[base.id], nicknames) : undefined),
    [base, identity, nicknames],
  );
  const [sheet, setSheet] = useState<null | "identity" | "quality" | "export" | "share">(null);
  const [shareId, setShareId] = useState<string | null>(null);
  const reset = usePlayer((s) => s.reset);
  const cue = usePlayer((s) => s.cue);
  const stageRef = useRef<HTMLDivElement>(null);
  const firstCue = useRef(true);

  // A new match starts at the beginning — unless the link carried a frame, in which
  // case we open already seeked to it (the `?f=` contract the production app uses).
  // biome-ignore lint/correctness/useExhaustiveDependencies: arrival only — later seeks come from the cards
  useEffect(() => {
    if (search.f !== undefined) usePlayer.getState().seek(search.f);
    else reset();
  }, [matchId]);

  // Ask who you are the first time you open a match, before any "you" is claimed.
  useEffect(() => {
    const m = getMatch(matchId);
    if (m && m.status === "ready" && !useStore.getState().identity[matchId]) {
      setSheet("identity");
    }
  }, [matchId]);

  // Any "watch" anywhere brings the player back into view.
  useEffect(() => {
    if (!cue) return;
    if (firstCue.current) {
      firstCue.current = false;
      return;
    }
    stageRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [cue]);

  if (!match) {
    return (
      <Page title="We couldn't find that match">
        <StateShell
          kind="permission"
          title="This match isn't here"
          reason="It may have been deleted, or the link may belong to someone else."
          action={
            <Link to="/matches">
              <Button variant="primary">See your matches</Button>
            </Link>
          }
        />
      </Page>
    );
  }

  if (match.status === "failed") {
    return (
      <Page title={match.title}>
        <StateShell
          kind="failed"
          title="We couldn't finish this one"
          reason="The recording stopped about four minutes in. There isn't enough footage to analyse, and the venue has been told."
          action={
            <Link to="/matches">
              <Button variant="primary">Back to your matches</Button>
            </Link>
          }
        />
      </Page>
    );
  }

  // Who you are is a decision, not an assumption. Until it is made, nothing says "you".
  const identified = identity[match.id];
  const me = match.players.find((p) => p.id === identified) ?? youIn(match);
  const who = search.who ?? me.id;
  const lowCoverage = match.coverage.followed / Math.max(1, match.coverage.total) < 0.7;
  const tab = search.tab ?? "overview";
  const set = (patch: Partial<MatchSearch>) => navigate({ to: ".", search: { ...search, ...patch } });

  const tabs: { id: Tab; label: string; show: boolean }[] = [
    { id: "overview", label: "Overview", show: true },
    { id: "moments", label: `Moments · ${match.highlights.length}`, show: true },
    { id: "rallies", label: `Rallies · ${match.rallies.filter((r) => r.official).length}`, show: true },
    { id: "shots", label: "Shots", show: true },
    { id: "tactics", label: "Tactics", show: true },
    { id: "court", label: "Court", show: true },
    { id: "movement", label: "Movement", show: true },
    { id: "h2h", label: "Head to head", show: true },
    { id: "pair", label: "Your pair", show: match.discipline === "doubles" },
    { id: "ask", label: "Ask", show: true },
  ];

  return (
    <div className="mx-auto w-full max-w-[1480px] px-4 py-5 md:px-6">
      <MatchHeader
        match={match}
        me={me}
        identified={Boolean(identified)}
        onIdentity={() => setSheet("identity")}
        onQuality={() => setSheet("quality")}
        onExport={() => setSheet("export")}
      />

      {lowCoverage && (
        <div className="mt-4 flex items-start gap-3 rounded-[14px] border border-opportunity/40 bg-opportunity/10 p-4">
          <span aria-hidden className="mt-0.5 text-opportunity">
            ◆
          </span>
          <div>
            <p className="font-[600] text-ink">
              We could only follow {match.coverage.followed} of {match.coverage.total} rallies.
            </p>
            <p className="mt-1 text-sm text-muted">
              {match.coverage.reason} Every number below uses only the rallies we followed, so read them as a
              partial picture — and treat comparisons with other matches carefully.
            </p>
            <button
              type="button"
              onClick={() => setSheet("quality")}
              className="mt-2 text-sm text-primary underline underline-offset-2"
            >
              What we could and couldn't see
            </button>
          </div>
        </div>
      )}

      <div className="mt-4">
        <ChangeSummary matchId={match.id} />
      </div>

      <div ref={stageRef} className="mt-5 scroll-mt-4">
        {match.status === "analysing" ? <Analysing match={match} /> : <MatchPlayer match={match} />}
      </div>

      {match.status === "ready" && (
        <>
          <WhoPicker match={match} who={who} onChange={(id) => set({ who: id })} />

          <nav
            aria-label="Match analysis"
            className="-mx-4 mt-4 flex gap-1 overflow-x-auto border-b border-edge px-4 quiet-scroll md:mx-0 md:px-0"
          >
            {tabs
              .filter((t) => t.show)
              .map((t) => (
                <button
                  key={t.id}
                  type="button"
                  aria-current={tab === t.id ? "page" : undefined}
                  onClick={() => set({ tab: t.id })}
                  className={clsx(
                    "-mb-px shrink-0 whitespace-nowrap border-b-2 px-3.5 py-3 text-sm transition-colors",
                    tab === t.id
                      ? "border-ink font-[600] text-ink"
                      : "border-transparent text-muted hover:text-ink",
                  )}
                >
                  {t.label}
                </button>
              ))}
          </nav>

          <div className="mt-5">
            {tab === "overview" && <OverviewTab match={match} who={who} />}
            {tab === "moments" && (
              <MomentsTab
                match={match}
                lens={search.lens}
                onLens={(l) => set({ lens: l })}
                who={who}
                onShare={setShareId}
              />
            )}
            {tab === "rallies" && (
              <RalliesTab
                match={match}
                rally={search.rally ?? null}
                onRally={(n) => set({ rally: n ?? undefined })}
                who={who}
              />
            )}
            {tab === "shots" && <ShotsTab match={match} who={who} />}
            {tab === "tactics" && <TacticsTab match={match} who={who} />}
            {tab === "court" && (
              <CourtTab
                match={match}
                kind={search.kind ?? "presence"}
                onKind={(k) => set({ kind: k })}
                who={who}
              />
            )}
            {tab === "movement" && <MovementTab match={match} who={who} />}
            {tab === "h2h" && <H2HTab match={match} who={who} />}
            {tab === "pair" && <PairTab match={match} who={who} />}
            {tab === "ask" && <AskTab match={match} who={who} />}
          </div>
        </>
      )}

      <IdentitySheet match={match} open={sheet === "identity"} onClose={() => setSheet(null)} />
      <QualityPanel match={match} open={sheet === "quality"} onClose={() => setSheet(null)} />
      <ExportSheet match={match} open={sheet === "export"} onClose={() => setSheet(null)} />
      <SharePreviewDialog
        match={match}
        highlight={match.highlights.find((h) => h.id === shareId) ?? null}
        open={Boolean(shareId)}
        onClose={() => setShareId(null)}
      />
    </div>
  );
}

/* ───────────────────────── header ───────────────────────── */

function MatchHeader({
  match,
  me,
  identified,
  onIdentity,
  onQuality,
  onExport,
}: {
  match: Match;
  me: ReturnType<typeof youIn>;
  identified: boolean;
  onIdentity: () => void;
  onQuality: () => void;
  onExport: () => void;
}) {
  const won = match.games.filter(([a, b]) => (me.side === "A" ? a > b : b > a)).length;
  const lost = match.games.length - won;
  return (
    <header className="flex flex-col gap-3">
      <Link to="/matches" className="inline-flex w-fit items-center gap-1 text-sm text-muted hover:text-ink">
        <ArrowLeft className="size-4" aria-hidden />
        Matches
      </Link>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-[700] leading-tight text-ink md:text-3xl">{match.title}</h1>
          <p className="mt-1 text-sm text-muted">
            {longDate(match.date)} · {match.venue}, {match.court} ·{" "}
            <span className="capitalize">{match.discipline}</span> · {match.durationMin} min
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <ScoreCard match={match} />
          <span className="rounded-full border border-edge px-3 py-1.5 text-sm text-muted">
            {won}–{lost} in games
          </span>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" variant={identified ? "secondary" : "primary"} onClick={onIdentity}>
          <UserRound className="size-4" aria-hidden />
          {identified ? `You are ${me.short}` : "Which one is you?"}
        </Button>
        <Button size="sm" variant="ghost" onClick={onQuality}>
          <ShieldCheck className="size-4" aria-hidden />
          How reliable is this?
        </Button>
        <Button size="sm" variant="ghost" onClick={onExport}>
          <Download className="size-4" aria-hidden />
          Export
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted">
        <span>
          <strong className="font-[600] text-ink">{match.rallies.filter((r) => r.official).length}</strong>{" "}
          rallies
        </span>
        <span>
          <strong className="font-[600] text-ink">{Math.round(match.activePlayS / 60)}</strong> min shuttle in
          play
        </span>
        <span>
          We followed{" "}
          <strong className="font-[600] text-ink">
            {match.coverage.followed} of {match.coverage.total}
          </strong>{" "}
          rallies
        </span>
        <span className="text-faint">{match.coverage.reason}</span>
      </div>
    </header>
  );
}

function ScoreCard({ match }: { match: Match }) {
  return (
    <div className="flex overflow-hidden rounded-[10px] border border-edge">
      {(["A", "B"] as const).map((side) => (
        <div key={side} className="flex items-center gap-2 border-r border-edge px-3 py-1.5 last:border-0">
          <span className="flex -space-x-1">
            {match.sides[side].players.map((id) => (
              <RoleGlyph key={id} player={match.players.find((p) => p.id === id)} />
            ))}
          </span>
          <span className="text-sm text-muted">{match.sides[side].label}</span>
          <span className="numerals tabular text-base text-ink">
            {match.games.map(([a, b]) => (side === "A" ? a : b)).join(" ")}
          </span>
        </div>
      ))}
    </div>
  );
}

function Analysing({ match }: { match: Match }) {
  const pct = Math.round((match.progress ?? 0) * 100);
  return (
    <Card className="flex flex-col gap-4">
      <p className="text-lg font-[650] text-ink">We're watching this one</p>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-surface-raised"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className="h-full rounded-full bg-you" style={{ width: `${pct}%` }} />
      </div>
      <p className="tabular text-sm text-muted">{pct}% of the footage watched</p>
      <p className="text-sm text-faint">
        Rallies, shots and moments appear as they are found. You can close this.
      </p>
    </Card>
  );
}

/** Whose numbers am I looking at? The single most important control in doubles. */
function WhoPicker({
  match,
  who,
  onChange,
}: {
  match: Match;
  who: PlayerId;
  onChange: (id: PlayerId) => void;
}) {
  return (
    <div className="mt-4 flex flex-wrap items-center gap-2">
      <span className="text-sm text-muted">Showing</span>
      {match.players.map((p) => (
        <button
          key={p.id}
          type="button"
          aria-pressed={who === p.id}
          onClick={() => onChange(p.id)}
          className={clsx(
            "inline-flex min-h-9 items-center gap-1.5 rounded-full border px-3 text-sm transition-colors",
            who === p.id
              ? "border-ink bg-ink text-canvas"
              : "border-edge bg-surface text-muted hover:border-edge-strong hover:text-ink",
          )}
        >
          <RoleGlyph player={p} />
          {p.short}
          {p.isYou && " (you)"}
        </button>
      ))}
    </div>
  );
}

/* ───────────────────────── overview ───────────────────────── */

function OverviewTab({ match, who }: { match: Match; who: PlayerId }) {
  const seek = usePlayer((s) => s.seek);
  const st = match.stats[who];
  const p = match.players.find((x) => x.id === who);
  const hero = match.highlights[0];
  const offs = match.rallies.filter((r) => r.official);
  const longest = offs.slice().sort((a, b) => b.shots.length - a.shots.length)[0];
  if (!st) return null;

  return (
    <div className="flex flex-col gap-5">
      <ReflectionPrompt match={match} />

      {/* the numbers that matter to a player, big */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          hero
          value={longest?.shots.length ?? 0}
          unit="shots"
          label="Longest rally"
          sub={`of ${offs.length} counted rallies`}
          onWatch={() =>
            longest && seek(longest.frames[0], `The longest rally — ${longest.shots.length} shots`)
          }
        />
        <StatTile
          value={st.shotsPlayed}
          unit="shots"
          label={`${p?.short} played`}
          sub={`${st.repertoire} different shot types`}
        />
        <StatTile
          value={st.distanceM}
          unit="m"
          label="Distance covered"
          sub={`${st.steps.toLocaleString()} steps · ${(st.activeS / 60).toFixed(1)} min of play`}
        />
        <StatTile
          value={Math.round((st.returnsMade / Math.max(1, st.returnsAttempted)) * 100)}
          unit="%"
          label="Returns kept in play"
          sub={`${st.returnsMade} of ${st.returnsAttempted}`}
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        {hero && (
          <Panel
            question="What was the moment of the match?"
            hint={hero.why}
            actions={
              <Button size="sm" variant="primary" onClick={() => seek(hero.frames[0], hero.title)}>
                <Play className="size-4 fill-current" aria-hidden />
                Watch
              </Button>
            }
          >
            <div className="flex flex-col gap-3">
              <p className="text-xl font-[650] text-ink">{hero.title}</p>
              <div className="flex flex-wrap gap-1.5">
                {hero.categories.map((c) => (
                  <span
                    key={c}
                    className="rounded-full bg-surface-raised px-2.5 py-1 text-xs font-medium text-ink"
                  >
                    {CATEGORY_LABEL[c]}
                  </span>
                ))}
              </div>
              <p className="text-sm text-muted">
                Rally {hero.rallyNo} at {mmss(hero.frames[0], match.fps)} · {hero.durationS}s · credits{" "}
                {hero.credits.map((id) => match.players.find((x) => x.id === id)?.short).join(" & ")}
              </p>
              <div className="flex flex-wrap gap-2">
                {match.highlights.slice(1, 5).map((h) => (
                  <button
                    key={h.id}
                    type="button"
                    onClick={() => seek(h.frames[0], h.title)}
                    className="rounded-full border border-edge px-3 py-1.5 text-xs text-muted hover:border-edge-strong hover:text-ink"
                  >
                    {h.title}
                  </button>
                ))}
              </div>
            </div>
          </Panel>
        )}

        <Panel
          question="How did the match swing?"
          hint="Each point nudges the line. Click anywhere on it to jump there."
          insights={momentumInsights(match, who)}
        >
          <MomentumChart match={match} />
        </Panel>
      </div>

      <Panel
        question={`What stood out for ${p?.short}?`}
        hint="Every line below is generated from the numbers on this page, and opens the footage it came from."
        insights={overviewInsights(match, who)}
      >
        <div className="grid gap-3 sm:grid-cols-3">
          <MiniStat label="Winners" value={st.winners} />
          <MiniStat label="Ended long or wide" value={st.errorsOut} />
          <MiniStat label="Ended in the net" value={st.errorsNet} />
          <MiniStat label="Smashes" value={st.smashes} sub={`${st.jumpSmashes} jumping`} />
          <MiniStat label="Net shots" value={st.netShots} />
          <MiniStat label="Defensive saves" value={st.defensiveSaves} />
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-edge pt-3">
          <span className="text-sm text-muted">Want to keep an eye on something?</span>
          <SetFocusButton
            title={`Where my shots were met — ${match.title}`}
            why="You picked this yourself from the match overview."
            matchId={match.id}
            frame={longest?.frames[0] ?? null}
          />
          <Link to="/progress" search={{ tab: "focus" }}>
            <Button size="sm" variant="ghost">
              See your focus
            </Button>
          </Link>
        </div>
      </Panel>
    </div>
  );
}

function MiniStat({ label, value, sub }: { label: string; value: number; sub?: string }) {
  return (
    <div className="rounded-[10px] bg-surface-raised px-3 py-2.5">
      <p className="numerals text-2xl leading-none text-ink">{value}</p>
      <p className="mt-1 text-sm text-ink">{label}</p>
      {sub && <p className="text-xs text-faint">{sub}</p>}
    </div>
  );
}

/* ───────────────────────── moments ───────────────────────── */

function MomentsTab({
  match,
  lens,
  onLens,
  who,
  onShare,
}: {
  match: Match;
  lens?: string;
  onLens: (l: string | undefined) => void;
  who: PlayerId;
  onShare: (id: string) => void;
}) {
  const playClip = usePlayer((s) => s.playClip);
  const saved = useStore((s) => s.savedMoments);
  const toggleSaved = useStore((s) => s.toggleSaved);
  const [selected, setSelected] = useState<string[]>([]);
  const [playlistOpen, setPlaylistOpen] = useState(false);
  const cats = [...new Set(match.highlights.flatMap((h) => h.categories))];
  const shown = lens
    ? match.highlights.filter((h) => h.categories.includes(lens as never))
    : match.highlights;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap gap-2">
        <Chip selected={!lens} onClick={() => onLens(undefined)}>
          All {match.highlights.length}
        </Chip>
        {cats.map((c) => (
          <Chip key={c} selected={lens === c} onClick={() => onLens(c)}>
            {CATEGORY_LABEL[c]}
          </Chip>
        ))}
      </div>

      <ul className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {shown.map((h) => {
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
                  Rally {h.rallyNo} · {mmss(h.frames[0], match.fps)} ·
                  {h.credits.map((id) => {
                    const p = match.players.find((x) => x.id === id);
                    return (
                      <span key={id} className="inline-flex items-center gap-1">
                        <RoleGlyph player={p} className="size-2" />
                        {p?.short}
                      </span>
                    );
                  })}
                </p>
                {/* The ranker's own reasons — the explainability the engine already produces. */}
                <details className="mt-auto">
                  <summary className="cursor-pointer list-none text-xs text-primary hover:underline">
                    Why this was picked
                  </summary>
                  <ul className="mt-1.5 flex flex-col gap-1 text-xs text-muted">
                    {Object.entries(h.reasons)
                      .sort((a, b) => b[1] - a[1])
                      .map(([k, v]) => (
                        <li key={k} className="flex items-center justify-between gap-2">
                          <span>{k.replace(/_/g, " ")}</span>
                          <span className="tabular text-faint">{v.toFixed(1)}</span>
                        </li>
                      ))}
                  </ul>
                </details>
              </div>
              <div className="flex items-center gap-1 border-t border-edge px-3 py-2">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => playClip(h.frames[0], h.frames[1], h.title)}
                >
                  <Play className="size-4 fill-current" aria-hidden />
                  Watch
                </Button>
                <Button size="sm" variant="ghost" onClick={() => toggleSaved(h.id)}>
                  <Heart className={clsx("size-4", isSaved && "fill-you text-you")} aria-hidden />
                  {isSaved ? "Saved" : "Save"}
                </Button>
                <Button size="sm" variant="ghost" onClick={() => onShare(h.id)}>
                  <Share2 className="size-4" aria-hidden />
                  Share
                </Button>
                <label className="ml-auto flex cursor-pointer items-center gap-1.5 text-xs text-muted">
                  <input
                    type="checkbox"
                    checked={selected.includes(h.id)}
                    onChange={(e) =>
                      setSelected((xs) => (e.target.checked ? [...xs, h.id] : xs.filter((x) => x !== h.id)))
                    }
                    className="size-4 accent-[var(--c-primary)]"
                  />
                  Pick
                </label>
              </div>
            </li>
          );
        })}
      </ul>

      {selected.length > 0 && (
        <div className="sticky bottom-4 z-10 flex flex-wrap items-center gap-3 rounded-[14px] border border-edge bg-surface p-3 shadow-[var(--shadow-pop)]">
          <span className="text-sm text-ink">{selected.length} picked</span>
          <Button size="sm" variant="primary" onClick={() => setPlaylistOpen(true)}>
            <Share2 className="size-4" aria-hidden />
            Send to a coach
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setSelected([])}>
            Clear
          </Button>
        </div>
      )}

      <PlaylistDialog
        open={playlistOpen}
        onClose={() => {
          setPlaylistOpen(false);
          setSelected([]);
        }}
        momentIds={selected}
        momentTitles={selected.map((id) => match.highlights.find((h) => h.id === id)?.title ?? id)}
      />

      <Panel
        question="And the ones that got away"
        hint="A reel is selected for being good. These are long rallies that ended on your racket, shown so the picture is not only the flattering half."
      >
        <Counterexamples match={match} pid={who} />
      </Panel>
    </div>
  );
}

/* ───────────────────────── rallies ───────────────────────── */

function RalliesTab({
  match,
  rally,
  onRally,
  who,
}: {
  match: Match;
  rally: number | null;
  onRally: (n: number | null) => void;
  who: PlayerId;
}) {
  const me = match.players.find((p) => p.id === who) ?? youIn(match);
  const [game, setGame] = useState<number | "all">("all");
  const [state, setState] = useState<ScoreState | "all">("all");
  const [role, setRole] = useState<"all" | "serving" | "receiving">("all");
  const [length, setLength] = useState<"all" | "long" | "short">("all");
  const [outcome, setOutcome] = useState<"all" | "won" | "lost">("all");

  const list = match.rallies.filter((r) => {
    if (game !== "all" && r.game !== game) return false;
    if (length === "long" && r.shots.length < 8) return false;
    if (length === "short" && r.shots.length > 4) return false;
    if (outcome !== "all") {
      if (!r.official) return false;
      const won = r.winner === me.side;
      if (outcome === "won" && !won) return false;
      if (outcome === "lost" && won) return false;
    }
    if (role !== "all") {
      if (!r.official) return false;
      const iServed = match.players.find((p) => p.id === r.server)?.side === me.side;
      if (role === "serving" && !iServed) return false;
      if (role === "receiving" && iServed) return false;
    }
    if (state !== "all") {
      if (!r.official) return false;
      if (scoreStateOf(match, r.no, me.id) !== state) return false;
    }
    return true;
  });

  const reset = () => {
    setGame("all");
    setState("all");
    setRole("all");
    setLength("all");
    setOutcome("all");
  };
  const active =
    (game !== "all" ? 1 : 0) +
    (state !== "all" ? 1 : 0) +
    (role !== "all" ? 1 : 0) +
    (length !== "all" ? 1 : 0) +
    (outcome !== "all" ? 1 : 0);

  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-3 rounded-[14px] border border-edge bg-surface p-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-[600] text-ink">Filter the rallies</p>
            <span className="text-sm text-muted">
              {list.length} of {match.rallies.length}
              {active > 0 && (
                <button
                  type="button"
                  onClick={reset}
                  className="ml-2 text-primary underline underline-offset-2"
                >
                  Clear {active}
                </button>
              )}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Select
              label="Game"
              value={String(game)}
              onChange={(v) => setGame(v === "all" ? "all" : Number(v))}
              options={[
                ["all", "Any game"],
                ...match.games.map((_, i) => [String(i + 1), `Game ${i + 1}`] as [string, string]),
              ]}
            />
            <Select
              label="Score state"
              value={state}
              onChange={(v) => setState(v as ScoreState | "all")}
              options={[
                ["all", "Any score"],
                ...(Object.entries(SCORE_STATE_LABEL) as [ScoreState, string][]).map(
                  ([k, v]) => [k, v] as [string, string],
                ),
              ]}
            />
            <Select
              label="Serve"
              value={role}
              onChange={(v) => setRole(v as "all" | "serving" | "receiving")}
              options={[
                ["all", "Either"],
                ["serving", `${me.short} served`],
                ["receiving", `${me.short} received`],
              ]}
            />
            <Select
              label="Rally length"
              value={length}
              onChange={(v) => setLength(v as "all" | "long" | "short")}
              options={[
                ["all", "Any length"],
                ["long", "8 shots or more"],
                ["short", "4 shots or fewer"],
              ]}
            />
            <Select
              label="Outcome"
              value={outcome}
              onChange={(v) => setOutcome(v as "all" | "won" | "lost")}
              options={[
                ["all", "Any outcome"],
                ["won", "Points won"],
                ["lost", "Points lost"],
              ]}
            />
          </div>
        </div>

        {list.length === 0 ? (
          <StateShell
            kind="empty"
            title="No rally matches those filters"
            reason="That is a result too — it means this situation did not come up in this match."
            action={
              <Button variant="primary" onClick={reset}>
                Clear the filters
              </Button>
            }
          />
        ) : (
          <RallyList
            match={match}
            rallies={list}
            expanded={rally}
            onExpand={onRally}
            extra={(r) => <CorrectionControls match={match} rally={r} />}
          />
        )}
      </div>

      <div className="flex flex-col gap-5">
        <Panel
          question="How long were the rallies?"
          hint="Click a bar to watch one of that length."
          basis={`${match.rallies.filter((r) => r.official).length} counted rallies`}
          insights={rallyInsights(match, me.id)}
        >
          <RallyHistogram match={match} />
        </Panel>
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: [string, string][];
}) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-10 rounded-[10px] border border-edge bg-surface px-2.5 text-sm text-ink focus:border-edge-strong focus:outline-none"
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
}

/* ───────────────────────── shots ───────────────────────── */

function ShotsTab({ match, who }: { match: Match; who: PlayerId }) {
  const ids = match.players.map((p) => p.id);
  const st = match.stats[who];
  const p = match.players.find((x) => x.id === who);
  if (!st) return null;
  const serveWin = st.serves ? Math.round((st.servePointsWon / st.serves) * 100) : 0;

  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile value={st.shotsPlayed} unit="shots" label={`${p?.short} played`} />
        <StatTile value={st.repertoire} unit="types" label="Different shots used" />
        <StatTile
          value={st.smashes}
          unit="smashes"
          label="Smashes"
          sub={`${st.jumpSmashes} jumping · ${st.smashPoints} finished the rally`}
        />
        <StatTile value={serveWin} unit="%" label="Serves that won the rally" sub={`${st.serves} serves`} />
      </div>

      <Panel
        question={`What happened when ${p?.short} played each shot?`}
        hint="Counts and rates together — a shot played four times and one played sixty cannot be compared on frequency alone."
        basis={`${match.rallies.filter((r) => r.official).length} counted rallies`}
      >
        <ShotEffectiveness rows={shotEffectiveness(match, who)} />
      </Panel>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel
          question="Which shots did everyone play?"
          basis={`${match.rallies.filter((r) => r.official).length} counted rallies`}
          tag={
            <PreviewTag
              what="shot naming"
              why="The classifier is rule-based and has not been validated on this venue's camera. Treat every name as a candidate."
            />
          }
          insights={shotInsights(match, who)}
          table={<StrokeTable match={match} ids={ids} />}
        >
          <StrokeMix match={match} ids={ids} />
        </Panel>

        <div className="flex flex-col gap-5">
          <Panel
            question="How much of the time was each player attacking?"
            hint="Smashes, drops and net kills count as attacking; clears, lifts and blocks as defending."
          >
            <FamilySplit match={match} ids={ids} />
          </Panel>
          <Panel
            question="Which shots ended rallies?"
            hint="The last shot of each counted rally. Read it next to the build-up on the Tactics tab — a finishing shot is rarely the one that created the opening."
          >
            <DecisiveShots match={match} />
          </Panel>
        </div>
      </div>
    </div>
  );
}

function StrokeTable({ match, ids }: { match: Match; ids: PlayerId[] }) {
  const keys = [...new Set(ids.flatMap((id) => Object.keys(match.stats[id]?.strokes ?? {})))];
  return (
    <table className="w-full text-sm">
      <thead className="text-left text-xs text-faint">
        <tr>
          <th className="py-1 font-[600]">Shot</th>
          {ids.map((id) => (
            <th key={id} className="py-1 text-right font-[600]">
              {match.players.find((p) => p.id === id)?.short}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="tabular">
        {keys.map((k) => (
          <tr key={k} className="border-t border-edge">
            <th scope="row" className="py-1.5 text-left font-normal text-ink">
              {STROKE_LABEL[k] ?? k}
            </th>
            {ids.map((id) => (
              <td key={id} className="py-1.5 text-right text-muted">
                {match.stats[id]?.strokes[k] ?? 0}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function DecisiveShots({ match }: { match: Match }) {
  const seek = usePlayer((s) => s.seek);
  const counts = new Map<string, { n: number; frame: number }>();
  for (const r of match.rallies) {
    if (!r.official) continue;
    const last = r.shots[r.shots.length - 1];
    if (!last) continue;
    const key = last.subtype ?? last.stroke;
    const prev = counts.get(key);
    counts.set(key, { n: (prev?.n ?? 0) + 1, frame: prev?.frame ?? last.frame });
  }
  const list = [...counts.entries()].sort((a, b) => b[1].n - a[1].n);
  const max = Math.max(1, ...list.map(([, v]) => v.n));
  return (
    <ul className="flex flex-col gap-2">
      {list.map(([k, v]) => (
        <li key={k} className="grid grid-cols-[110px_1fr_auto] items-center gap-3">
          <span className="truncate text-sm text-ink">{STROKE_LABEL[k] ?? k}</span>
          <span className="h-2.5 rounded-sm bg-you" style={{ width: `${(v.n / max) * 100}%` }} />
          <button
            type="button"
            onClick={() => seek(v.frame, `A rally that ended with a ${(STROKE_LABEL[k] ?? k).toLowerCase()}`)}
            className="tabular text-xs text-evidence hover:underline"
          >
            {v.n} ▸
          </button>
        </li>
      ))}
    </ul>
  );
}

/* ───────────────────────── tactics ─────────────────────────
   What built the point, not only what finished it. The source blueprint is explicit
   that a terminal-shot view misleads, so the build-up panel leads this tab. */

function TacticsTab({ match, who }: { match: Match; who: PlayerId }) {
  const p = match.players.find((x) => x.id === who);
  const seq = buildUp(match, who);
  const sr = serveAndReceive(match, who);
  const tr = transitions(match, who);
  const counted = match.rallies.filter((r) => r.official).length;

  return (
    <div className="flex flex-col gap-5">
      <Panel
        question="What led to the point?"
        hint="The last three shots of each rally, split by who won it. Crediting only the final stroke hides the shot that actually created the opening."
        basis={`${seq.sampleWon + seq.sampleLost} counted rallies ${p?.short} was involved in at the end`}
      >
        <BuildUp won={seq.won} lost={seq.lost} sampleWon={seq.sampleWon} sampleLost={seq.sampleLost} />
      </Panel>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel
          question="How did the serve and the return go?"
          hint="Rallies won, against the serve that started them."
          basis={`${counted} counted rallies`}
        >
          <ServeReceive serving={sr.serving} receiving={sr.receiving} />
        </Panel>

        <Panel
          question="Did you turn defence into attack?"
          hint="Rallies where the same player played both a defending and an attacking shot, in that order."
          basis={`${tr.sample} rallies with two or more shots from ${p?.short}`}
        >
          <TransitionsPanel t={tr} />
        </Panel>
      </div>
    </div>
  );
}

/* ───────────────────────── court ───────────────────────── */

function CourtTab({
  match,
  kind,
  onKind,
  who,
}: {
  match: Match;
  kind: HeatmapKind;
  onKind: (k: HeatmapKind) => void;
  who: PlayerId;
}) {
  const meta = HEATMAP_KINDS.find((k) => k.id === kind) ?? HEATMAP_KINDS[0];
  const st = match.stats[who];
  const p = match.players.find((x) => x.id === who);

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap gap-2">
        {HEATMAP_KINDS.map((k) => (
          <Chip key={k.id} selected={kind === k.id} onClick={() => onKind(k.id)}>
            {k.label}
            {k.preview && <span className="text-uncertain">◇</span>}
          </Chip>
        ))}
      </div>

      <Panel
        question={meta?.label ?? "Court"}
        hint={meta?.hint}
        tag={
          meta?.preview ? (
            <PreviewTag
              what="placement"
              why="We do not reconstruct the shuttle's flight. This shows where the receiver met the shuttle, which is a different thing and is named for what it measures."
            />
          ) : undefined
        }
        insights={courtInsights(match, who, kind)}
      >
        <div className="flex flex-wrap items-start justify-center gap-6">
          {match.players.map((pl) => (
            <figure key={pl.id} className="flex flex-col items-center gap-2">
              <figcaption className="flex items-center gap-1.5 text-sm font-[600] text-ink">
                <RoleGlyph player={pl} />
                {pl.short}
                {pl.isYou && " (you)"}
              </figcaption>
              <CourtHeatmap
                heat={match.heatmaps.find((h) => h.player === pl.id && h.kind === kind)}
                player={pl}
                kind={kind}
                width={200}
              />
            </figure>
          ))}
        </div>
      </Panel>

      {st && (
        <div className="grid gap-5 lg:grid-cols-2">
          <Panel
            question={`Where did ${p?.short} hit from?`}
            hint="Counted by the 3 × 3 zones the engine uses."
          >
            <ZoneTable counts={st.originZones} title={`${p?.short} shot origins`} />
          </Panel>
          <Panel
            question={`Where were ${p?.short}'s shots met?`}
            tag={<PreviewTag what="placement" />}
            hint="The receiver's position at the moment of contact."
          >
            <ZoneTable counts={st.targetZones} title={`${p?.short} targets`} />
          </Panel>
        </div>
      )}
    </div>
  );
}

/* ───────────────────────── movement ───────────────────────── */

function MovementTab({ match, who }: { match: Match; who: PlayerId }) {
  const ids = match.players.map((p) => p.id);
  const st = match.stats[who];
  const p = match.players.find((x) => x.id === who);
  if (!st) return null;
  const mins = st.activeS / 60;

  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile hero value={st.distanceM} unit="m" label="Distance covered" sub={`${p?.short} on court`} />
        <StatTile
          value={st.steps.toLocaleString()}
          unit="steps"
          label="Steps"
          sub="at an average 0.78 m stride"
        />
        <StatTile
          value={mins.toFixed(1)}
          unit="min"
          label="Shuttle in play"
          sub={`of ${match.durationMin} min on court`}
        />
        <StatTile
          value={(st.distanceM / Math.max(1, mins)).toFixed(0)}
          unit="m/min"
          label="Work rate"
          sub="while the shuttle was live"
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel
          question="Who covered the most ground?"
          tag={
            <PreviewTag
              what="distance"
              why="Estimated from tracked foot position. Jitter inflates it, so compare within a match rather than across venues."
            />
          }
          insights={movementInsights(match, who)}
        >
          <WorkRate match={match} ids={ids} />
        </Panel>

        <Panel
          question={`Where did ${p?.short} spend their energy?`}
          hint="Movement across the floor — the busier the area, the more ground covered there."
        >
          <div className="flex flex-wrap items-start justify-center gap-6">
            {match.players.map((pl) => (
              <figure key={pl.id} className="flex flex-col items-center gap-2">
                <figcaption className="flex items-center gap-1.5 text-sm font-[600] text-ink">
                  <RoleGlyph player={pl} />
                  {pl.short}
                </figcaption>
                <CourtHeatmap
                  heat={match.heatmaps.find((h) => h.player === pl.id && h.kind === "movement")}
                  player={pl}
                  kind="movement"
                  width={170}
                />
              </figure>
            ))}
          </div>
        </Panel>
      </div>

      <Panel
        question="How does this compare with your other matches?"
        hint="Your own history only — never anyone else's."
      >
        <div className="grid gap-5 md:grid-cols-2">
          {trends
            .filter((t) => t.id === "distance" || t.id === "avg-rally")
            .map((t) => (
              <div key={t.id} className="flex flex-col gap-1">
                <p className="text-sm font-[600] text-ink">{t.label}</p>
                <TrendLine points={t.points} unit={t.unit} label={t.label} />
              </div>
            ))}
        </div>
      </Panel>
    </div>
  );
}

/* ───────────────────────── head to head ───────────────────────── */

function H2HTab({ match, who }: { match: Match; who: PlayerId }) {
  return (
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
      <Panel
        question="How did the two sides compare?"
        hint="Totals per side. In doubles both partners are summed — switch to a single player with the picker above the tabs."
        insights={h2hInsights(match, who)}
      >
        <HeadToHead match={match} />
      </Panel>
      <div className="flex flex-col gap-5">
        <Panel
          question="Who is who?"
          hint="Colour and shape both carry the identity, so neither is load-bearing on its own."
        >
          <ul className="flex flex-col gap-3">
            {match.players.map((p) => {
              const st = match.stats[p.id];
              return (
                <li key={p.id} className="flex items-center gap-3">
                  <span
                    aria-hidden
                    className="flex size-9 shrink-0 items-center justify-center rounded-full"
                    style={{ background: `color-mix(in oklab, ${roleColour(p)} 18%, transparent)` }}
                  >
                    <RoleGlyph player={p} className="size-4" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-[600] text-ink">
                      {p.short}
                      {p.isYou && " (you)"}
                    </span>
                    <span className="block text-xs text-muted">
                      {match.sides[p.side].label} · {st?.shotsPlayed ?? 0} shots · {st?.distanceM ?? 0} m
                    </span>
                  </span>
                </li>
              );
            })}
          </ul>
        </Panel>
      </div>
    </div>
  );
}

/* ───────────────────────── doubles: the pair ───────────────────────── */

function PairTab({ match, who }: { match: Match; who: PlayerId }) {
  const me = match.players.find((p) => p.id === who) ?? youIn(match);
  const pair = match.pairs?.[me.side];
  const partner = match.players.find((p) => p.id !== me.id && p.side === me.side);
  if (!pair || !partner) {
    return (
      <StateShell
        kind="empty"
        title="This was a singles match"
        reason="Pair analytics appear on doubles matches."
      />
    );
  }
  const mine = pair.frontRear[me.id] ?? { front: 0, rear: 0 };
  const theirs = pair.frontRear[partner.id] ?? { front: 0, rear: 0 };

  return (
    <div className="flex flex-col gap-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile hero value={pair.bothContributed} unit="rallies" label="You both hit the shuttle" />
        <StatTile value={pair.rescues} unit="times" label="One of you covered the other" />
        <StatTile value={pair.attackCombos} unit="combos" label="Attack then net interception" />
        <StatTile value={pair.longestSharedRally} unit="shots" label="Longest rally you built together" />
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <Panel
          question={`How did you and ${partner.short} split the court?`}
          hint="Shots played from the front third against the rear third, for each of you."
          insights={pairInsights(match, who)}
        >
          <div className="flex flex-col gap-4">
            {[
              { p: me, v: mine },
              { p: partner, v: theirs },
            ].map(({ p, v }) => {
              const t = Math.max(1, v.front + v.rear);
              return (
                <div key={p.id} className="flex flex-col gap-1.5">
                  <span className="flex items-center justify-between text-sm">
                    <span className="flex items-center gap-1.5 font-[600] text-ink">
                      <RoleGlyph player={p} />
                      {p.short}
                    </span>
                    <span className="tabular text-muted">
                      {v.front} front · {v.rear} rear
                    </span>
                  </span>
                  <span className="flex h-6 overflow-hidden rounded-[6px]">
                    <span
                      className="flex items-center justify-center bg-you"
                      style={{ width: `${(v.front / t) * 100}%` }}
                    >
                      <span className="text-[11px] font-[600] text-canvas">front</span>
                    </span>
                    <span
                      className="flex items-center justify-center bg-other"
                      style={{ width: `${(v.rear / t) * 100}%` }}
                    >
                      <span className="text-[11px] font-[600] text-canvas">rear</span>
                    </span>
                  </span>
                </div>
              );
            })}
          </div>
        </Panel>

        <Panel
          question="Where did each of you stand?"
          hint="Both halves of your side, side by side — the shape of a pair is easier to see than to describe."
        >
          <div className="flex flex-wrap items-start justify-center gap-6">
            {[me, partner].map((pl) => (
              <figure key={pl.id} className="flex flex-col items-center gap-2">
                <figcaption className="flex items-center gap-1.5 text-sm font-[600] text-ink">
                  <RoleGlyph player={pl} />
                  {pl.short}
                </figcaption>
                <CourtHeatmap
                  heat={match.heatmaps.find((h) => h.player === pl.id && h.kind === "presence")}
                  player={pl}
                  kind="presence"
                  width={185}
                />
              </figure>
            ))}
          </div>
        </Panel>
      </div>

      <Panel
        question="Which moments were built by both of you?"
        hint="Rallies you won where both partners hit the shuttle."
      >
        <PartnerMoments match={match} side={me.side} />
      </Panel>
    </div>
  );
}

function PartnerMoments({ match, side }: { match: Match; side: "A" | "B" }) {
  const seek = usePlayer((s) => s.seek);
  const list = match.highlights.filter((h) => h.categories.includes("partner_play"));
  const fallback = match.rallies
    .filter((r) => r.official && r.winner === side && r.shots.length >= 8)
    .slice(0, 6);
  if (list.length === 0 && fallback.length === 0) {
    return <p className="text-sm text-muted">No rally yet where you both got involved.</p>;
  }
  return (
    <ul className="flex flex-wrap gap-2">
      {list.map((h) => (
        <li key={h.id}>
          <button
            type="button"
            onClick={() => seek(h.frames[0], h.title)}
            className="rounded-full border border-edge px-3 py-1.5 text-sm text-ink hover:border-edge-strong"
          >
            Rally {h.rallyNo} · {h.title}
          </button>
        </li>
      ))}
      {(list.length ? [] : fallback).map((r) => (
        <li key={r.no}>
          <button
            type="button"
            onClick={() => seek(r.frames[0], `Rally ${r.no} — ${r.shots.length} shots`)}
            className="rounded-full border border-edge px-3 py-1.5 text-sm text-muted hover:border-edge-strong hover:text-ink"
          >
            Rally {r.no} · {r.shots.length} shots
          </button>
        </li>
      ))}
    </ul>
  );
}

/* ───────────────────────── ask ───────────────────────── */

function AskTab({ match, who }: { match: Match; who: PlayerId }) {
  const seek = usePlayer((s) => s.seek);
  const [turns, setTurns] = useState<
    { id: string; q: string; a: string; cites: { label: string; frame: number }[] }[]
  >([]);
  const [q, setQ] = useState("");

  const answers = useMemo(() => buildAnswers(match, who), [match, who]);

  function ask(question: string) {
    const key = question.toLowerCase();
    const hit = answers.find((a) => a.match.some((m) => key.includes(m))) ?? {
      q: question,
      match: [],
      a: "I can only answer from what the analysis actually found in this match. Try one of the suggestions below — those all have evidence behind them.",
      cites: [] as { label: string; frame: number }[],
    };
    setTurns((t) => [...t, { id: `${t.length}-${question}`, q: question, a: hit.a, cites: hit.cites }]);
    setQ("");
  }

  return (
    <div className="flex max-w-[820px] flex-col gap-4">
      <Panel
        question="Ask about this match"
        hint="Every number in an answer comes from this match's data, and every answer links to the rally it came from."
      >
        <ul className="flex flex-col gap-4">
          {turns.map((t) => (
            <li key={t.id} className="flex flex-col gap-2">
              <p className="self-end rounded-[14px] rounded-br-sm bg-surface-raised px-4 py-2.5 text-sm text-ink">
                {t.q}
              </p>
              <div className="rounded-[14px] rounded-bl-sm border border-edge bg-surface px-4 py-3">
                <p className="text-base text-ink">{t.a}</p>
                {t.cites.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-2">
                    {t.cites.map((c) => (
                      <button
                        key={`${c.frame}-${c.label}`}
                        type="button"
                        onClick={() => seek(c.frame, c.label)}
                        className="inline-flex items-center gap-1.5 rounded-full border border-evidence/40 bg-evidence/8 px-3 py-1 text-xs font-medium text-evidence hover:bg-evidence/15"
                      >
                        <Play className="size-3 fill-current" aria-hidden />
                        {c.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
          {turns.length === 0 && (
            <li className="text-sm text-muted">
              Ask anything about this match. If there is no grounded answer, it says so rather than guessing.
            </li>
          )}
        </ul>
      </Panel>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (q.trim()) ask(q);
        }}
        className="flex gap-2"
      >
        <label htmlFor="ask" className="sr-only">
          Ask about this match
        </label>
        <input
          id="ask"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask about this match…"
          className="h-11 flex-1 rounded-[10px] border border-edge bg-surface px-3 text-base text-ink placeholder:text-faint focus:border-edge-strong focus:outline-none"
        />
        <Button type="submit" variant="primary" disabled={!q.trim()}>
          <Send className="size-4" aria-hidden />
          Ask
        </Button>
      </form>

      <div className="flex flex-wrap gap-2">
        {answers.map((a) => (
          <Chip key={a.q} onClick={() => ask(a.q)}>
            {a.q}
          </Chip>
        ))}
      </div>
    </div>
  );
}

/** Grounded answers, built from this match's derived numbers. */
function buildAnswers(match: Match, who: PlayerId) {
  const st = match.stats[who];
  const p = match.players.find((x) => x.id === who);
  const offs = match.rallies.filter((r) => r.official);
  const longest = offs.slice().sort((a, b) => b.shots.length - a.shots.length)[0];
  const partner = partnerIn(match);
  const opps = opponentsIn(match);
  const pair = p && match.pairs ? match.pairs[p.side] : undefined;
  const topZone = st
    ? (Object.entries(st.targetZones).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "the middle")
    : "the middle";

  const list: { q: string; match: string[]; a: string; cites: { label: string; frame: number }[] }[] = [
    {
      q: "What was my longest rally?",
      match: ["longest", "long rally"],
      a: longest
        ? `${longest.shots.length} shots, at ${mmss(longest.frames[0], match.fps)}. ${p?.short} played ${longest.shots.filter((s) => s.player === who).length} of them.`
        : "No counted rallies yet.",
      cites: longest ? [{ label: `The ${longest.shots.length}-shot rally`, frame: longest.frames[0] }] : [],
    },
    {
      q: "How did my defence hold up?",
      match: ["defence", "defend", "defensive"],
      a: st
        ? `${st.defensiveSaves} times you played from under the shuttle and stayed in the rally, out of ${st.familySplit.defend} defensive shots in total. ${st.returnsMade} of your ${st.returnsAttempted} returns kept the rally going.`
        : "",
      cites: (() => {
        const r = offs.find((x) => x.shots.some((s) => s.player === who && s.stroke === "lift"));
        return r ? [{ label: "A defensive rally", frame: r.frames[0] }] : [];
      })(),
    },
    {
      q: `Where did ${opps[0]?.short ?? "they"} attack me?`,
      match: ["attack me", "where did", "target"],
      a: (() => {
        const opp = opps[0] ? match.stats[opps[0].id] : undefined;
        if (!opp) return "I don't have enough on the other side to answer that.";
        const z = Object.entries(opp.targetZones).sort((a, b) => b[1] - a[1])[0];
        return `${opps[0]?.short} most often put the shuttle into your ${z?.[0]?.replace("-", " ")} — ${z?.[1]} of their ${opp.shotsPlayed} shots. They smashed ${opp.smashes} times and finished ${opp.smashPoints} rallies that way.`;
      })(),
      cites: (() => {
        const r = offs.find((x) => x.shots.some((s) => s.player === opps[0]?.id && s.stroke === "smash"));
        return r ? [{ label: "One of their smashes", frame: r.frames[0] }] : [];
      })(),
    },
    {
      q: "How much did I run?",
      match: ["run", "distance", "steps", "fitness"],
      a: st
        ? `About ${st.distanceM} m — roughly ${st.steps.toLocaleString()} steps — in ${(st.activeS / 60).toFixed(1)} minutes of actual play. That is an estimate from tracked position, not a fitness measurement.`
        : "",
      cites: [],
    },
    ...(partner && pair
      ? [
          {
            q: `Did ${partner.short} and I cover the court well?`,
            match: ["cover the court", "partner", partner.short.toLowerCase()],
            a: `You both hit the shuttle in ${pair.bothContributed} rallies, and ${pair.rescues} times one of you took over after the other was under pressure. The longest rally you built together ran to ${pair.longestSharedRally} shots.`,
            cites: (() => {
              const h = match.highlights.find((x) => x.categories.includes("partner_play"));
              return h ? [{ label: h.title, frame: h.frames[0] }] : [];
            })(),
          },
        ]
      : []),
    {
      q: "What should I practise?",
      match: ["practise", "practice", "improve", "better"],
      a: `I'm not able to coach — that needs a judgement I can't make from tracking alone. What I can tell you is what the data shows: your shots were met most often in the ${String(topZone).replace("-", " ")}, and ${st ? st.errorsOut + st.errorsNet : 0} rallies ended on your racket. Whether either is worth working on is your call, or a coach's.`,
      cites: [],
    },
  ];
  return list;
}
