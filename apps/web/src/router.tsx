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

const libraryRoute = createRoute({ getParentRoute: () => rootRoute, path: "/", component: LibraryPage });

export interface SessionSearch {
  /** deep-link frame (citations, highlights, exports link back here) */
  f?: number;
}

const sessionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/sessions/$sessionId",
  component: SessionPage,
  validateSearch: (s: Record<string, unknown>): SessionSearch => {
    const f = Number(s.f);
    return Number.isFinite(f) && f >= 0 ? { f: Math.floor(f) } : {};
  },
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

const routeTree = rootRoute.addChildren([libraryRoute, sessionRoute, calibrateRoute, systemRoute]);

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
