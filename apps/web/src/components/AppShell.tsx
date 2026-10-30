import { useQuery } from "@tanstack/react-query";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import {
  Activity,
  ChevronRight,
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

export function Logo({ compact = false, className = "" }: { compact?: boolean; className?: string }) {
  const light = compact ? "rally-symbol-forest.svg" : "rally-lockup-on-light.svg";
  const dark = compact ? "rally-symbol-lime.svg" : "rally-lockup-on-dark.svg";
  return (
    <span className={`rally-logo ${compact ? "rally-logo-compact" : ""} ${className}`}>
      <img
        src={`/brand/${light}`}
        className="rally-logo-light"
        alt="Rally"
        width={compact ? 30 : 114}
        height={compact ? 30 : 44}
      />
      <img
        src={`/brand/${dark}`}
        className="rally-logo-dark"
        alt="Rally"
        width={compact ? 30 : 114}
        height={compact ? 30 : 44}
      />
    </span>
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
      aria-label={label}
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
  const [systemDark, setSystemDark] = useState(
    () => window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false,
  );
  const [logoutError, setLogoutError] = useState("");
  const path = useRouterState({ select: (s) => s.location.pathname });
  const main = useRef<HTMLElement>(null);
  const darkTheme = theme === "dark" || (theme === "system" && systemDark);
  const pageLabel = path.includes("/calibrate")
    ? "Court calibration"
    : path.startsWith("/matches/") || path.startsWith("/sessions/")
      ? "Match review"
      : path === "/library"
        ? "Add a recording"
        : path === "/system"
          ? "System"
          : path === "/settings"
            ? "Settings"
            : path === "/help"
              ? "Help"
              : (NAV.find((item) => item.to === path)?.label ?? "Workspace");
  useEffect(() => {
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    const onSystemChange = () => setSystemDark(media?.matches ?? false);
    media?.addEventListener("change", onSystemChange);
    const observer = new MutationObserver(() => {
      const value = document.documentElement.dataset.theme;
      setTheme(value === "dark" || value === "light" ? value : "system");
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => {
      media?.removeEventListener("change", onSystemChange);
      observer.disconnect();
    };
  }, []);

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
      <div className="rally-offline">
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
        <Link to="/" className="rally-brand" aria-label="Rally home">
          <Logo className="rally-logo-lockup" />
          <Logo compact className="rally-logo-symbol" />
        </Link>
        <p className="rally-sidebar-context">Badminton analytics</p>
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
                theme: darkTheme ? ("light" as const) : ("dark" as const),
              };
              applyDisplay(next);
              setTheme(next.theme);
              try {
                localStorage.setItem("rally-display-v1", JSON.stringify(next));
              } catch {
                /* blocked storage */
              }
            }}
            aria-label={`Switch to ${darkTheme ? "light" : "dark"} theme`}
          >
            {!darkTheme ? <Moon className="size-5" /> : <Sun className="size-5" />}
            <span>{darkTheme ? "Light appearance" : "Dark appearance"}</span>
          </button>
          <NavItem to="/settings" label="Settings" icon={Settings} />
        </div>
      </aside>
      <div className="rally-app-main">
        <header className="rally-header">
          <Link to="/" className="rally-mobile-brand" aria-label="Rally home">
            <Logo />
          </Link>
          <div className="rally-breadcrumb">
            <span>Analytics</span>
            <ChevronRight size={14} aria-hidden />
            <strong>{pageLabel}</strong>
          </div>
          <div className="rally-header-actions">
            <Link to="/library" className="rally-header-link rally-header-add">
              <Upload className="size-4" aria-hidden />
              <span>Add recording</span>
            </Link>
            <Link to="/help" className="rally-header-link rally-header-help" aria-label="Help">
              <HelpCircle className="size-4" aria-hidden />
              <span>Help</span>
            </Link>
            <Link to="/settings" className="rally-header-link rally-mobile-settings" aria-label="Settings">
              <Settings className="size-4" aria-hidden />
              <span>Settings</span>
            </Link>
            {me.data.auth_required && (
              <button
                type="button"
                className="rally-header-link"
                aria-label="Sign out"
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
        <main id="content" ref={main} className="rally-main-sheet">
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
