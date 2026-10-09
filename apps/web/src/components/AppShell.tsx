import { useQuery } from "@tanstack/react-query";
import { Link, Outlet } from "@tanstack/react-router";
import { Activity, LibraryBig, LogOut } from "lucide-react";
import { LoginPage } from "@/features/auth/LoginPage";
import { api, setCsrf } from "@/lib/api";
import { Spinner } from "./ui";

export function Logo() {
  // a shuttle seen from above: cork + skirt — the product mark
  return (
    <svg viewBox="0 0 32 32" className="size-7" aria-hidden>
      <rect width="32" height="32" rx="8" fill="#18221f" />
      <path d="M9 10 L16 23 L23 10 Z" fill="none" stroke="#e8efea" strokeWidth="1.6" strokeLinejoin="round" />
      <path d="M12.5 10 L16 23 M19.5 10 L16 23" stroke="#a9bab2" strokeWidth="1" />
      <circle cx="16" cy="23.5" r="2.6" fill="#ffffff" />
      <path d="M9 10 Q16 7 23 10" fill="none" stroke="#3ddc97" strokeWidth="1.6" />
    </svg>
  );
}

function NavLink({ to, children }: { to: "/" | "/system"; children: React.ReactNode }) {
  return (
    <Link
      to={to}
      className="inline-flex h-8 items-center gap-2 rounded-lg px-3 text-sm text-line-2 transition-colors hover:bg-stand-raised hover:text-line"
      activeProps={{ className: "bg-stand-raised text-line" }}
      activeOptions={{ exact: to === "/" }}
    >
      {children}
    </Link>
  );
}

export function AppShell() {
  const me = useQuery({ queryKey: ["me"], queryFn: api.me, staleTime: 60_000 });
  if (me.data) setCsrf(me.data.csrf);

  if (me.isPending) {
    return (
      <div className="grid h-full place-items-center">
        <Spinner className="size-6" />
      </div>
    );
  }
  if (me.isError) {
    return (
      <div className="grid h-full place-items-center px-4 text-center">
        <div className="space-y-2">
          <p className="font-medium">Can't reach the Badminton AI server</p>
          <p className="text-sm text-line-2">Start it with `bai serve`, then reload this page.</p>
        </div>
      </div>
    );
  }
  if (me.data.auth_required && !me.data.authenticated) return <LoginPage onDone={() => me.refetch()} />;

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-13 shrink-0 items-center gap-3 border-b border-seam bg-mat-deep/60 px-4 backdrop-blur">
        <Link
          to="/"
          className="flex items-center gap-2.5 rounded-lg pr-2"
          aria-label="Badminton AI — library"
        >
          <Logo />
          <span className="text-[15px] font-semibold tracking-tight">Badminton AI</span>
        </Link>
        <nav className="ml-4 flex items-center gap-1">
          <NavLink to="/">
            <LibraryBig className="size-4" aria-hidden /> Library
          </NavLink>
          <NavLink to="/system">
            <Activity className="size-4" aria-hidden /> System
          </NavLink>
        </nav>
        <div className="ml-auto" />
        {me.data.auth_required && (
          <button
            type="button"
            className="inline-flex h-8 items-center gap-2 rounded-lg px-3 text-sm text-line-2 hover:bg-stand-raised hover:text-line"
            onClick={async () => {
              await api.logout();
              me.refetch();
            }}
          >
            <LogOut className="size-4" aria-hidden /> Sign out
          </button>
        )}
      </header>
      <main className="min-h-0 flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}

export function NotFound() {
  return (
    <div className="grid h-full place-items-center px-4 text-center">
      <div className="space-y-3">
        <p className="font-medium">This page doesn't exist</p>
        <Link to="/" className="text-sm text-signal underline-offset-4 hover:underline">
          Back to the library
        </Link>
      </div>
    </div>
  );
}
