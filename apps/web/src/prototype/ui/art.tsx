import { clsx } from "clsx";

/* ─────────────────────────────────────────────────────────────────────────────
   Drawn assets.

   The prototype has no real footage. 08 §15 says posters must be real match frames
   and never stock athletes — so rather than fake a photograph, every poster here is
   an openly diagrammatic stand-in, drawn from the court geometry, and labelled as one.
   Nothing on screen pretends to be a photo of a person.
   ───────────────────────────────────────────────────────────────────────────── */

function hash(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i += 1) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 4294967296;
}

/**
 * A stand-in frame: the court as the venue camera sees it, with the two players
 * placed by a hash of the moment id so each clip looks like its own moment.
 */
export function Poster({
  seed,
  className,
  label,
  sample,
}: {
  seed: string;
  className?: string;
  label?: string;
  sample?: boolean;
}) {
  const a = hash(seed);
  const b = hash(`${seed}-b`);
  const c = hash(`${seed}-c`);
  // Near player sits low and wide; far player sits high and narrow (perspective).
  const youX = 110 + a * 100;
  const youY = 132 + b * 20;
  const oppX = 125 + c * 70;
  const oppY = 72 + a * 14;
  const shuttleX = (youX + oppX) / 2 + (b - 0.5) * 40;
  const shuttleY = (youY + oppY) / 2 - 14 - c * 16;

  return (
    <div className={clsx("relative overflow-hidden rounded-[14px] bg-well", className)}>
      <svg
        viewBox="0 0 320 180"
        className="h-full w-full"
        preserveAspectRatio="xMidYMid slice"
        role="img"
        aria-label={label ?? "A stand-in frame showing the court from the venue camera"}
      >
        <defs>
          <linearGradient id={`floor-${seed}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#14382f" />
            <stop offset="100%" stopColor="#0c2620" />
          </linearGradient>
        </defs>
        <rect width="320" height="180" fill="#0c2620" />
        {/* court, in camera perspective: far edge narrow, near edge wide */}
        <path d="M118 56 L202 56 L268 162 L52 162 Z" fill={`url(#floor-${seed})`} />
        <g stroke="rgb(232 239 234 / 0.42)" strokeWidth="1" fill="none">
          <path d="M118 56 L202 56 L268 162 L52 162 Z" />
          {/* net */}
          <path d="M104 96 L216 96" strokeWidth="1.6" stroke="rgb(232 239 234 / 0.6)" />
          <path d="M104 96 L104 78 M216 96 L216 78" strokeWidth="1.2" />
          {/* service lines */}
          <path d="M128 74 L192 74" />
          <path d="M92 130 L228 130" />
          {/* centre line */}
          <path d="M160 56 L160 74 M160 130 L160 162" />
        </g>
        {/* far player — square, --other */}
        <rect x={oppX - 4} y={oppY - 4} width="8" height="8" fill="#7c8794" rx="1" />
        <ellipse cx={oppX} cy={oppY + 7} rx="7" ry="2" fill="rgb(0 0 0 / 0.35)" />
        {/* near player — circle, --you */}
        <ellipse cx={youX} cy={youY + 10} rx="10" ry="3" fill="rgb(0 0 0 / 0.4)" />
        <circle cx={youX} cy={youY} r="6" fill="#4fd6c4" />
        {/* shuttle — the only pure white */}
        <circle cx={shuttleX} cy={shuttleY} r="2.2" fill="#ffffff" />
        <path
          d={`M${youX} ${youY - 6} Q ${shuttleX} ${shuttleY - 18} ${oppX} ${oppY + 4}`}
          stroke="rgb(255 255 255 / 0.22)"
          strokeWidth="1"
          strokeDasharray="3 3"
          fill="none"
        />
      </svg>
      <span className="absolute bottom-1.5 left-2 rounded bg-well/80 px-1.5 py-0.5 text-[11px] text-[#8da098]">
        Stand-in frame
      </span>
      {sample && (
        <span className="absolute right-0 top-0 rounded-bl-[10px] bg-opportunity/90 px-2 py-1 text-[11px] font-medium text-[#14211d]">
          Sample
        </span>
      )}
    </div>
  );
}

/** The shuttle mark. Teal arc in daylight, signal arc in the theatre. */
export function Logo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 28 28" className={className} aria-hidden fill="none">
      <rect width="28" height="28" rx="8" className="fill-ink" />
      <path
        d="M14 6.5 8.5 19.5 14 22.5 19.5 19.5 Z"
        className="stroke-canvas"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <circle cx="14" cy="8.5" r="2.6" className="fill-canvas" />
      <path d="M11.2 15.2h5.6M12.1 12.4h3.8" className="stroke-canvas" strokeWidth="1.1" />
    </svg>
  );
}

/* ─────────────────────── state illustrations ───────────────────────
   One inline SVG each, built from court lines and a shuttle, following currentColor
   so they theme automatically (08 §15.1). No characters, no humour at the player's expense. */

