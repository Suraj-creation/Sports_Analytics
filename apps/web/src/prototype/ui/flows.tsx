import { clsx } from "clsx";
import { Check, Download, FileText, Link2, Share2, Users, Wrench } from "lucide-react";
import { useState } from "react";
import type { Highlight, Match, PlayerId, Rally } from "../data/types";
import { exportEventsJsonl, exportRalliesCsv, exportSummaryJson } from "../lib/download";
import type { Correction } from "../store";
import { useStore } from "../store";
import { mmss, RoleGlyph } from "./analytics";
import { Button, Card, Chip, Sheet, Toggle } from "./primitives";

/* ─────────────────────────────────────────────────────────────────────────────
   The flows that sit around the analytics: who you are, fixing what is wrong,
   sharing it, checking how reliable it is, and getting it out.
   ───────────────────────────────────────────────────────────────────────────── */

/* ───────────────────────── which one is you? ─────────────────────────
   The single most important interaction in the product: every "you" downstream
   hangs off it, and in doubles you have to pick yourself out of four people. */

export function IdentitySheet({
  match,
  open,
  onClose,
}: {
  match: Match;
  open: boolean;
  onClose: () => void;
}) {
  const setIdentity = useStore((s) => s.setIdentity);
  const setNickname = useStore((s) => s.setNickname);
  const nicknames = useStore((s) => s.nicknames);
  const current = useStore((s) => s.identity[match.id]);
  const [picked, setPicked] = useState<PlayerId | null>(current ?? null);
  const [step, setStep] = useState<1 | 2>(1);

  const chosen = match.players.find((p) => p.id === picked);
  const others = match.players.filter((p) => p.id !== picked);

  return (
    <Sheet
      open={open}
      onClose={onClose}
      wide
      title={step === 1 ? "Which one is you?" : "Who else was on court?"}
      description={
        step === 1
          ? "Everything after this — your shots, your court map, your distance — depends on this answer."
          : "A name for each person, just for you. It never appears in a link or an export."
      }
      footer={
        step === 1 ? (
          <Button
            variant="primary"
            className="w-full"
            disabled={!picked}
            onClick={() => {
              if (picked) setIdentity(match.id, picked);
              setStep(2);
            }}
          >
            That's me
          </Button>
        ) : (
          <Button variant="primary" className="w-full" onClick={onClose}>
            Done
          </Button>
        )
      }
    >
      {step === 1 ? (
        <div className="flex flex-col gap-4">
          {/* The court as the camera sees it, with each player tappable. */}
          <div className="relative overflow-hidden rounded-[14px] bg-well">
            <svg viewBox="0 0 320 190" className="w-full" aria-hidden>
              <rect width="320" height="190" fill="#0c2620" />
              <path d="M112 38 L208 38 L280 176 L40 176 Z" fill="#14382f" />
              <g stroke="rgb(232 239 234 / 0.4)" strokeWidth="1" fill="none">
                <path d="M112 38 L208 38 L280 176 L40 176 Z" />
                <path d="M94 94 L226 94" strokeWidth="1.8" stroke="rgb(232 239 234 / 0.6)" />
                <path d="M124 62 L196 62" />
                <path d="M76 136 L244 136" />
              </g>
            </svg>
            {match.players.map((p) => {
              const near = p.end === "near";
              const sideIdx = match.sides[p.side].players.indexOf(p.id);
              const left = match.discipline === "doubles" ? (sideIdx === 0 ? 38 : 62) : 50;
              const top = near ? 70 : 30;
              return (
                <button
                  key={p.id}
                  type="button"
                  aria-pressed={picked === p.id}
                  aria-label={`${p.name}, at the ${near ? "near" : "far"} end`}
                  onClick={() => setPicked(p.id)}
                  className={clsx(
                    "absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-1 rounded-full border-2 p-2 transition-colors",
                    near ? "size-20" : "size-16",
                    picked === p.id
                      ? "border-[#4fd6c4] bg-[#4fd6c4]/25"
                      : "border-white/40 bg-white/5 hover:bg-white/15",
                  )}
                  style={{ left: `${left}%`, top: `${top}%` }}
                >
                  <span
                    aria-hidden
                    className={clsx(
                      "rounded-full",
                      near ? "size-4" : "size-3",
                      picked === p.id ? "bg-[#4fd6c4]" : "bg-white/70",
                    )}
                  />
                  <span className="text-[11px] text-white">{p.name}</span>
                </button>
              );
            })}
            <span className="absolute bottom-1.5 left-2 rounded bg-black/70 px-1.5 py-0.5 text-[11px] text-[#8da098]">
              Stand-in frame — a real one would show the players
            </span>
          </div>

          <ul className="flex flex-col gap-2">
            {match.players.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  onClick={() => setPicked(p.id)}
                  aria-pressed={picked === p.id}
                  className={clsx(
                    "flex w-full items-center gap-3 rounded-[10px] border px-3 py-2.5 text-left",
                    picked === p.id ? "border-ink bg-surface-raised" : "border-edge hover:border-edge-strong",
                  )}
                >
                  <RoleGlyph player={p} className="size-3" />
                  <span className="flex-1 text-sm text-ink">
                    {nicknames[p.id] ?? p.name}
                    <span className="ml-2 text-xs text-muted">
                      {p.end === "near" ? "near end" : "far end"} · {match.stats[p.id]?.shotsPlayed ?? 0}{" "}
                      shots
                    </span>
                  </span>
                  {picked === p.id && <Check className="size-4 text-ink" aria-hidden />}
                </button>
              </li>
            ))}
          </ul>
          <p className="text-xs text-faint">
            Not sure? Pick the one you think is you and change it later from the match menu — nothing is lost
            when you do.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {chosen && (
            <p className="text-sm text-muted">
              You are <strong className="text-ink">{chosen.name}</strong>, at the{" "}
              {chosen.end === "near" ? "near" : "far"} end.
            </p>
          )}
          {others.map((p) => (
            <label key={p.id} className="flex flex-col gap-1.5">
              <span className="flex items-center gap-2 text-sm font-[600] text-ink">
                <RoleGlyph player={p} className="size-3" />
                {p.side === chosen?.side ? "Your partner" : "Opponent"} — currently "{p.name}"
              </span>
              <input
                defaultValue={nicknames[p.id] ?? p.name}
                onChange={(e) => setNickname(p.id, e.target.value)}
                className="h-11 rounded-[10px] border border-edge bg-surface px-3 text-base text-ink focus:border-edge-strong focus:outline-none"
              />
            </label>
          ))}
          <p className="text-xs text-faint">
            Use whatever you'd call them. Don't use a full legal name — these stay on this device.
          </p>
        </div>
      )}
    </Sheet>
  );
}

