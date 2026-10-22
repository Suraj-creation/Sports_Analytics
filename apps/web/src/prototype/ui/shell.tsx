import { useRouterState } from "@tanstack/react-router";
import { clsx } from "clsx";
import {
  CircleUser,
  Clapperboard,
  House,
  LibraryBig,
  Monitor,
  Moon,
  Sun,
  TrendingUp,
  Users,
} from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { matches } from "../data/fixtures";
import { Link } from "../nav";
import { useStore } from "../store";
import { Logo } from "./art";
import { Button, LiveRegion } from "./primitives";
import { MatchStatusChip } from "./states";

const NAV = [
  { to: "/", label: "Home", icon: House },
  { to: "/matches", label: "Matches", icon: LibraryBig },
  { to: "/moments", label: "Moments", icon: Clapperboard },
  { to: "/progress", label: "Progress", icon: TrendingUp },
  { to: "/people", label: "People", icon: Users },
] as const;

/* ─────────────────────────────────────────────────────────────────────────────
   AppShell.

   No ＋ button: players do not upload (DESIGN_DIRECTION C7). Four equal tabs on a
   phone, a 240px SideNav from 1024, an icon rail between. The one cross-page status
   indicator is the running-analysis pill in the header (04 §4.3).
   ───────────────────────────────────────────────────────────────────────────── */

