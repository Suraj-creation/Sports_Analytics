/**
 * The fixture set.
 *
 * Five matches chosen to exercise what matters: a singles match the player LOST (so the
 * product can be checked for loss parity), a doubles match (partner analytics, pair
 * chemistry), an older singles match to compare against, one still analysing, one that
 * failed. Everything numeric is derived by `buildMatch` from generated rallies and shots.
 */

import { buildMatch, FPS } from "./generate";
import type { Match, Player, PlayerId } from "./types";

export { FPS };

export const VENUE = "Smash Point Arena";
export const YOU: PlayerId = "alex";

const you = (end: "near" | "far"): Player => ({
  id: YOU,
  name: "Alex",
  short: "Alex",
  side: "A",
  end,
  isYou: true,
  colour: "you",
});

/* ───────────────────────── singles, and you lost it ───────────────────────── */

const singlesNow = buildMatch({
  id: "m1",
  title: "Thursday evening singles",
  date: "2026-10-15",
  venue: VENUE,
  court: "Court 3",
  discipline: "singles",
  seed: 7,
  // A is you. You take the second game and lose the decider — loss parity matters.
  games: [
    [17, 21],
    [21, 19],
    [18, 21],
  ],
  followedRatio: 0.88,
  coverageReason:
    "Three rallies were partly hidden behind the net post, and two happened while the second camera was live.",
  durationMin: 52,
  players: [
    you("near"),
    {
      id: "rahul",
      name: "Rahul",
      short: "Rahul",
      side: "B",
      end: "far",
      isYou: false,
      colour: "opponent-1",
    },
  ],
});

/* ───────────────────────── doubles ───────────────────────── */

const doubles = buildMatch({
  id: "m2",
  title: "Sunday doubles",
  date: "2026-10-18",
  venue: VENUE,
  court: "Court 1",
  discipline: "doubles",
  seed: 23,
  games: [
    [21, 18],
    [19, 21],
    [21, 17],
  ],
  followedRatio: 0.84,
  coverageReason:
    "Four rallies ran into the corner the camera can't see past the post, so they aren't counted.",
  durationMin: 61,
  players: [
    { ...you("near"), partnerId: "priya" },
    {
      id: "priya",
      name: "Priya",
      short: "Priya",
      side: "A",
      end: "near",
      isYou: false,
      partnerId: YOU,
      colour: "partner",
    },
    {
      id: "rahul",
      name: "Rahul",
      short: "Rahul",
      side: "B",
      end: "far",
      isYou: false,
      partnerId: "meera",
      colour: "opponent-1",
    },
    {
      id: "meera",
      name: "Meera",
      short: "Meera",
      side: "B",
      end: "far",
      isYou: false,
      partnerId: "rahul",
      colour: "opponent-2",
    },
  ],
});

/* ───────────────────────── two weeks earlier, same opponent ───────────────────────── */

const singlesBefore = buildMatch({
  id: "m3",
  title: "Thursday evening singles",
  date: "2026-10-01",
  venue: VENUE,
  court: "Court 3",
  discipline: "singles",
  seed: 41,
  games: [
    [21, 15],
    [16, 21],
    [19, 21],
  ],
  followedRatio: 0.9,
  coverageReason: "Three rallies were partly hidden behind the net post.",
  durationMin: 46,
  players: [
    you("near"),
    {
      id: "rahul",
      name: "Rahul",
      short: "Rahul",
      side: "B",
      end: "far",
      isYou: false,
      colour: "opponent-1",
    },
  ],
});

/* ── the camera was moved mid-session: most of it could not be followed ── */

const lowCoverage = buildMatch({
  id: "m6",
  title: "Tuesday club night",
  date: "2026-10-13",
  venue: VENUE,
  court: "Court 5",
  discipline: "singles",
  seed: 61,
  games: [
    [21, 16],
    [14, 21],
  ],
  followedRatio: 0.44,
  coverageReason:
    "The camera on Court 5 was repositioned partway through, so the court fit was wrong for most of the second game and those rallies were not followed.",
  durationMin: 48,
  players: [
    you("near"),
    {
      id: "meera",
      name: "Meera",
      short: "Meera",
      side: "B",
      end: "far",
      isYou: false,
      colour: "opponent-1",
    },
  ],
});

