import type { HighlightCollection, HighlightEvidence, HighlightInsight } from "../types";
import { badmintonHighlights } from "./catalogue";

// Synthetic design material only. These contacts, sides and histories are not labels
// for real footage. All example figures come from these same small source arrays.
const contactCounts = [
  3, 7, 4, 6, 9, 2, 5, 11, 4, 8, 3, 6, 10, 4, 7, 2, 5, 28, 3, 8, 4, 6, 2, 9, 7, 4, 11, 5, 3, 8, 6, 4, 10, 7,
  2, 5, 12, 3, 6, 4,
];
const winningSides = [
  "B",
  "A",
  "B",
  "B",
  "A",
  "B",
  "A",
  "B",
  "B",
  "A",
  "B",
  "A",
  "B",
  "B",
  "A",
  "B",
  "A",
  "B",
  "A",
  "B",
  "B",
  "A",
  "B",
  "A",
  "A",
  "A",
  "A",
  "A",
  "B",
  "A",
  "B",
  "A",
  "A",
  "A",
  "B",
  "B",
  "A",
  "B",
  "A",
  "A",
];
const smashOutcomes = [
  "direct",
  "continued",
  "forced",
  "uncertain",
  "direct",
  "continued",
  "own",
  "continued",
  "forced",
  "direct",
  "continued",
  "uncertain",
];

