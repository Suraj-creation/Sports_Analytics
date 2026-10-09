import { clsx } from "clsx";
import { LoaderCircle } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import type { Band, PlayerId } from "@/lib/types";

type Variant = "primary" | "secondary" | "ghost" | "danger";

export function Button({
  variant = "secondary",
  size = "md",
  busy = false,
  className,
  children,
  disabled,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: "sm" | "md"; busy?: boolean }) {
  return (
    <button
      type="button"
      {...rest}
      disabled={disabled || busy}
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors duration-150",
        "disabled:cursor-not-allowed disabled:opacity-50",
        size === "sm" ? "h-8 px-3 text-[13px]" : "h-10 px-4 text-sm",
        variant === "primary" && "bg-line text-mat-deep hover:bg-white",
        variant === "secondary" && "border border-seam bg-stand-raised text-line hover:border-line-3",
        variant === "ghost" && "text-line-2 hover:bg-stand-raised hover:text-line",
        variant === "danger" && "border border-alert/40 text-alert hover:bg-alert/10",
        className,
      )}
    >
      {busy && <LoaderCircle className="size-4 animate-spin" aria-hidden />}
      {children}
    </button>
  );
}

export function IconButton({
  label,
  active,
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { label: string; active?: boolean }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={active}
      {...rest}
      className={clsx(
        "inline-flex size-9 items-center justify-center rounded-lg transition-colors duration-150",
        active ? "bg-line/12 text-line" : "text-line-2 hover:bg-stand-raised hover:text-line",
        "disabled:opacity-40",
        className,
      )}
    >
      {children}
    </button>
  );
}

export function Spinner({ className }: { className?: string }) {
  return <LoaderCircle className={clsx("size-4 animate-spin text-line-2", className)} aria-label="Loading" />;
}

/** Certainty chip: confirmed = solid, probable = outlined + word, uncertain = dashed + muted. */
export function BandChip({
  band,
  color,
  children,
  className,
}: {
  band: Band;
  color?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 whitespace-nowrap rounded-full px-2 py-0.5 text-xs font-medium",
        `band-${band}`,
        className,
      )}
      style={{ color: color ?? "var(--color-line)" }}
    >
      <span className="text-line">{children}</span>
      {band === "probable" && <span className="text-line-2">probable</span>}
      {(band === "uncertain" || band === "unknown") && <span className="text-line-3">uncertain</span>}
    </span>
  );
}

export function PlayerDot({ pid, className }: { pid: PlayerId | null | undefined; className?: string }) {
  return (
    <span
      aria-hidden
      className={clsx("inline-block size-2 shrink-0 rounded-full", className)}
      style={{
        background:
          pid === "P1" ? "var(--color-p1)" : pid === "P2" ? "var(--color-p2)" : "var(--color-line-3)",
      }}
    />
  );
}

export function Empty({ title, children, icon }: { title: string; children?: ReactNode; icon?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-6 py-10 text-center">
      {icon && <div className="text-line-3">{icon}</div>}
      <p className="font-medium text-line">{title}</p>
      {children && <div className="max-w-sm text-sm text-line-2">{children}</div>}
    </div>
  );
}

export function ErrorNote({ error }: { error: unknown }) {
  if (!error) return null;
  const msg = error instanceof Error ? error.message : String(error);
  return (
    <p role="alert" className="rounded-lg border border-alert/40 bg-alert/10 px-3 py-2 text-sm text-line">
      {msg}
    </p>
  );
}

export function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded border border-seam bg-mat-deep px-1 text-[11px] text-line-2">
      {children}
    </kbd>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    // biome-ignore lint/a11y/noLabelWithoutControl: the control is passed as children
    <label className="flex flex-col gap-1.5 text-sm">
      <span className="font-medium text-line">{label}</span>
      {children}
      {hint && <span className="text-xs text-line-3">{hint}</span>}
    </label>
  );
}

export const inputClass =
  "h-10 rounded-lg border border-seam bg-mat-deep px-3 text-sm text-line placeholder:text-line-3 " +
  "focus:border-line-3 focus:outline-none";

export function Meter({
  value,
  className,
  tone = "signal",
}: {
  value: number;
  className?: string;
  tone?: "signal" | "line";
}) {
  const v = Math.max(0, Math.min(1, value));
  return (
    <div
      className={clsx("h-1.5 overflow-hidden rounded-full bg-seam", className)}
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(v * 100)}
    >
      <div
        className="h-full rounded-full transition-[width] duration-500"
        style={{
          width: `${v * 100}%`,
          background: tone === "signal" ? "var(--color-signal)" : "var(--color-line-2)",
        }}
      />
    </div>
  );
}