/* ───────────────────────── corrections ─────────────────────────
   The engine supports exactly four corrections. These are those four, and nothing
   that looks like a fifth. Changing a winner refolds every score after it, which is
   the part people do not expect, so the sheet says so before and after. */

export function CorrectionControls({
  match,
  rally,
  onDone,
}: {
  match: Match;
  rally: Rally;
  onDone?: () => void;
}) {
  const addCorrection = useStore((s) => s.addCorrection);
  const corrections = useStore((s) => s.corrections);
  const mine = corrections.find((c) => c.matchId === match.id && c.rallyNo === rally.no);
  const winnerLabel = rally.winner ? match.sides[rally.winner].label : "nobody";
  const otherSide = rally.winner === "A" ? "B" : "A";
  const laterRallies = match.rallies.filter((r) => r.official && r.no > rally.no).length;

  if (mine) {
    return (
      <div className="corrected-tint rounded-[10px] border border-corrected/40 px-3 py-2">
        <p className="flex items-center gap-1.5 text-sm font-[600] text-corrected">
          <span aria-hidden>✎</span> {mine.summary}
        </p>
        <p className="mt-0.5 text-xs text-muted">{mine.knockOn}</p>
      </div>
    );
  }

  const apply = (kind: Correction["kind"], summary: string, knockOn: string) => {
    addCorrection({ matchId: match.id, rallyNo: rally.no, kind, summary, knockOn });
    onDone?.();
  };

  return (
    <div className="flex flex-col gap-2 rounded-[10px] border border-edge bg-surface-raised px-3 py-2.5">
      <p className="text-xs font-[600] text-ink">Is this right?</p>
      <p className="text-xs text-muted">
        We have {winnerLabel} winning this rally because {rally.endReason}.
      </p>
      <div className="flex flex-wrap gap-1.5">
        <Button
          size="sm"
          variant="secondary"
          onClick={() =>
            apply(
              "confirm_winner",
              `Rally ${rally.no}: you confirmed ${winnerLabel} won it.`,
              "Nothing else changed — confirming matches what we already had.",
            )
          }
        >
          Yes, {winnerLabel} won
        </Button>
        <Button
          size="sm"
          variant="secondary"
          onClick={() =>
            apply(
              "change_winner",
              `Rally ${rally.no}: changed to ${match.sides[otherSide].label}.`,
              `Every score after it was recalculated — ${laterRallies} later rallies shift by one point.`,
            )
          }
        >
          No, {match.sides[otherSide].label} won
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() =>
            apply(
              rally.official ? "not_counted" : "counted",
              rally.official
                ? `Rally ${rally.no}: marked as a warm-up, not counted.`
                : `Rally ${rally.no}: counted into the match.`,
              rally.official
                ? "It stays on the timeline but leaves the score and every statistic."
                : "It now counts toward the score and the statistics.",
            )
          }
        >
          {rally.official ? "Not part of the match" : "Count this one"}
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() =>
            apply(
              "match_start",
              `The match now starts at rally ${rally.no}.`,
              "Everything before it became warm-up and left the score.",
            )
          }
        >
          Match starts here
        </Button>
      </div>
      <p className="text-xs text-faint">
        Changing a winner refolds the score for every rally after this one. There is no undo yet — the server
        cannot reverse a refold, so we do not offer a button that would not work.
      </p>
    </div>
  );
}

