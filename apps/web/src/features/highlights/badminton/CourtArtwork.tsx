import type { HighlightCollection } from "../types";

/** Deliberate diagram, never a stand-in for observed video or position evidence. */
export function CourtArtwork({
  variant,
  format,
}: {
  variant: string;
  format: HighlightCollection["format"];
}) {
  const doubles = format === "doubles";
  const locations = doubles
    ? [
        { x: 196, y: 127, side: "other" },
        { x: 230, y: 223, side: "other" },
        { x: 422, y: 124, side: "you" },
        { x: variant === "coverage" ? 450 : 405, y: variant === "coverage" ? 139 : 228, side: "you" },
      ]
    : [
        { x: 211, y: 146, side: "other" },
        { x: 427, y: 211, side: "you" },
      ];
  return (
    <svg
      viewBox="0 0 640 360"
      preserveAspectRatio="xMidYMid slice"
      className={`hl-court-art hl-court-art-${variant}`}
      role="img"
      aria-label={`Illustrated ${format} court. Positions and shuttle path are synthetic, not measured.`}
    >
      <rect className="hl-court-ground" width="640" height="360" rx="0" />
      <g className="hl-court-lines" fill="none" strokeWidth="1.5">
        <rect x="98" y="68" width="444" height="202" />
        <path d="M98 84H542 M98 254H542 M132 68V270 M508 68V270 M254 68V270 M386 68V270 M98 169H254 M386 169H542" />
        <path d="M320 57V281" strokeWidth="2" />
      </g>
      {variant === "rally" && (
        <path
          className="hl-shuttle-path"
          d="M405 228L196 127L422 124L230 223L440 190L177 173L409 107"
          fill="none"
          strokeWidth="1.5"
          strokeDasharray="5 7"
        />
      )}
      {variant === "save" && (
        <g fill="none" className="hl-shuttle-path" strokeWidth="2">
          <path d="M196 127L466 230L240 110" strokeDasharray="5 7" />
          <path d="M410 228Q450 222 466 230" />
        </g>
      )}
      {variant === "pair" && (
        <path
          className="hl-shuttle-path"
          d="M422 124Q453 169 405 228"
          fill="none"
          strokeWidth="1.5"
          strokeDasharray="5 7"
        />
      )}
      {locations.map((point, index) => (
        <g key={index} className={point.side === "you" ? "hl-court-player" : "hl-court-opponent"}>
          <circle cx={point.x} cy={point.y} r="12" fill="currentColor" fillOpacity="0.13" />
          <circle cx={point.x} cy={point.y} r="5" fill="currentColor" />
        </g>
      ))}
      {variant === "save" && (
        <circle className="hl-court-player" cx="466" cy="230" r="4" fill="currentColor" />
      )}
      <g className="hl-court-net" strokeWidth="1">
        <path d="M315 68V270 M325 68V270" />
        <path d="M315 100H325 M315 134H325 M315 168H325 M315 202H325 M315 236H325" />
      </g>
    </svg>
  );
}
