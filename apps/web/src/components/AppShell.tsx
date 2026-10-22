import { useQuery } from "@tanstack/react-query";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  Clapperboard,
  HelpCircle,
  House,
  LibraryBig,
  LogOut,
  Moon,
  Settings,
  Sun,
  TrendingUp,
  Upload,
  Users,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { LoginPage } from "@/features/auth/LoginPage";
import { applyDisplay, readDisplay } from "@/features/product/Settings";
import { api, setCsrf } from "@/lib/api";
import { Spinner } from "./ui";

const NAV = [
  { to: "/", label: "Home", icon: House },
  { to: "/matches", label: "Matches", icon: LibraryBig },
  { to: "/moments", label: "Moments", icon: Clapperboard },
  { to: "/progress", label: "Progress", icon: TrendingUp },
  { to: "/people", label: "People", icon: Users },
] as const;

export function Logo() {
  return (
    <svg viewBox="0 0 32 32" className="size-8" aria-hidden>
      <rect width="32" height="32" rx="9" fill="var(--c-primary)" />
      <path
        d="M9 9 16 23 23 9M12 9l4 14 4-14M9 9q7-3 14 0"
        fill="none"
        stroke="var(--c-on-primary)"
        strokeWidth="1.5"
      />
      <circle cx="16" cy="24" r="2" fill="var(--c-on-primary)" />
    </svg>
  );
}

function NavItem({ to, label, icon: Icon }: { to: string; label: string; icon: typeof House }) {
  const path = useRouterState({ select: (s) => s.location.pathname });
  const active =
    to === "/" ? path === "/" : path.startsWith(to) || (to === "/matches" && path.startsWith("/sessions/"));
  return (
    <Link
      to={to}
      aria-current={active ? "page" : undefined}
      title={label}
      className={`rally-nav-item ${active ? "is-active" : ""}`}
    >
      <Icon className="size-5 shrink-0" aria-hidden />
      <span>{label}</span>
    </Link>
  );
}

export function AppShell() {
  const me = useQuery({ queryKey: ["me"], queryFn: api.me, staleTime: 60_000 });
  const [theme, setTheme] = useState(() => readDisplay().theme);
  const [logoutError, setLogoutError] = useState("");
  const path = useRouterState({ select: (s) => s.location.pathname });
  const main = useRef<HTMLElement>(null);

  useEffect(() => {
    if (me.data) setCsrf(me.data.csrf);
  }, [me.data]);
  useEffect(() => {
    if (!path) return;
    setTheme(readDisplay().theme);
    const heading = main.current?.querySelector<HTMLElement>("h1");
    heading?.setAttribute("tabindex", "-1");
    heading?.focus({ preventScroll: true });
  }, [path]);

  if (me.isPending)
    return (
      <div className="grid h-full place-items-center">
        <Spinner className="size-6" />
      </div>
    );
  if (me.isError)
    return (
      <div className="grid h-full place-items-center p-6 text-center">
        <div>
          <h1 className="text-xl font-semibold">We couldn't reach the server</h1>
          <p className="mt-2 text-line-2">Check your connection, then try again.</p>
          <button type="button" className="rally-action mt-4" onClick={() => void me.refetch()}>
            Try again
          </button>
        </div>
      </div>
    );
  if (me.data.auth_required && !me.data.authenticated) return <LoginPage onDone={() => me.refetch()} />;

  return (
    <div className="rally-app">
      <a href="#content" className="rally-skip">
        Skip to content
      </a>
      <aside className="rally-sidebar">
        <Link to="/" className="rally-brand">
          <Logo />
          <span>Rally</span>
        </Link>
        <nav aria-label="Main">
          {NAV.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>
        <div className="rally-sidebar-bottom">
          <NavItem to="/library" label="Add a recording" icon={Upload} />
          <NavItem to="/system" label="System" icon={Activity} />
          <button
            type="button"
            className="rally-nav-item"
            onClick={() => {
              const next = {
                ...readDisplay(),
                theme: theme === "dark" ? ("light" as const) : ("dark" as const),
              };
              applyDisplay(next);
              setTheme(next.theme);
              try {
                localStorage.setItem("rally-display-v1", JSON.stringify(next));
              } catch {
                /* blocked storage */
              }
            }}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
          >
            {theme === "light" ? <Moon className="size-5" /> : <Sun className="size-5" />}
            <span>{theme === "light" ? "Arena night" : "Court daylight"}</span>
          </button>
          <NavItem to="/settings" label="Settings" icon={Settings} />
        </div>
      </aside>
      <div className="rally-app-main">
        <header className="rally-header">
          <Link to="/" className="rally-mobile-brand">
            <Logo />
            <span>Rally</span>
          </Link>
          <div className="ml-auto flex items-center gap-2">
            <Link to="/library" className="rally-header-link">
              <Upload className="size-4" aria-hidden />
              <span>Add recording</span>
            </Link>
            <Link to="/help" className="rally-header-link">
              <HelpCircle className="size-4" aria-hidden />
              <span>Help</span>
            </Link>
            {me.data.auth_required && (
              <button
                type="button"
                className="rally-header-link"
                onClick={async () => {
                  try {
                    await api.logout();
                    await me.refetch();
                  } catch {
                    setLogoutError("Sign out failed. Please try again.");
                  }
                }}
              >
                <LogOut className="size-4" aria-hidden />
                <span>Sign out</span>
              </button>
            )}
          </div>
        </header>
        {logoutError && (
          <p role="alert" className="px-6 py-3 text-alert">
            {logoutError}
          </p>
        )}
        <main id="content" ref={main} className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
      <nav className="rally-bottom-nav" aria-label="Main on mobile">
        {NAV.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>
    </div>
  );
}

export function NotFound() {
  return (
    <div className="mx-auto max-w-lg space-y-4 px-6 py-16">
      <h1 className="text-2xl font-bold">We couldn't find that page</h1>
      <p className="text-line-2">The link may be old, or the match may have been removed.</p>
      <Link to="/matches" className="rally-action">
        See your matches
      </Link>
    </div>
  );
}
