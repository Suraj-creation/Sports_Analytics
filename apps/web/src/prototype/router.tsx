import {
  createHashHistory,
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from "@tanstack/react-router";
import { HelpScreen } from "./screens/Help";
import { HomeScreen } from "./screens/Home";
import { MatchScreen } from "./screens/Match";
import { MatchesScreen } from "./screens/Matches";
import { MomentsScreen } from "./screens/Moments";
import { PeopleScreen } from "./screens/People";
import { ProgressScreen } from "./screens/Progress";
import { SettingsScreen } from "./screens/Settings";
import { WelcomeScreen } from "./screens/Welcome";
import { AppShell, NotFound } from "./ui/shell";

/* ─────────────────────────────────────────────────────────────────────────────
   Eight routes. The depth lives in tabs and query state, not in more pages:
   the match workspace alone carries nine analysis views, all addressable.

   `?f=` is the frame deep link — the same contract the production app uses — so a
   moment anywhere in the product can link straight into the player at its rally.
   ───────────────────────────────────────────────────────────────────────────── */

function str(v: unknown): string | undefined {
  return typeof v === "string" && v.length > 0 && v.length < 64 ? v : undefined;
}
function int(v: unknown): number | undefined {
  const n = Number(v);
  return Number.isFinite(n) && n >= 0 ? Math.floor(n) : undefined;
}
function oneOf<T extends string>(v: unknown, allowed: readonly T[], fallback: T): T {
  return allowed.includes(v as T) ? (v as T) : fallback;
}

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
  notFoundComponent: NotFound,
});

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: HomeScreen,
});

const welcomeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/welcome",
  component: WelcomeScreen,
});

const matchesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/matches",
  component: MatchesScreen,
});

const MATCH_TABS = [
  "overview",
  "moments",
  "rallies",
  "shots",
  "tactics",
  "court",
  "movement",
  "h2h",
  "pair",
  "ask",
] as const;

const HEAT_KINDS = ["presence", "movement", "origin", "landing", "targeting"] as const;

const matchRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/matches/$matchId",
  component: MatchScreen,
  validateSearch: (s: Record<string, unknown>) => ({
    tab: oneOf(s.tab, MATCH_TABS, "overview"),
    who: str(s.who),
    rally: int(s.rally),
    kind: s.kind ? oneOf(s.kind, HEAT_KINDS, "presence") : undefined,
    lens: str(s.lens),
    f: int(s.f),
  }),
});

const momentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/moments",
  component: MomentsScreen,
  validateSearch: (s: Record<string, unknown>) => ({ lens: str(s.lens), who: str(s.who) }),
});

const progressRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/progress",
  component: ProgressScreen,
  validateSearch: (s: Record<string, unknown>) => ({
    tab: oneOf(s.tab, ["overview", "records", "shots", "focus", "story"] as const, "overview"),
  }),
});

const peopleRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/people",
  component: PeopleScreen,
});

const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/settings",
  component: SettingsScreen,
  validateSearch: (s: Record<string, unknown>) => ({
    s: oneOf(s.s, ["privacy", "data", "display", "notifications"] as const, "privacy"),
  }),
});

const helpRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/help",
  component: HelpScreen,
  validateSearch: (s: Record<string, unknown>) => ({ topic: str(s.topic) }),
});

const routeTree = rootRoute.addChildren([
  homeRoute,
  welcomeRoute,
  matchesRoute,
  matchRoute,
  momentsRoute,
  progressRoute,
  peopleRoute,
  settingsRoute,
  helpRoute,
]);

export const router = createRouter({
  routeTree,
  history: createHashHistory(),
  defaultPreload: "intent",
  scrollRestoration: true,
});
