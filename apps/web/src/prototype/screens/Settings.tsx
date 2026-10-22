import { clsx } from "clsx";
import { useState } from "react";
import { VENUE } from "../data/fixtures";
import { exportMyData } from "../lib/download";
import { useNavigate, useSearch } from "../nav";
import { type Theme, useStore } from "../store";
import { Button, Card, SegmentedControl, Sheet, Toggle } from "../ui/primitives";
import { Page } from "../ui/shell";

/* ─────────────────────────────────────────────────────────────────────────────
   Settings and privacy.

   The venue owns the footage and the cameras; the player owns their analysis and
   their clips. The page says which is which rather than offering a switch that
   cannot do what it implies.
   ───────────────────────────────────────────────────────────────────────────── */

const SECTIONS = [
  { id: "privacy", label: "Privacy" },
  { id: "data", label: "Your data" },
  { id: "display", label: "Display" },
  { id: "notifications", label: "Notifications" },
] as const;

type Section = (typeof SECTIONS)[number]["id"];

const VENUE_FACTS = [
  {
    label: `${VENUE} films Courts 1–6`,
    detail:
      "The venue owns these recordings and set the cameras up. We analyse them for you. To have an original recording deleted, ask the venue — we cannot do it from here.",
  },
  {
    label: "Recordings are kept for 30 days",
    detail:
      "After that the venue deletes the original. Clips and analysis you have kept stay with you until you delete them.",
  },
];