/* ───────────────────────── in-flight and failed ───────────────────────── */

const analysing: Match = {
  ...buildMatch({
    id: "m4",
    title: "Tuesday club night",
    date: "2026-10-20",
    venue: VENUE,
    court: "Court 5",
    discipline: "doubles",
    seed: 99,
    games: [[21, 19]],
    followedRatio: 0.8,
    coverageReason: "Still watching.",
    durationMin: 44,
    players: [
      { ...you("near"), partnerId: "sam" },
      {
        id: "sam",
        name: "Sam",
        short: "Sam",
        side: "A",
        end: "near",
        isYou: false,
        partnerId: YOU,
        colour: "partner",
      },
      {
        id: "dev",
        name: "Dev",
        short: "Dev",
        side: "B",
        end: "far",
        isYou: false,
        partnerId: "nina",
        colour: "opponent-1",
      },
      {
        id: "nina",
        name: "Nina",
        short: "Nina",
        side: "B",
        end: "far",
        isYou: false,
        partnerId: "dev",
        colour: "opponent-2",
      },
    ],
  }),
  status: "analysing",
  progress: 0.64,
};

const failed: Match = {
  ...buildMatch({
    id: "m5",
    title: "Last Thursday",
    date: "2026-10-08",
    venue: VENUE,
    court: "Court 3",
    discipline: "singles",
    seed: 13,
    games: [[4, 2]],
    followedRatio: 0.3,
    coverageReason: "The recording stopped about four minutes in.",
    durationMin: 4,
    players: [
      you("near"),
      {
        id: "rahul",
        name: "Rahul",
        short: "Rahul",
        side: "B",
        end: "far",
        isYou: false,
        colour: "opponent-1",
      },
    ],
  }),
  status: "failed",
};

export const matches: Match[] = [analysing, doubles, singlesNow, lowCoverage, singlesBefore, failed].sort(
  (a, b) => (a.date < b.date ? 1 : -1),
);

export const readyMatches = matches.filter((m) => m.status === "ready");

/**
 * Matches fit to compare with each other.
 *
 * A match where the camera moved is still worth watching, but putting it on a trend
 * line next to a clean one compares two different measurements and calls the gap
 * progress. Below 70% followed, it is excluded from trends and records and the
 * Progress page says so.
 */
export const COMPARABLE_FLOOR = 0.7;
export const comparableMatches = readyMatches.filter(
  (m) => m.coverage.followed / Math.max(1, m.coverage.total) >= COMPARABLE_FLOOR,
);
export const excludedMatches = readyMatches.filter((m) => !comparableMatches.includes(m));

export function getMatch(id: string): Match | undefined {
  return matches.find((m) => m.id === id);
}

export function playerOf(match: Match, id: PlayerId) {
  return match.players.find((p) => p.id === id);
}

/**
 * Re-centre a match on the player who said they are themselves.
 *
 * The fixture ships a default "you", but once someone has picked themselves out of the
 * four on court, every "you" in the product has to mean that person — the colour, the
 * shape, the pair surface, the narration. Doing it here keeps that single decision from
 * having to be remembered by thirty components.
 */
export function applyIdentity(
  match: Match,
  meId: PlayerId | undefined,
  nicknames: Record<PlayerId, string> = {},
): Match {
  const me = match.players.find((p) => p.id === meId);
  const named = (p: Player) => nicknames[p.id] ?? p.short;
  if (!me) {
    return {
      ...match,
      players: match.players.map((p) => ({ ...p, short: named(p) })),
    };
  }
  let opponentIndex = 0;
  const players = match.players.map((p): Player => {
    const isYou = p.id === me.id;
    const samePartner = !isYou && p.side === me.side;
    const colour: Player["colour"] = isYou
      ? "you"
      : samePartner
        ? "partner"
        : ((opponentIndex++ === 0 ? "opponent-1" : "opponent-2") as Player["colour"]);
    return {
      ...p,
      short: named(p),
      isYou,
      colour,
      partnerId: samePartner
        ? me.id
        : isYou
          ? match.players.find((x) => x.side === p.side && x.id !== p.id)?.id
          : p.partnerId,
    };
  });
  const sides = {
    A: {
      ...match.sides.A,
      label: match.sides.A.players.map((id) => named(players.find((p) => p.id === id) as Player)).join(" & "),
    },
    B: {
      ...match.sides.B,
      label: match.sides.B.players.map((id) => named(players.find((p) => p.id === id) as Player)).join(" & "),
    },
  };
  return { ...match, players, sides };
}

