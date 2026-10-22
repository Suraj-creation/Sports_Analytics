import type { QueryClient } from "@tanstack/react-query";
import {
  createRootRouteWithContext,
  createRoute,
  createRouter,
  lazyRouteComponent,
} from "@tanstack/react-router";
import { AppShell, NotFound } from "@/components/AppShell";
import { LibraryPage } from "@/features/library/LibraryPage";
import { SessionPage } from "@/features/session/SessionPage";

export interface RouterContext {
  queryClient: QueryClient;
}
const rootRoute = createRootRouteWithContext<RouterContext>()({
  component: AppShell,
  notFoundComponent: NotFound,
});
const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: lazyRouteComponent(() => import("@/features/product/Home"), "HomePage"),
});
const libraryRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/library",
  component: LibraryPage,
});
const matchesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/matches",
  component: lazyRouteComponent(() => import("@/features/product/Matches"), "MatchesPage"),
});
export interface SessionSearch {
  f?: number;
  tab?: string;
  who?: string;
  kind?: string;
  rally?: number;
}
const tabs = [
  "overview",
  "moments",
  "highlights",
  "rallies",
  "shots",
  "stats",
  "tactics",
  "court",
  "heatmaps",
  "movement",
  "h2h",
  "pair",
  "ask",
  "events",
];
function sessionSearch(search: Record<string, unknown>): SessionSearch {
  const result: SessionSearch = {};
  if (search.f != null && Number.isFinite(Number(search.f)) && Number(search.f) >= 0)
    result.f = Math.floor(Number(search.f));
  if (typeof search.tab === "string" && tabs.includes(search.tab)) result.tab = search.tab;
  if (search.who === "P1" || search.who === "P2") result.who = search.who;
  if (
    typeof search.kind === "string" &&
    ["presence", "movement", "origin", "landing", "targeting"].includes(search.kind)
  )
    result.kind = search.kind;
  if (search.rally != null && Number.isFinite(Number(search.rally)) && Number(search.rally) >= 0)
    result.rally = Math.floor(Number(search.rally));
  return result;
}
const sessionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/sessions/$sessionId",
  component: SessionPage,
  validateSearch: sessionSearch,
});
const matchRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/matches/$matchId",
  component: SessionPage,
  validateSearch: sessionSearch,
});
const momentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/moments",
  component: lazyRouteComponent(() => import("@/features/product/Moments"), "MomentsPage"),
});
const progressRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/progress",
  component: lazyRouteComponent(() => import("@/features/product/Progress"), "ProgressPage"),
  validateSearch: (search: Record<string, unknown>): { tab?: string } => ({
    tab:
      typeof search.tab === "string" &&
      ["overview", "records", "shots", "focus", "story"].includes(search.tab)
        ? search.tab
        : "overview",
  }),
});
const peopleRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/people",
  component: lazyRouteComponent(() => import("@/features/product/People"), "PeoplePage"),
});
const settingsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/settings",
  component: lazyRouteComponent(() => import("@/features/product/Settings"), "SettingsPage"),
});
const helpRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/help",
  component: lazyRouteComponent(() => import("@/features/product/Help"), "HelpPage"),
});
const calibrateRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/sessions/$sessionId/calibrate",
  component: lazyRouteComponent(() => import("@/features/calibrate/CalibratePage"), "CalibratePage"),
});
const systemRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/system",
  component: lazyRouteComponent(() => import("@/features/system/SystemPage"), "SystemPage"),
});
const routeTree = rootRoute.addChildren([
  homeRoute,
  libraryRoute,
  matchesRoute,
  sessionRoute,
  matchRoute,
  momentsRoute,
  progressRoute,
  peopleRoute,
  settingsRoute,
  helpRoute,
  calibrateRoute,
  systemRoute,
]);
export const router = createRouter({
  routeTree,
  context: { queryClient: undefined as unknown as QueryClient },
  defaultPreload: "intent",
  scrollRestoration: true,
});
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