export function exampleCollection(format: "singles" | "doubles"): HighlightCollection {
  const doubles = format === "doubles";
  const participants = doubles
    ? [
        { id: "anika", name: "Anika Shah", teamId: "A" },
        { id: "dev", name: "Dev Mehta", teamId: "A" },
        { id: "maya", name: "Maya Rao", teamId: "B" },
        { id: "rohan", name: "Rohan Nair", teamId: "B" },
      ]
    : [
        { id: "anika", name: "Anika Shah", teamId: "A" },
        { id: "maya", name: "Maya Rao", teamId: "B" },
      ];
  const teamName = doubles ? "Anika & Dev" : "Anika";
  const ourIds = participants
    .filter((person) => person.teamId === "A")
    .map((person) => `person:${person.id}`)
    .concat("team:A");
  const everyone = participants.map((person) => `person:${person.id}`).concat("team:A", "team:B");
  const rallies: HighlightEvidence[] = contactCounts.map((count, index) => ({
    id: `example-rally-${index + 1}`,
    label: `Rally ${index + 1}`,
    start: index * 34 * 30,
    end: (index * 34 + Math.max(4, Math.round(count * 0.65))) * 30,
    shotCount: count,
    outcome: winningSides[index] === "A" ? `${teamName} won` : `${doubles ? "Maya & Rohan" : "Maya"} won`,
  }));
  const longest = rallies.reduce((best, row) => ((row.shotCount ?? 0) > (best.shotCount ?? 0) ? row : best));
  const evidenceAt = (index: number) => (rallies[index] ? [rallies[index]] : []);
  const firstWins = winningSides.slice(0, 20).filter((side) => side === "A").length;
  const lastWins = winningSides.slice(20).filter((side) => side === "A").length;
  const mean = (counts: number[]) =>
    (counts.reduce((sum, count) => sum + count, 0) / counts.length).toFixed(1);
  const lengthRows = [
    { label: "Short · 1–4 shots", low: 1, high: 4 },
    { label: "Medium · 5–8 shots", low: 5, high: 8 },
    { label: "Long · 9+ shots", low: 9, high: Infinity },
  ].map(({ label, low, high }) => {
    const indices = contactCounts.flatMap((count, i) => (count >= low && count <= high ? [i] : []));
    const won = indices.filter((i) => winningSides[i] === "A").length;
    return {
      label,
      value: won,
      max: indices.length,
      display: `${won} / ${indices.length} won`,
      detail: `${Math.round((won / indices.length) * 100)}% · ${teamName}`,
    };
  });
  const resolved = smashOutcomes.filter((outcome) => outcome !== "uncertain").length;
  const converted = smashOutcomes.filter((outcome) => outcome === "direct" || outcome === "forced").length;
  const shared = { origin: "example" as const, subjectIds: everyone, metrics: [], evidence: [] };
  const insights: HighlightInsight[] = [
    {
      ...shared,
      definitionId: "rally",
      headline: "One rally. 28 reasons to replay.",
      summary:
        "The longest exchange of this example session. A rally doesn't have to go your way to be worth keeping.",
      availability: "available",
      support: "40 example rallies · complete illustrative contact counts",
      metrics: [
        { label: "Rally length", value: `${longest.shotCount} shots` },
        { label: "Exchange", value: longest.label },
      ],
      evidence: [longest],
      visual: { kind: "diagram", variant: "rally", illustrated: true },
    },
    {
      ...shared,
      definitionId: "smile",
      headline: "The best part might be yours to pick.",
      summary:
        "The laugh between points. The return you didn't think you'd reach. Keep a moment for your own reasons.",
      availability: "missing",
      support: "A personal selection, not an automatic award",
      visual: { kind: "invitation", label: "A little moment, just for you." },
    },
    {
      ...shared,
      definitionId: "comeback",
      headline: "Five down. Back on level terms.",
      summary: `${teamName} recovered from 9–14 to 14–14 in the same game. The sequence ends at the first tie.`,
      availability: "available",
      support: "Illustrative score sequence · game 1 · rallies 24–28",
      subjectIds: ourIds,
      metrics: [
        { label: "Starting deficit", value: "5 points" },
        { label: "Recovered to", value: "14–14" },
      ],
      evidence: rallies.slice(23, 28),
      visual: {
        kind: "scores",
        points: [
          { label: "Rally 23", value: "9–14" },
          { label: "Rally 25", value: "11–14" },
          { label: "Rally 28", value: "14–14" },
        ],
      },
    },
    {
      ...shared,
      definitionId: "record",
      headline: "A longer rally in your story.",
      summary:
        "Anika's 28-shot exchange beats a previous illustrative record of 24. Rally length counts everyone's contacts, not just Anika's.",
      availability: "available",
      subjectIds: ["person:anika"],
      support: "Example history · 4 linked sessions · same format and count rule",
      metrics: [
        { label: "This session", value: "28 shots" },
        { label: "Previous record", value: "24 shots" },
      ],
      evidence: [longest],
      visual: { kind: "record", previous: 24, current: 28, unit: "shots" },
    },
    {
      ...shared,
      definitionId: "save",
      headline: "The point continued. That was enough.",
      summary:
        "Anika reached a difficult return and kept the exchange alive. The other side won the rally; the save still deserves a look.",
      availability: "available",
      subjectIds: ["person:anika"],
      support: "Illustrative player selection · return success and rally outcome separated",
      metrics: [
        { label: "Immediate return", value: "In play" },
        { label: "Rally outcome", value: "Other side won" },
      ],
      evidence: evidenceAt(30),
      visual: { kind: "diagram", variant: "save", illustrated: true },
    },
    {
      ...shared,
      definitionId: "partnership",
      headline: doubles ? "Some rallies belong to both of you." : "A story for your next doubles session.",
      summary: doubles
        ? "Anika and Dev's shared exchange, with a memory to keep privately. No claim about equal contributions is needed."
        : "Partnership memories need two players on the same team. This example session is singles.",
      availability: doubles ? "available" : "not_applicable",
      subjectIds: ourIds,
      support: doubles
        ? "Illustrative pair membership · personal memory"
        : "Not applicable to this singles example",
      evidence: doubles ? [longest] : [],
      visual: doubles
        ? { kind: "diagram", variant: "pair", illustrated: true }
        : { kind: "invitation", label: "Better together, another time." },
    },
    {
      ...shared,
      definitionId: "halves",
      headline: "A different finish to the game.",
      summary: `${teamName} won ${firstWins} of the first 20 rallies and ${lastWins} of the last 20. A comparison, not a claim about what caused the change.`,
      availability: "available",
      subjectIds: ourIds,
      support: "40 example rallies · split by rally order · known winners",
      metrics: [
        { label: "First-half average", value: `${mean(contactCounts.slice(0, 20))} shots` },
        { label: "Second-half average", value: `${mean(contactCounts.slice(20))} shots` },
      ],
      evidence: [longest, ...evidenceAt(36)],
      visual: {
        kind: "bars",
        rows: [
          {
            label: "First 20 rallies",
            value: firstWins,
            max: 20,
            display: `${firstWins} / 20 won`,
            detail: teamName,
          },
          {
            label: "Last 20 rallies",
            value: lastWins,
            max: 20,
            display: `${lastWins} / 20 won`,
            detail: teamName,
          },
        ],
      },
    },
    {
      ...shared,
      definitionId: "length",
      headline: "Every exchange has its own rhythm.",
      summary: `Short, medium and long rallies for ${teamName}. The counts show what happened, not which style caused a win.`,
      availability: "available",
      subjectIds: ourIds,
      support: "40 example rallies · 0 unknown counts · 0 unknown winners",
      visual: { kind: "bars", rows: lengthRows },
      evidence: [longest],
    },
    {
      ...shared,
      definitionId: "coverage",
      headline: doubles
        ? "See the pair. Leave room for context."
        : "Four-player coverage needs a doubles court.",
      summary: doubles
        ? "Two players can share a side of the court for a good reason. This illustrated interval awaits a coach's coverage review."
        : "Court-coverage gaps for a pair are not inferred from singles positions.",
      availability: doubles ? "review" : "not_applicable",
      subjectIds: ourIds,
      support: doubles
        ? "Illustrated positions · coverage-gap judgement not supplied"
        : "Not applicable to singles",
      evidence: doubles ? evidenceAt(25) : [],
      visual: doubles
        ? { kind: "diagram", variant: "coverage", illustrated: true }
        : { kind: "invitation", label: "A view for your pair." },
    },
    {
      ...shared,
      definitionId: "smash",
      headline: "After the attack, the whole picture.",
      summary: `${converted} immediate winning outcomes from ${resolved} resolved attempts. Continued rallies and own errors stay in the denominator.`,
      availability: "available",
      subjectIds: ["person:anika"],
      support: `${smashOutcomes.length} example attempts · ${smashOutcomes.length - resolved} uncertain outcomes shown separately`,
      metrics: [
        {
          label: "Immediate conversion",
          value: `${Math.round((converted / resolved) * 100)}%`,
          detail: `${converted} / ${resolved} resolved attempts`,
        },
        {
          label: "Outcome coverage",
          value: `${resolved} / ${smashOutcomes.length}`,
          detail: "Illustrative attempts",
        },
      ],
      evidence: evidenceAt(33),
      visual: {
        kind: "bars",
        rows: [
          ["direct", "Direct winner"],
          ["forced", "Forced error"],
          ["continued", "Rally continued"],
          ["own", "Own error"],
          ["uncertain", "Uncertain"],
        ].map(([key, label]) => ({
          label: label ?? "Unknown",
          value: smashOutcomes.filter((outcome) => outcome === key).length,
          max: smashOutcomes.length,
          display: String(smashOutcomes.filter((outcome) => outcome === key).length),
        })),
      },
    },
  ];
  return {
    id: `example-${format}`,
    sport: "badminton",
    title: doubles ? "Anika & Dev · evening doubles" : "Anika & Maya · evening singles",
    format,
    example: true,
    revision: 1,
    sourceKey: `synthetic-highlights-v1:${format}`,
    media: {
      fps_num: 30,
      fps_den: 1,
      n_frames: 42600,
      width: 1920,
      height: 1080,
      duration_us: 1420000000,
      has_audio: false,
    },
    participants,
    teams: [
      { id: "A", name: teamName },
      { id: "B", name: doubles ? "Maya & Rohan" : "Maya" },
    ],
    definitions: badmintonHighlights,
    insights,
    rallies,
    scope: "40 illustrative rallies · one game · no source video",
  };
}