export function SettingsScreen() {
  const { s } = useSearch<{ s: Section }>({ from: "/settings" });
  const navigate = useNavigate();
  const active = s ?? "privacy";

  return (
    <Page title="Settings" lead="Private by default. Nothing is shared unless you choose to share it.">
      <div className="grid gap-6 lg:grid-cols-[180px_1fr] lg:gap-10">
        <nav aria-label="Settings sections" className="lg:sticky lg:top-20 lg:self-start">
          <ul className="-mx-4 flex gap-1 overflow-x-auto px-4 quiet-scroll lg:mx-0 lg:flex-col lg:px-0">
            {SECTIONS.map((sec) => (
              <li key={sec.id} className="shrink-0">
                <button
                  type="button"
                  aria-current={active === sec.id ? "page" : undefined}
                  onClick={() => navigate({ to: ".", search: { s: sec.id } })}
                  className={clsx(
                    "min-h-11 w-full rounded-[10px] px-3 text-left text-sm transition-colors",
                    active === sec.id
                      ? "bg-surface-raised font-[600] text-ink"
                      : "text-muted hover:bg-surface-raised hover:text-ink",
                  )}
                >
                  {sec.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>
        <div className="flex flex-col gap-5">
          {active === "privacy" && <Privacy />}
          {active === "data" && <Data />}
          {active === "display" && <Display />}
          {active === "notifications" && <Notifications />}
        </div>
      </div>
    </Page>
  );
}

function Privacy() {
  const consents = useStore((st) => st.consents);
  const setConsent = useStore((st) => st.setConsent);
  return (
    <>
      <h2 className="text-xl font-[650] text-ink">Your decisions</h2>
      <ul className="flex flex-col gap-3">
        {consents.map((c) => (
          <Card as="li" key={c.id} className="flex items-start gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-[600] text-ink">{c.label}</p>
              <p id={`c-${c.id}`} className="mt-1 text-sm text-muted">
                {c.consequence}
              </p>
              {c.blockedReason && (
                <p className="mt-2 rounded-[10px] bg-surface-raised px-3 py-2 text-sm text-uncertain">
                  {c.blockedReason}
                </p>
              )}
            </div>
            <Toggle
              checked={c.on && !c.blockedReason}
              disabled={Boolean(c.blockedReason)}
              onChange={(v) => setConsent(c.id, v)}
              label={c.label}
              describedBy={`c-${c.id}`}
            />
          </Card>
        ))}
      </ul>

      <h2 className="mt-3 text-xl font-[650] text-ink">What {VENUE} decided</h2>
      <p className="measure text-sm text-muted">
        These are the venue's decisions, shown so you know what they are — not switches we can flip for you.
      </p>
      <ul className="flex flex-col gap-3">
        {VENUE_FACTS.map((f) => (
          <Card as="li" key={f.label} className="flex items-start gap-4 bg-surface-raised">
            <div className="min-w-0 flex-1">
              <p className="font-[600] text-ink">{f.label}</p>
              <p className="mt-1 text-sm text-muted">{f.detail}</p>
            </div>
            <span className="shrink-0 rounded-full border border-edge px-2.5 py-1 text-xs text-muted">
              Venue
            </span>
          </Card>
        ))}
      </ul>
    </>
  );
}

function Data() {
  const store = useStore();
  const [confirm, setConfirm] = useState(false);
  const [done, setDone] = useState(false);

  const counts = {
    savedMoments: store.savedMoments.length,
    corrections: store.corrections.length,
    focus: store.focus.length,
    playlists: store.playlists.length,
    matchesIdentified: Object.keys(store.identity).length,
    nicknames: Object.keys(store.nicknames).length,
  };

  return (
    <>
      <h2 className="text-xl font-[650] text-ink">Your data</h2>
      <Card className="flex flex-col gap-3">
        <p className="font-[600] text-ink">What this device holds</p>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
          <dt className="text-muted">Saved moments</dt>
          <dd className="tabular text-ink">{counts.savedMoments}</dd>
          <dt className="text-muted">Corrections you made</dt>
          <dd className="tabular text-ink">{counts.corrections}</dd>
          <dt className="text-muted">Matches where you said who you are</dt>
          <dd className="tabular text-ink">{counts.matchesIdentified}</dd>
          <dt className="text-muted">Nicknames</dt>
          <dd className="tabular text-ink">{counts.nicknames}</dd>
          <dt className="text-muted">Focus items</dt>
          <dd className="tabular text-ink">{counts.focus}</dd>
          <dt className="text-muted">Coach playlists</dt>
          <dd className="tabular text-ink">{counts.playlists}</dd>
        </dl>
        <p className="text-sm text-muted">We do not hold the footage. That stays with {VENUE}.</p>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="secondary"
            onClick={() =>
              exportMyData({
                identity: store.identity,
                nicknames: store.nicknames,
                savedMoments: store.savedMoments,
                corrections: store.corrections,
                focus: store.focus,
                playlists: store.playlists,
                reflections: store.reflected,
                consents: store.consents.map((c) => ({ id: c.id, on: c.on })),
              })
            }
          >
            Download it as JSON
          </Button>
          <Button variant="danger" onClick={() => setConfirm(true)}>
            Delete everything on this device
          </Button>
        </div>
        {done && (
          <p className="rounded-[10px] bg-surface-raised px-3 py-2 text-sm text-ink">
            Done. Everything this device held is gone. The venue's recording and the analysis on the server
            are untouched — only {VENUE} can delete the footage.
          </p>
        )}
      </Card>

      <Sheet
        open={confirm}
        onClose={() => setConfirm(false)}
        title="Delete everything on this device?"
        description="This cannot be undone."
        footer={
          <div className="flex gap-2">
            <Button
              variant="danger"
              className="flex-1"
              onClick={() => {
                store.wipe();
                setConfirm(false);
                setDone(true);
              }}
            >
              Yes, delete it
            </Button>
            <Button variant="secondary" className="flex-1" onClick={() => setConfirm(false)}>
              Keep it
            </Button>
          </div>
        }
      >
        <ul className="flex list-disc flex-col gap-2 pl-5 text-sm text-muted">
          <li>
            {counts.savedMoments} saved moments, {counts.corrections} corrections, {counts.focus} focus items
            and {counts.playlists} playlists go.
          </li>
          <li>
            Who you are in {counts.matchesIdentified} matches is forgotten — you will be asked again next
            time.
          </li>
          <li>The analysis itself stays; this only clears what this device remembers.</li>
          <li>
            The venue's original recording is not affected. Only {VENUE} can delete that, and the front desk
            can do it for you.
          </li>
        </ul>
      </Sheet>
    </>
  );
}

function Display() {
  const { theme, setTheme, reduceMotion, setReduceMotion } = useStore();
  return (
    <>
      <h2 className="text-xl font-[650] text-ink">Display</h2>
      <Card className="flex flex-col gap-4">
        <div>
          <p className="font-[600] text-ink">Theme</p>
          <p className="mb-3 mt-1 text-sm text-muted">
            Your choice applies everywhere except the player's stage, which stays dark so the overlays stay
            readable.
          </p>
          <SegmentedControl
            value={theme}
            options={[
              { value: "system" as Theme, label: "System" },
              { value: "light" as Theme, label: "Light" },
              { value: "dark" as Theme, label: "Dark" },
            ]}
            onChange={setTheme}
            label="Theme"
          />
        </div>
      </Card>
      <Card className="flex items-start gap-4">
        <div className="flex-1">
          <p className="font-[600] text-ink">Keep animations off</p>
          <p className="mt-1 text-sm text-muted">
            For devices where the system setting isn't picked up. Nothing here needs motion to be understood.
          </p>
        </div>
        <Toggle checked={reduceMotion} onChange={setReduceMotion} label="Keep animations off" />
      </Card>
      <Card className="flex flex-col gap-2">
        <p className="font-[600] text-ink">Built in</p>
        <ul className="flex list-disc flex-col gap-1.5 pl-5 text-sm text-muted">
          <li>Everything works from the keyboard, including scrubbing frame by frame.</li>
          <li>No meaning is carried by colour alone — every player has a shape as well.</li>
          <li>Every chart has a table behind it.</li>
        </ul>
      </Card>
    </>
  );
}

function Notifications() {
  const consents = useStore((st) => st.consents);
  return (
    <>
      <h2 className="text-xl font-[650] text-ink">Notifications</h2>
      <Card className="flex flex-col gap-3">
        <p className="font-[600] text-ink">One message, when a match is ready</p>
        <p className="text-sm text-muted">
          Nothing else. There are no streak reminders, no "we miss you" messages and no nudges to come back.
          If you stop playing, we stop writing.
        </p>
      </Card>
      <p className="text-xs text-faint">{consents.length} privacy settings are on the Privacy tab.</p>
    </>
  );
}
