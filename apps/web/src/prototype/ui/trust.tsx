import * as Popover from "@radix-ui/react-popover";
import { clsx } from "clsx";

/**
 * Preview tag.
 *
 * Marks a surface whose underlying capability is young — shot naming, placement,
 * distance. It explains the limit of the measurement so the number can still be used,
 * which is the point: a reader who knows where a figure gets soft can lean on the rest.
 * It is a statement about the method, never about whether a particular number is right.
 */
export function PreviewTag({ what, why, className }: { what?: string; why?: string; className?: string }) {
  return (
    <Popover.Root>
      <Popover.Trigger asChild>
        <button
          type="button"
          className={clsx(
            "inline-flex min-h-6 shrink-0 items-center gap-1 rounded-full border border-uncertain/60 px-2 py-0.5",
            "text-xs font-medium text-uncertain transition-opacity hover:opacity-80",
            className,
          )}
        >
          <svg viewBox="0 0 16 16" className="size-3" aria-hidden fill="none">
            <path d="M8 2.2 13.8 8 8 13.8 2.2 8Z" stroke="currentColor" strokeWidth="1.5" />
          </svg>
          Preview
        </button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          sideOffset={6}
          collisionPadding={12}
          className="z-50 max-w-[320px] rounded-[14px] border border-edge bg-surface p-4 text-sm text-muted shadow-[var(--shadow-pop)]"
        >
          <p className="mb-1.5 font-[600] text-ink">Preview{what ? `: ${what}` : ""}</p>
          <p>
            {why ??
              "This works, with limits. It has not been validated on this venue's camera yet, so read it as a measurement with a margin rather than a precise figure."}
          </p>
          <Popover.Arrow className="fill-[var(--c-edge)]" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
}