export function youIn(match: Match) {
  return match.players.find((p) => p.isYou) ?? (match.players[0] as Player);
}

export function partnerIn(match: Match): Player | undefined {
  const me = youIn(match);
  return match.players.find((p) => p.id === me.partnerId);
}

export function opponentsIn(match: Match): Player[] {
  const me = youIn(match);
  return match.players.filter((p) => p.side !== me.side);
}

/* ───────────────────────── across matches ───────────────────────── */

export interface Record_ {
  id: string;
  label: string;
  value: number;
  unit: string;
  matchId: string;
  date: string;
  previous: number | null;
  definition: string;
}

function yourStats(m: Match) {
  return m.stats[youIn(m).id];
}

export const records: Record_[] = (() => {
  const ordered = comparableMatches.slice().sort((a, b) => (a.date < b.date ? -1 : 1));
  const out: Record_[] = [];
  const track = (id: string, label: string, unit: string, definition: string, get: (m: Match) => number) => {
    let best = 0;
    let bestMatch = ordered[0] as Match;
    let previous: number | null = null;
    for (const m of ordered) {
      const v = get(m);
      if (v > best) {
        previous = best || null;
        best = v;
        bestMatch = m;
      }
    }
    out.push({
      id,
      label,
      value: Math.round(best),
      unit,
      matchId: bestMatch.id,
      date: bestMatch.date,
      previous: previous ? Math.round(previous) : null,
      definition,
    });
  };
  track("longest-rally", "Longest rally", "shots", "The most shots counted in one rally.", (m) =>
    Math.max(...m.rallies.filter((r) => r.official).map((r) => r.shots.length)),
  );
  track(
    "long-rallies",
    "Rallies of 8+ shots",
    "rallies",
    "Rallies in which eight or more shots were counted.",
    (m) => m.rallies.filter((r) => r.official && r.shots.length >= 8).length,
  );
  track(
    "distance",
    "Distance covered",
    "m",
    "Estimated court movement while the shuttle was in play, from tracked position.",
    (m) => yourStats(m)?.distanceM ?? 0,
  );
  track(
    "steps",
    "Steps on court",
    "steps",
    "Estimated from distance covered at an average stride of 0.78 m.",
    (m) => yourStats(m)?.steps ?? 0,
  );
  track(
    "repertoire",
    "Shot types played",
    "types",
    "Distinct shot names the classifier assigned to your shots in one match.",
    (m) => yourStats(m)?.repertoire ?? 0,
  );
  track(
    "defence",
    "Defensive saves",
    "saves",
    "Shots played from under the shuttle that you followed with another shot in the same rally.",
    (m) => yourStats(m)?.defensiveSaves ?? 0,
  );
  return out;
})();

export interface TrendSeries {
  id: string;
  label: string;
  unit: string;
  points: { matchId: string; date: string; value: number; discipline: string }[];
  definition: string;
}