export function AppShell({ children }: { children: ReactNode }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const h1 = useRef<HTMLDivElement>(null);
  const [announce, setAnnounce] = useState("");
  const analysing = matches.filter((m) => m.status === "analysing");

  useEffect(() => {
    // Focus moves to the page heading on navigation, with a polite announcement (04 §4.7).
    const heading = h1.current?.querySelector<HTMLElement>("h1");
    if (heading) {
      heading.setAttribute("tabindex", "-1");
      heading.focus({ preventScroll: true });
      setAnnounce(`${heading.textContent ?? "Page"}, loaded`);
    }
  }, []);

  // The landing page carries no app chrome — there is nothing to navigate yet.
  if (path.startsWith("/welcome")) {
    return (
      <div className="min-h-full bg-canvas">
        <LiveRegion message={announce} />
        <div ref={h1}>{children}</div>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-canvas">
      <LiveRegion message={announce} />
      <a
        href="#content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-[10px] focus:bg-surface focus:px-4 focus:py-2 focus:text-ink"
      >
        Skip to content
      </a>

      <div className="lg:flex">
        {/* ── SideNav (>=1024) / Rail (768-1023) ── */}
        <nav
          aria-label="Main"
          className="sticky top-0 z-30 hidden h-screen shrink-0 flex-col gap-1 border-r border-edge bg-surface px-3 py-4 md:flex md:w-[76px] lg:w-[240px] lg:px-4"
        >
          <Link to="/" className="mb-4 flex items-center gap-2.5 rounded-[10px] px-1 py-1">
            <Logo className="size-8 shrink-0" />
            <span className="hidden text-lg font-[700] tracking-tight text-ink lg:inline">Rally</span>
          </Link>

          {NAV.map(({ to, label, icon: Icon }) => (
            <NavItem key={to} to={to} label={label} icon={Icon} active={isActive(path, to)} />
          ))}

          <hr className="my-3 border-edge" />

          <div className="mt-auto flex flex-col gap-1">
            <ThemeSwitcher />
            <NavItem to="/settings" label="Settings" icon={CircleUser} active={isActive(path, "/settings")} />
          </div>
        </nav>

        <div className="flex min-w-0 flex-1 flex-col">
          {/* ── header ── */}
          <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-edge bg-canvas/95 px-4 py-2.5 backdrop-blur md:px-6">
            <Link to="/" className="flex items-center gap-2 md:hidden">
              <Logo className="size-7" />
              <span className="text-base font-[700] text-ink">Rally</span>
            </Link>
            <div className="ml-auto flex items-center gap-2">
              {analysing.map((m) => (
                <Link
                  key={m.id}
                  to="/matches/$matchId"
                  params={{ matchId: m.id }}
                  search={{ tab: "overview" }}
                  className="hidden items-center gap-2 rounded-full border border-edge bg-surface px-3 py-1.5 text-xs text-ink hover:border-edge-strong sm:inline-flex"
                >
                  <span className="max-w-[140px] truncate">{m.title}</span>
                  <MatchStatusChip status={m.status} progress={m.progress} className="border-0 px-0" />
                </Link>
              ))}
              <Link
                to="/help"
                className="rounded-[10px] px-3 py-2 text-sm text-muted hover:bg-surface-raised hover:text-ink"
              >
                Help
              </Link>
              <Link
                to="/settings"
                aria-label="Settings and privacy"
                className="flex size-10 items-center justify-center rounded-full border border-edge bg-surface text-sm font-[600] text-ink md:hidden"
              >
                A
              </Link>
            </div>
          </header>

          <main id="content" ref={h1} className="flex-1 pb-[calc(72px+env(safe-area-inset-bottom))] md:pb-10">
            {children}
          </main>
        </div>
      </div>

      {/* ── BottomBar (<768): four equal tabs, labels always visible ── */}
      <nav
        aria-label="Main"
        className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-5 border-t border-edge bg-surface pb-[env(safe-area-inset-bottom)] md:hidden"
      >
        {NAV.map(({ to, label, icon: Icon }) => {
          const active = isActive(path, to);
          return (
            <Link
              key={to}
              to={to}
              aria-current={active ? "page" : undefined}
              className={clsx(
                "flex min-h-[56px] flex-col items-center justify-center gap-0.5 text-xs",
                active ? "font-[600] text-ink" : "text-muted",
              )}
            >
              <Icon className={clsx("size-5", active && "stroke-[2.2]")} aria-hidden />
              {label}
              {active && <span aria-hidden className="mt-0.5 h-0.5 w-5 rounded-full bg-ink" />}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}

function isActive(path: string, to: string) {
  return to === "/" ? path === "/" : path.startsWith(to);
}

function NavItem({
  to,
  label,
  icon: Icon,
  active,
  soon,
}: {
  to: string;
  label: string;
  icon: typeof House;
  active: boolean;
  soon?: boolean;
}) {
  const content = (
    <>
      <Icon className="size-5 shrink-0" aria-hidden />
      <span className="hidden lg:inline">{label}</span>
      {soon && (
        <span className="ml-auto hidden rounded-full border border-edge px-1.5 py-0.5 text-[11px] text-faint lg:inline">
          Soon
        </span>
      )}
    </>
  );
  const cls = clsx(
    "flex min-h-11 items-center gap-3 rounded-[10px] px-2.5 text-sm transition-colors duration-150 lg:px-3",
    "md:justify-center lg:justify-start",
    active ? "bg-surface-raised font-[600] text-ink" : "text-muted hover:bg-surface-raised hover:text-ink",
    soon && "opacity-70",
  );
  if (soon) {
    return (
      <span className={cls} title={`${label} — not yet available`}>
        {content}
      </span>
    );
  }
  return (
    <Link to={to} aria-current={active ? "page" : undefined} className={cls} title={label}>
      {content}
    </Link>
  );
}

function ThemeSwitcher() {
  const theme = useStore((s) => s.theme);
  const setTheme = useStore((s) => s.setTheme);
  const next = theme === "system" ? "light" : theme === "light" ? "dark" : "system";
  const Icon = theme === "system" ? Monitor : theme === "light" ? Sun : Moon;
  return (
    <button
      type="button"
      onClick={() => setTheme(next)}
      className="flex min-h-11 items-center gap-3 rounded-[10px] px-2.5 text-sm text-muted hover:bg-surface-raised hover:text-ink md:justify-center lg:justify-start lg:px-3"
      title={`Theme: ${theme}. Switch to ${next}.`}
    >
      <Icon className="size-5 shrink-0" aria-hidden />
      <span className="hidden capitalize lg:inline">{theme} theme</span>
    </button>
  );
}

/* ───────────────────────────── page scaffolding ───────────────────────────── */

export function Page({
  title,
  lead,
  actions,
  width = "default",
  children,
}: {
  /** Omit when the screen renders its own h1 (e.g. MatchHeader) — there is one h1 per route. */
  title?: string;
  lead?: ReactNode;
  actions?: ReactNode;
  width?: "default" | "wide" | "form";
  children: ReactNode;
}) {
  return (
    <div
      className={clsx(
        "mx-auto w-full px-4 py-6 md:px-6 md:py-8",
        width === "default" && "max-w-[1120px]",
        width === "wide" && "max-w-[1680px]",
        width === "form" && "max-w-[640px]",
      )}
    >
      {title && (
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-[length:var(--text-2xl)] font-[700] leading-tight text-ink md:text-3xl">
              {title}
            </h1>
            {lead && <div className="measure mt-2 text-muted">{lead}</div>}
          </div>
          {actions}
        </div>
      )}
      {children}
    </div>
  );
}

export function NotFound() {
  return (
    <Page title="We couldn't find that page">
      <p className="measure text-muted">
        The link may be old, or the match may have been deleted. Nothing is wrong with your account.
      </p>
      <div className="mt-6 flex gap-2">
        <Link to="/">
          <Button variant="primary">Go to Home</Button>
        </Link>
        <Link to="/matches">
          <Button variant="secondary">See your matches</Button>
        </Link>
      </div>
    </Page>
  );
}