type Motif =
  | "empty"
  | "partial"
  | "low-coverage"
  | "failed"
  | "not-enough"
  | "offline"
  | "permission"
  | "processing";

export function StateArt({ motif, className }: { motif: Motif; className?: string }) {
  const common = {
    viewBox: "0 0 96 72",
    className: clsx("text-faint", className),
    fill: "none" as const,
    "aria-hidden": true,
  };
  const court = "M24 10 H72 V62 H24 Z";
  const net = "M20 36 H76";

  switch (motif) {
    case "empty":
      return (
        <svg {...common} aria-hidden="true">
          <path d={court} stroke="currentColor" strokeWidth="1.5" />
          <path d={net} stroke="currentColor" strokeWidth="1.5" />
          <circle cx="48" cy="24" r="3" fill="currentColor" />
          <path d="M48 27 L45 33 M48 27 L51 33" stroke="currentColor" strokeWidth="1.2" />
        </svg>
      );
    case "partial":
      return (
        <svg {...common} aria-hidden="true">
          <path d="M24 10 H72 V36 H24 Z" stroke="currentColor" strokeWidth="1.5" />
          <path
            d="M24 36 H72 V62 H24 Z"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeDasharray="3 3"
            fill="url(#hatchPattern)"
          />
          <defs>
            <pattern id="hatchPattern" width="5" height="5" patternTransform="rotate(45)">
              <line x1="0" y1="0" x2="0" y2="5" stroke="currentColor" strokeWidth="1" opacity="0.35" />
            </pattern>
          </defs>
          <path d={net} stroke="currentColor" strokeWidth="1.5" />
        </svg>
      );
    case "low-coverage":
      return (
        <svg {...common} aria-hidden="true">
          <path d={court} stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
          <path d={net} stroke="currentColor" strokeWidth="1.5" />
          <rect x="38" y="20" width="20" height="14" rx="3" stroke="currentColor" strokeWidth="1.5" />
          <circle cx="48" cy="27" r="3.5" stroke="currentColor" strokeWidth="1.5" />
          <path d="M43 20 l3 -4 h4 l3 4" stroke="currentColor" strokeWidth="1.5" />
        </svg>
      );
    case "failed":
      return (
        <svg {...common} aria-hidden="true">
          <path d={court} stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
          <path d={net} stroke="currentColor" strokeWidth="1.5" opacity="0.4" />
          <path d="M28 54 Q 44 20 56 34" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
          <circle cx="56" cy="34" r="3" className="fill-error" />
        </svg>
      );
    case "not-enough":
      return (
        <svg {...common} aria-hidden="true">
          <circle cx="48" cy="36" r="20" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
          <text x="48" y="43" textAnchor="middle" fontSize="20" fill="currentColor" fontFamily="inherit">
            ?
          </text>
        </svg>
      );
    case "offline":
      return (
        <svg {...common} aria-hidden="true">
          <path d="M24 10 H46" stroke="currentColor" strokeWidth="1.5" />
          <path d="M56 10 H72 V62 H24 V40" stroke="currentColor" strokeWidth="1.5" />
          <path d={net} stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 4" />
        </svg>
      );
    case "permission":
      return (
        <svg {...common} aria-hidden="true">
          <rect x="34" y="34" width="28" height="22" rx="4" stroke="currentColor" strokeWidth="1.5" />
          <path d="M40 34 v-7 a8 8 0 0 1 16 0 v7" stroke="currentColor" strokeWidth="1.5" />
          <circle cx="48" cy="45" r="2.5" fill="currentColor" />
        </svg>
      );
    case "processing":
      return (
        <svg {...common} aria-hidden="true">
          <path d={court} stroke="currentColor" strokeWidth="1.5" />
          <path d={net} stroke="currentColor" strokeWidth="1.5" />
          <circle cx="36" cy="22" r="2.5" fill="currentColor" />
          <circle cx="48" cy="22" r="2.5" fill="currentColor" opacity="0.6" />
          <circle cx="60" cy="22" r="2.5" fill="currentColor" opacity="0.3" />
        </svg>
      );
  }
}

/** The court-line corner that sits behind the landing hero at 8% (§5). */
export function CourtLinesBackdrop({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 300"
      preserveAspectRatio="xMidYMid meet"
      className={clsx("pointer-events-none text-ink opacity-[0.07]", className)}
      aria-hidden
      fill="none"
    >
      <g stroke="currentColor" strokeWidth="1.5">
        <path d="M40 20 H360 V280 H40 Z" />
        <path d="M0 150 H400" strokeWidth="2.5" />
        <path d="M80 20 V280 M320 20 V280" />
        <path d="M40 70 H360 M40 230 H360" />
        <path d="M200 20 V70 M200 230 V280" />
      </g>
    </svg>
  );
}