export const trends: TrendSeries[] = (() => {
  const ordered = comparableMatches.slice().sort((a, b) => (a.date < b.date ? -1 : 1));
  const series = (
    id: string,
    label: string,
    unit: string,
    definition: string,
    get: (m: Match) => number,
  ): TrendSeries => ({
    id,
    label,
    unit,
    definition,
    points: ordered.map((m) => ({
      matchId: m.id,
      date: m.date,
      value: Math.round(get(m)),
      discipline: m.discipline,
    })),
  });
  return [
    series("longest-rally", "Longest rally", "shots", "The most shots in one rally.", (m) =>
      Math.max(...m.rallies.filter((r) => r.official).map((r) => r.shots.length)),
    ),
    series("avg-rally", "Average rally length", "shots", "Mean shots per counted rally.", (m) => {
      const off = m.rallies.filter((r) => r.official);
      return off.reduce((a, r) => a + r.shots.length, 0) / Math.max(1, off.length);
    }),
    series(
      "distance",
      "Distance covered",
      "m",
      "Estimated movement while the shuttle was in play.",
      (m) => yourStats(m)?.distanceM ?? 0,
    ),
    series(
      "returns",
      "Returns kept in play",
      "%",
      "Share of your returns that kept the rally alive.",
      (m) => {
        const s = yourStats(m);
        return s ? (s.returnsMade / Math.max(1, s.returnsAttempted)) * 100 : 0;
      },
    ),
    series(
      "repertoire",
      "Shot types played",
      "types",
      "Distinct shot names observed.",
      (m) => yourStats(m)?.repertoire ?? 0,
    ),
    series(
      "defence",
      "Defensive saves",
      "saves",
      "Shots from under the shuttle you followed up.",
      (m) => yourStats(m)?.defensiveSaves ?? 0,
    ),
  ];
})();

/** Who you have played with and against, across the fixture set. */
export interface PartnerRow {
  id: PlayerId;
  name: string;
  role: "partner" | "opponent";
  matches: number;
  lastPlayed: string;
  /** Rallies you both appeared in. */
  shared: number;
  bestTogether?: { matchId: string; shots: number };
}

export const people: PartnerRow[] = (() => {
  const map = new Map<PlayerId, PartnerRow>();
  for (const m of readyMatches) {
    const me = youIn(m);
    for (const p of m.players) {
      if (p.isYou) continue;
      const role = p.side === me.side ? "partner" : "opponent";
      const row = map.get(p.id) ?? {
        id: p.id,
        name: p.name,
        role,
        matches: 0,
        lastPlayed: m.date,
        shared: 0,
      };
      row.matches += 1;
      row.role = role;
      if (m.date > row.lastPlayed) row.lastPlayed = m.date;
      row.shared += m.rallies.filter((r) => r.official).length;
      if (role === "partner") {
        const best = Math.max(
          0,
          ...m.rallies
            .filter((r) => r.official && new Set(r.shots.map((s) => s.player)).has(p.id))
            .map((r) => r.shots.length),
        );
        if (!row.bestTogether || best > row.bestTogether.shots) {
          row.bestTogether = { matchId: m.id, shots: best };
        }
      }
      map.set(p.id, row);
    }
  }
  return [...map.values()].sort((a, b) => (a.lastPlayed < b.lastPlayed ? 1 : -1));
})();

export interface JourneyEntry {
  id: string;
  date: string;
  kind: "match" | "record" | "first" | "partner";
  title: string;
  detail: string;
  matchId: string | null;
}

export const journey: JourneyEntry[] = (() => {
  const out: JourneyEntry[] = [];
  for (const m of readyMatches) {
    const s = yourStats(m);
    out.push({
      id: `j-${m.id}`,
      date: m.date,
      kind: "match",
      title: m.title,
      detail: `${m.rallies.filter((r) => r.official).length} rallies · ${s?.shotsPlayed ?? 0} shots you played · ${s?.distanceM ?? 0} m covered`,
      matchId: m.id,
    });
  }
  const pb = records.find((x) => x.id === "longest-rally");
  if (pb) {
    out.push({
      id: "j-pb",
      date: pb.date,
      kind: "record",
      title: `Longest rally — ${pb.value} shots`,
      detail: pb.previous ? `Your previous best was ${pb.previous}.` : "Your first recorded best.",
      matchId: pb.matchId,
    });
  }
  out.push({
    id: "j-doubles",
    date: doubles.date,
    kind: "partner",
    title: "First doubles match with Priya",
    detail: `You both hit in ${doubles.pairs?.A.bothContributed ?? 0} of the rallies you won.`,
    matchId: doubles.id,
  });
  return out.sort((a, b) => (a.date < b.date ? 1 : -1));
})();

export const askSuggestions = [
  "What was my longest rally?",
  "How did my defence hold up?",
  "Where did Rahul attack me?",
  "How much did I run?",
  "Did Priya and I cover the court well?",
  "What should I practise?",
];
