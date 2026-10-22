import { clsx } from "clsx";
import { LoaderCircle, X } from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { useEffect, useId, useRef } from "react";

/* ───────────────────────────── Button ─────────────────────────────
   Primary is the court teal fill; there is exactly one per view (P3).
   `danger` exists only for destructive actions — red never describes play. */

type Variant = "primary" | "secondary" | "ghost" | "danger";

export function Button({
  variant = "secondary",
  size = "md",
  busy = false,
  className,
  children,
  disabled,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: "sm" | "md" | "lg";
  busy?: boolean;
}) {
  return (
    <button
      type="button"
      {...rest}
      disabled={disabled || busy}
      className={clsx(
        "inline-flex shrink-0 items-center justify-center gap-2 rounded-[10px] font-medium",
        "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-45",
        size === "sm" && "h-9 px-3 text-sm",
        size === "md" && "h-11 px-4 text-sm",
        size === "lg" && "h-12 px-6 text-base",
        variant === "primary" && "bg-primary text-on-primary hover:bg-primary-hover",
        variant === "secondary" &&
          "border border-edge bg-surface text-ink hover:border-edge-strong hover:bg-surface-raised",
        variant === "ghost" && "text-muted hover:bg-surface-raised hover:text-ink",
        variant === "danger" && "border border-error/45 text-error hover:bg-error/10",
        className,
      )}
    >
      {busy && <LoaderCircle className="size-4 animate-spin" aria-hidden />}
      {children}
    </button>
  );
}

/** Icon-only is allowed for close, play/pause and frame step. Everything else gets a word. */
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
        "inline-flex size-11 items-center justify-center rounded-[10px] transition-colors duration-150",
        active ? "bg-ink/10 text-ink" : "text-muted hover:bg-surface-raised hover:text-ink",
        "disabled:opacity-40",
        className,
      )}
    >
      {children}
    </button>
  );
}

/* ───────────────────────────── Card ─────────────────────────────
   Flat: a 1px edge on surface. No shadow — only floating things cast one (§8). */

export function Card({
  as: As = "div",
  className,
  children,
}: {
  as?: "div" | "section" | "article" | "li";
  className?: string;
  children: ReactNode;
}) {
  return (
    <As className={clsx("rounded-[14px] border border-edge bg-surface", "p-[var(--d-pad)]", className)}>
      {children}
    </As>
  );
}

export function SectionHeading({
  children,
  step,
  action,
}: {
  children: ReactNode;
  step?: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <h2 className="flex items-baseline gap-2 text-xl font-[650] text-ink">
        {step && <span className="numerals text-base text-faint">{step}</span>}
        {children}
      </h2>
      {action}
    </div>
  );
}

/* ───────────────────────────── Chip ───────────────────────────── */

export function Chip({
  selected,
  className,
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { selected?: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      {...rest}
      className={clsx(
        "inline-flex h-9 shrink-0 items-center gap-1.5 rounded-full border px-3.5 text-sm",
        "transition-colors duration-150 disabled:opacity-45",
        selected
          ? "border-ink bg-ink text-canvas"
          : "border-edge bg-surface text-muted hover:border-edge-strong hover:text-ink",
        className,
      )}
    >
      {children}
    </button>
  );
}

/* ───────────────────────────── SegmentedControl ───────────────────────────── */

export function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: string; hint?: string }[];
  onChange: (v: T) => void;
  label: string;
}) {
  const name = useId();
  return (
    <fieldset className="inline-flex rounded-[10px] border border-edge bg-surface p-0.5">
      <legend className="sr-only">{label}</legend>
      {options.map((o) => (
        <label
          key={o.value}
          title={o.hint}
          className={clsx(
            "flex h-10 cursor-pointer items-center rounded-[8px] px-3 text-sm font-medium",
            "transition-colors duration-150 focus-within:outline focus-within:outline-2",
            "focus-within:outline-offset-2 focus-within:outline-[var(--c-primary)]",
            value === o.value ? "bg-ink text-canvas" : "text-muted hover:text-ink",
          )}
        >
          <input
            type="radio"
            name={name}
            value={o.value}
            checked={value === o.value}
            onChange={() => onChange(o.value)}
            className="sr-only"
          />
          {o.label}
        </label>
      ))}
    </fieldset>
  );
}