/** What changed, after any correction on this match. */
export function ChangeSummary({ matchId }: { matchId: string }) {
  const corrections = useStore((s) => s.corrections).filter((c) => c.matchId === matchId);
  if (corrections.length === 0) return null;
  return (
    <div className="flex items-start gap-3 rounded-[14px] border border-corrected/40 bg-surface p-4">
      <span aria-hidden className="mt-0.5 text-corrected">
        ✎
      </span>
      <div className="min-w-0">
        <p className="font-[600] text-ink">
          {corrections.length === 1 ? "One thing changed" : `${corrections.length} things changed`}
        </p>
        <ul className="mt-1.5 flex flex-col gap-1.5 text-sm text-muted">
          {corrections.map((c) => (
            <li key={c.id}>
              <span className="text-ink">{c.summary}</span> {c.knockOn}
            </li>
          ))}
        </ul>
        <p className="mt-2 text-xs text-faint">
          In this prototype the corrections are recorded but the numbers above are not refolded — doing that
          honestly needs the server to recompute the whole match.
        </p>
      </div>
    </div>
  );
}

/** "Alex, Rahul and Meera" — not "Alex and Rahul and Meera". */
function listOf(names: string[]): string {
  if (names.length <= 1) return names[0] ?? "";
  return `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
}

/* ───────────────────────── share ─────────────────────────
   Preview the actual clip and the actual people in it, not a label. */

export function SharePreviewDialog({
  match,
  highlight,
  open,
  onClose,
}: {
  match: Match;
  highlight: Highlight | null;
  open: boolean;
  onClose: () => void;
}) {
  const consents = useStore((s) => s.consents);
  const nicknames = useStore((s) => s.nicknames);
  const [audio, setAudio] = useState<"stripped" | "kept">("stripped");
  const [audience, setAudience] = useState<"link" | "person" | "coach">("person");
  const [approved, setApproved] = useState<Record<string, boolean>>({});
  const canShare = consents.find((c) => c.id === "share")?.on ?? false;

  if (!highlight) return null;
  // Everyone visible in the clip, not only the credited player.
  const inClip = match.players.filter((p) =>
    match.rallies.find((r) => r.no === highlight.rallyNo)?.shots.some((s) => s.player === p.id),
  );
  const needed = inClip.filter((p) => !p.isYou);
  const allApproved = needed.every((p) => approved[p.id]);

  return (
    <Sheet
      open={open}
      onClose={onClose}
      title="Share this moment"
      description="Check what you are about to send, and who is in it."
      footer={
        <div className="flex flex-col gap-2">
          <Button variant="primary" className="w-full" disabled={!canShare || !allApproved}>
            <Link2 className="size-4" aria-hidden />
            Create a link
          </Button>
          <p className="text-center text-xs text-faint">
            {!canShare
              ? "Sharing is off in Settings → Privacy."
              : !allApproved
                ? `Waiting on ${listOf(
                    needed.filter((p) => !approved[p.id]).map((p) => nicknames[p.id] ?? p.short),
                  )}.`
                : "No link is minted in this prototype — the server has to enforce expiry and revocation."}
          </p>
        </div>
      }
    >
      <div className="flex flex-col gap-5">
        <div className="rounded-[10px] border border-edge bg-surface-raised p-4">
          <p className="font-[600] text-ink">{highlight.title}</p>
          <p className="mt-1 text-sm text-muted">
            Rally {highlight.rallyNo} · {mmss(highlight.frames[0], match.fps)} · {highlight.durationS}s ·{" "}
            {match.title}
          </p>
        </div>

        <div>
          <p className="mb-2 flex items-center gap-2 text-sm font-[600] text-ink">
            <Users className="size-4" aria-hidden />
            Who is in this clip
          </p>
          <ul className="flex flex-col gap-2">
            {inClip.map((p) => (
              <li key={p.id} className="flex items-center gap-3 rounded-[10px] border border-edge px-3 py-2">
                <RoleGlyph player={p} className="size-3" />
                <span className="flex-1 text-sm text-ink">
                  {nicknames[p.id] ?? p.short}
                  {p.isYou && " (you)"}
                </span>
                {p.isYou ? (
                  <span className="text-xs text-muted">your clip</span>
                ) : (
                  <Toggle
                    checked={Boolean(approved[p.id])}
                    onChange={(v) => setApproved((a) => ({ ...a, [p.id]: v }))}
                    label={`${p.short} approves`}
                  />
                )}
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-faint">
            Everyone visible has to approve, not only the person the moment credits. In the real product this
            is a request they answer, not a switch you flip.
          </p>
        </div>

        <div>
          <p className="mb-2 text-sm font-[600] text-ink">Who can open it</p>
          <div className="flex flex-wrap gap-2">
            <Chip selected={audience === "person"} onClick={() => setAudience("person")}>
              One person
            </Chip>
            <Chip selected={audience === "coach"} onClick={() => setAudience("coach")}>
              A coach
            </Chip>
            <Chip selected={audience === "link"} onClick={() => setAudience("link")}>
              Anyone with the link
            </Chip>
          </div>
          <p className="mt-2 text-xs text-faint">
            {audience === "link"
              ? "A link can be forwarded. It expires in 7 days and you can revoke it."
              : "Only that person, and it expires in 7 days."}
          </p>
        </div>

        <div>
          <p className="mb-2 text-sm font-[600] text-ink">Sound</p>
          <div className="flex gap-2">
            <Chip selected={audio === "stripped"} onClick={() => setAudio("stripped")}>
              Remove sound
            </Chip>
            <Chip selected={audio === "kept"} onClick={() => setAudio("kept")}>
              Keep sound
            </Chip>
          </div>
          <p className="mt-2 text-xs text-faint">
            Sound is removed by default — a court picks up other people's conversations.
          </p>
        </div>
      </div>
    </Sheet>
  );
}

/* ───────────────────────── quality ─────────────────────────
   Coverage, label reliability, model version and corrections in one place.
   Three different signals that are easy to conflate, so they are listed apart. */

export function QualityPanel({ match, open, onClose }: { match: Match; open: boolean; onClose: () => void }) {
  const corrections = useStore((s) => s.corrections).filter((c) => c.matchId === match.id);
  const followedPct = Math.round((match.coverage.followed / Math.max(1, match.coverage.total)) * 100);

  const capabilities = [
    {
      name: "Rally boundaries",
      state: "Working",
      detail: "Start and end of each rally from shuttle motion and contacts.",
    },
    {
      name: "Shot naming",
      state: "Preview",
      detail: "Rule-based classifier, not validated on this venue's camera angle.",
    },
    {
      name: "Court position",
      state: "Working",
      detail: "Calibrated once per camera. Accuracy drops if the camera is moved.",
    },
    {
      name: "Where shots were met",
      state: "Preview",
      detail: "The receiver's position, not the shuttle's landing point — no flight model.",
    },
    {
      name: "Distance and steps",
      state: "Preview",
      detail: "Summed tracked position; jitter inflates it. Steps derived at a 0.78 m stride.",
    },
    {
      name: "Doubles roles",
      state: "Preview",
      detail: "Front and rear inferred from position. Intent and communication are not observable.",
    },
  ];

  return (
    <Sheet
      open={open}
      onClose={onClose}
      wide
      title="How reliable is this?"
      description="Coverage, capability and corrections are three different things. They are listed separately so one does not get read as the other."
    >
      <div className="flex flex-col gap-5">
        <section className="flex flex-col gap-2">
          <h3 className="text-sm font-[600] text-ink">Coverage — how much we could follow</h3>
          <div className="flex h-2.5 overflow-hidden rounded-full bg-surface-raised">
            <span className="bg-you" style={{ width: `${followedPct}%` }} />
            <span className="hatch flex-1" />
          </div>
          <p className="text-sm text-muted">
            We followed {match.coverage.followed} of {match.coverage.total} rallies ({followedPct}%).{" "}
            {match.coverage.reason}
          </p>
          <p className="text-xs text-faint">
            Rallies we could not follow are excluded from every figure rather than estimated.
          </p>
        </section>

        <section className="flex flex-col gap-2">
          <h3 className="text-sm font-[600] text-ink">Capability — what each part can do</h3>
          <ul className="flex flex-col divide-y divide-edge rounded-[10px] border border-edge">
            {capabilities.map((c) => (
              <li key={c.name} className="flex items-start gap-3 px-3 py-2.5">
                <span
                  className={clsx(
                    "mt-0.5 shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium",
                    c.state === "Preview" ? "border-uncertain/60 text-uncertain" : "border-edge text-muted",
                  )}
                >
                  {c.state}
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-[600] text-ink">{c.name}</span>
                  <span className="block text-sm text-muted">{c.detail}</span>
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section className="flex flex-col gap-2">
          <h3 className="text-sm font-[600] text-ink">Provenance</h3>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
            <dt className="text-muted">Camera</dt>
            <dd className="text-ink">
              {match.venue}, {match.court} — fixed rig
            </dd>
            <dt className="text-muted">Frame rate</dt>
            <dd className="tabular text-ink">{match.fps} fps</dd>
            <dt className="text-muted">Frames analysed</dt>
            <dd className="tabular text-ink">{match.nFrames.toLocaleString()}</dd>
            <dt className="text-muted">Shots detected</dt>
            <dd className="tabular text-ink">
              {match.rallies.reduce((a, r) => a + r.shots.length, 0).toLocaleString()}
            </dd>
            <dt className="text-muted">Pipeline</dt>
            <dd className="text-ink">prototype fixtures — no model ran</dd>
          </dl>
        </section>

        <section className="flex flex-col gap-2">
          <h3 className="text-sm font-[600] text-ink">Corrections you have made</h3>
          {corrections.length === 0 ? (
            <p className="text-sm text-muted">
              None yet. Open any rally and check the winner if one looks wrong.
            </p>
          ) : (
            <ul className="flex flex-col gap-1.5 text-sm text-muted">
              {corrections.map((c) => (
                <li key={c.id}>
                  <span className="text-corrected">✎</span> {c.summary} {c.knockOn}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </Sheet>
  );
}

/* ───────────────────────── export ───────────────────────── */

export function ExportSheet({ match, open, onClose }: { match: Match; open: boolean; onClose: () => void }) {
  const rows = [
    {
      name: "Rallies (CSV)",
      detail: "One row per rally: times, shot count, server, winner, outcome, score.",
      run: () => exportRalliesCsv(match),
      ready: true,
    },
    {
      name: "Events (JSONL)",
      detail: "Every rally and every shot as a newline-delimited event, with provenance.",
      run: () => exportEventsJsonl(match),
      ready: true,
    },
    {
      name: "Summary (JSON)",
      detail: "The aggregate: per-player stats, pair stats, coverage and match metadata.",
      run: () => exportSummaryJson(match),
      ready: true,
    },
    {
      name: "Match report (PDF)",
      detail: "The rendered report. This one is generated on the server, so it is not available here.",
      run: () => {},
      ready: false,
    },
    {
      name: "Clips (MP4)",
      detail:
        "Each moment as a file. Needs the server's clip export, and everyone in the clip to approve it.",
      run: () => {},
      ready: false,
    },
  ];

  return (
    <Sheet
      open={open}
      onClose={onClose}
      title="Export this match"
      description="The data behind every chart on this page, in the formats the engine already produces."
    >
      <ul className="flex flex-col gap-2">
        {rows.map((r) => (
          <li key={r.name} className="flex items-start gap-3 rounded-[10px] border border-edge px-3 py-2.5">
            <FileText className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-[600] text-ink">{r.name}</span>
              <span className="block text-sm text-muted">{r.detail}</span>
            </span>
            <Button size="sm" variant={r.ready ? "secondary" : "ghost"} disabled={!r.ready} onClick={r.run}>
              <Download className="size-4" aria-hidden />
              {r.ready ? "Download" : "Server only"}
            </Button>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-faint">
        These files are generated from the prototype's fixture data. They are real files with real structure,
        but nothing in them was measured.
      </p>
    </Sheet>
  );
}

/* ───────────────────────── reflection ─────────────────────────
   Blueprint §7.11: ask what the player noticed BEFORE showing the numbers.
   Skippable, asked once, never repeated. */

export function ReflectionPrompt({ match }: { match: Match }) {
  const reflected = useStore((s) => s.reflected[match.id]);
  const setReflection = useStore((s) => s.setReflection);
  if (reflected) return null;
  const options = ["Better than it felt", "About right", "Worse than it felt", "No idea"];
  return (
    <Card className="flex flex-col gap-3">
      <div>
        <p className="text-base font-[650] text-ink">Before you look — how did it feel?</p>
        <p className="mt-1 text-sm text-muted">
          Worth answering first: comparing what you remember with what the data says is more useful than
          reading the data cold. Skip it if you'd rather not.
        </p>
      </div>
      <div className="flex flex-wrap gap-2">
        {options.map((o) => (
          <Chip key={o} onClick={() => setReflection(match.id, o)}>
            {o}
          </Chip>
        ))}
        <Button size="sm" variant="ghost" onClick={() => setReflection(match.id, "skipped")}>
          Skip
        </Button>
      </div>
    </Card>
  );
}

/* ───────────────────────── coach playlist ─────────────────────────
   Blueprint §7.14: a playlist carries ONE question, not a list of faults. */

export function PlaylistDialog({
  open,
  onClose,
  momentIds,
  momentTitles,
}: {
  open: boolean;
  onClose: () => void;
  momentIds: string[];
  momentTitles: string[];
}) {
  const addPlaylist = useStore((s) => s.addPlaylist);
  const [name, setName] = useState("");
  const [question, setQuestion] = useState("");

  return (
    <Sheet
      open={open}
      onClose={onClose}
      title="Send these to a coach"
      description="A playlist carries one question. A list of faults is not a conversation."
      footer={
        <Button
          variant="primary"
          className="w-full"
          disabled={!name.trim() || !question.trim()}
          onClick={() => {
            addPlaylist({ name: name.trim(), question: question.trim(), momentIds });
            setName("");
            setQuestion("");
            onClose();
          }}
        >
          <Share2 className="size-4" aria-hidden />
          Create the playlist
        </Button>
      }
    >
      <div className="flex flex-col gap-4">
        <p className="text-sm text-muted">{momentIds.length} moments selected:</p>
        <ul className="flex flex-wrap gap-1.5">
          {momentTitles.map((t) => (
            <li key={t} className="rounded-full bg-surface-raised px-2.5 py-1 text-xs text-ink">
              {t}
            </li>
          ))}
        </ul>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-[600] text-ink">Call it something</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Net exchanges, Sunday"
            className="h-11 rounded-[10px] border border-edge bg-surface px-3 text-base text-ink placeholder:text-faint focus:border-edge-strong focus:outline-none"
          />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-[600] text-ink">Your one question</span>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            placeholder="Am I standing too close to the net when I lift?"
            className="rounded-[10px] border border-edge bg-surface px-3 py-2 text-base text-ink placeholder:text-faint focus:border-edge-strong focus:outline-none"
          />
        </label>
        <p className="text-xs text-faint">
          Access is per playlist, expires in 30 days and you can revoke it. A coach never gets your whole
          history. In this prototype the playlist is saved locally and nothing is sent.
        </p>
      </div>
    </Sheet>
  );
}

export { Wrench };