/* ───────────────────────────── Toggle ───────────────────────────── */

export function Toggle({
  checked,
  onChange,
  label,
  describedBy,
  disabled,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  describedBy?: string;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      aria-describedby={describedBy}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={clsx(
        "relative inline-flex h-7 w-12 shrink-0 items-center rounded-full border transition-colors duration-150",
        "disabled:cursor-not-allowed disabled:opacity-45",
        checked ? "border-primary bg-primary" : "border-edge-strong bg-surface-raised",
      )}
    >
      <span
        aria-hidden
        className={clsx(
          "absolute size-5 rounded-full transition-[left] duration-150",
          checked ? "left-6 bg-on-primary" : "left-0.5 bg-edge-strong",
        )}
      />
    </button>
  );
}

/* ───────────────────────────── Sheet / Dialog ─────────────────────────────
   Bottom sheet on phones, centred panel from md. Esc closes; focus returns to
   whatever opened it; the backdrop is a button so pointer and keyboard agree. */

export function Sheet({
  open,
  onClose,
  title,
  description,
  children,
  footer,
  wide,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  footer?: ReactNode;
  wide?: boolean;
}) {
  const titleId = useId();
  const descId = useId();
  const panel = useRef<HTMLDivElement>(null);
  const opener = useRef<Element | null>(null);

  useEffect(() => {
    if (!open) return;
    opener.current = document.activeElement;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
      }
    };
    document.addEventListener("keydown", onKey);
    const first = panel.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    first?.focus();
    return () => {
      document.removeEventListener("keydown", onKey);
      (opener.current as HTMLElement | null)?.focus?.();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center md:items-center">
      <button
        type="button"
        aria-label="Close"
        onClick={onClose}
        className="absolute inset-0 bg-ink/40 backdrop-blur-[2px]"
      />
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descId : undefined}
        className={clsx(
          "sheet-up relative max-h-[88vh] w-full overflow-y-auto quiet-scroll",
          "rounded-t-[20px] border border-edge bg-surface shadow-[var(--shadow-pop)]",
          "md:rounded-[14px] md:animate-none",
          wide ? "md:max-w-[720px]" : "md:max-w-[520px]",
          "pb-[max(16px,env(safe-area-inset-bottom))]",
        )}
      >
        <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-edge bg-surface px-5 py-4">
          <div>
            <h2 id={titleId} className="text-lg font-[650] text-ink">
              {title}
            </h2>
            {description && (
              <p id={descId} className="mt-1 text-sm text-muted">
                {description}
              </p>
            )}
          </div>
          <IconButton label="Close" onClick={onClose} className="-mr-2 -mt-1">
            <X className="size-5" aria-hidden />
          </IconButton>
        </div>
        <div className="px-5 py-4">{children}</div>
        {footer && <div className="sticky bottom-0 border-t border-edge bg-surface px-5 py-3">{footer}</div>}
      </div>
    </div>
  );
}

/* ───────────────────────────── Skeleton ─────────────────────────────
   Static. A shimmer is looping decoration, which §13 forbids. */

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={clsx("rounded-[10px] bg-surface-raised", className)} />;
}

export function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded border border-edge bg-surface-raised px-1 text-xs text-muted">
      {children}
    </kbd>
  );
}

/** Announce route and state changes without stealing focus. */
export function LiveRegion({ message }: { message: string }) {
  return (
    <div aria-live="polite" aria-atomic="true" className="sr-only">
      {message}
    </div>
  );
}
