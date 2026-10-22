/**
 * Insight narration.
 *
 * Every sentence under a chart is generated HERE, from the derived numbers, with the frame
 * of the evidence attached. Nothing is written by hand against a specific fixture, so the
 * narration stays true if the data changes — and anything it says can be opened in the
 * player and watched.
 *
 * This is the deterministic layer an LLM would sit on top of: the agent picks and phrases,
 * it never invents the number.
 */

import type { Insight, Match, PlayerId, Rally } from "./types";
import { STROKE_FAMILY, STROKE_LABEL, type Zone } from "./types";

const ZONE_WORD: Record<Zone, string> = {
  "front-left": "the forecourt on your left",
  "front-centre": "the middle of the forecourt",
  "front-right": "the forecourt on your right",
  "mid-left": "the midcourt on your left",
  "mid-centre": "the middle of the court",
  "mid-right": "the midcourt on your right",
  "rear-left": "the rear court on your left",
  "rear-centre": "the middle of the rear court",
  "rear-right": "the rear court on your right",
};

function nameOf(match: Match, id: PlayerId) {
  return match.players.find((p) => p.id === id)?.short ?? id;
}

function officialRallies(match: Match) {
  return match.rallies.filter((r) => r.official);
}

function longestRally(match: Match): Rally | undefined {
  return officialRallies(match).sort((a, b) => b.shots.length - a.shots.length)[0];
}

function topZone(counts: Record<Zone, number>): { zone: Zone; share: number } | null {
  const entries = Object.entries(counts) as [Zone, number][];
  const total = entries.reduce((a, [, v]) => a + v, 0);
  if (total === 0) return null;
  const top = entries.sort((a, b) => b[1] - a[1])[0];
  if (!top) return null;
  return { zone: top[0], share: top[1] / total };
}

/* ───────────────────────── the match at a glance ───────────────────────── */

export function overviewInsights(match: Match, pid: PlayerId): Insight[] {
  const out: Insight[] = [];
  const st = match.stats[pid];
  if (!st) return out;
  const offs = officialRallies(match);
  const lr = longestRally(match);

  if (lr) {
    out.push({
      text: `The longest rally of the match ran to ${lr.shots.length} shots. You played ${lr.shots.filter((s) => s.player === pid).length} of them.`,
      frame: lr.frames[0],
      tone: "neutral",
    });
  }

  // Halves split — the kind of thing an amateur actually notices.
  const half = Math.floor(offs.length / 2);
  const firstLong = offs.slice(0, half).filter((r) => r.shots.length >= 8).length;
  const secondLong = offs.slice(half).filter((r) => r.shots.length >= 8).length;
  if (firstLong + secondLong >= 4) {
    const more = secondLong > firstLong;
    out.push({
      text: `Long rallies were ${more ? "more" : "less"} common later on — ${firstLong} in the first half of the match, ${secondLong} in the second.`,
      frame: offs[half]?.frames[0],
      tone: "neutral",
    });
  }

  const returnRate = st.returnsMade / Math.max(1, st.returnsAttempted);
  out.push({
    text: `You kept ${st.returnsMade} of your ${st.returnsAttempted} returns in play — ${Math.round(returnRate * 100)}% of the shots you had a chance to play.`,
    tone: returnRate > 0.8 ? "strength" : "neutral",
  });

  if (st.defensiveSaves >= 3) {
    const r = offs.find((x) => x.shots.some((s) => s.player === pid && STROKE_FAMILY[s.stroke] === "defend"));
    out.push({
      text: `${st.defensiveSaves} times you played from under the shuttle and stayed in the rally.`,
      frame: r?.frames[0],
      tone: "strength",
    });
  }

  if (st.errorsOut + st.errorsNet > 0) {
    const worse = st.errorsOut >= st.errorsNet ? "long or wide" : "into the net";
    out.push({
      text: `${st.errorsOut + st.errorsNet} rallies ended on your racket — more often ${worse} (${Math.max(st.errorsOut, st.errorsNet)} of them).`,
      tone: "watch",
    });
  }

  return out;
}

/* ───────────────────────── shots ───────────────────────── */

export function shotInsights(match: Match, pid: PlayerId): Insight[] {
  const out: Insight[] = [];
  const st = match.stats[pid];
  if (!st) return out;

  const entries = Object.entries(st.strokes)
    .filter(([k]) => k !== "jump_smash")
    .sort((a, b) => b[1] - a[1]);
  // A jump smash is a subtype, not a separate shot: it is excluded from the
  // ranking above but must stay in the denominator, or this figure disagrees
  // with the shot count on the same screen.
  const total = st.shotsPlayed;
  const top = entries[0];
  if (top && total > 0) {
    out.push({
      text: `Your most played shot was the ${(STROKE_LABEL[top[0]] ?? top[0]).toLowerCase()} — ${top[1]} of ${total} shots, about ${Math.round((top[1] / total) * 100)}%.`,
      tone: "neutral",
    });
  }

  const fam = st.familySplit;
  const famTotal = fam.attack + fam.neutral + fam.defend;
  if (famTotal > 0) {
    out.push({
      text: `You spent ${Math.round((fam.attack / famTotal) * 100)}% of your shots attacking, ${Math.round((fam.neutral / famTotal) * 100)}% in neutral exchanges and ${Math.round((fam.defend / famTotal) * 100)}% defending.`,
      tone: "neutral",
    });
  }

  if (st.smashes > 0) {
    const conv = st.smashPoints / st.smashes;
    const smashRally = officialRallies(match).find((r) =>
      r.shots.some((s) => s.player === pid && s.stroke === "smash" && s.decisive),
    );
    out.push({
      text: `${st.smashes} smashes${st.jumpSmashes ? `, ${st.jumpSmashes} of them jumping` : ""}. ${st.smashPoints} of them finished the rally — ${Math.round(conv * 100)}%.`,
      frame: smashRally?.frames[0],
      tone: conv > 0.3 ? "strength" : "neutral",
    });
  }

  const rare = entries.filter(([, v]) => v > 0 && v <= 2).map(([k]) => (STROKE_LABEL[k] ?? k).toLowerCase());
  if (rare.length >= 2) {
    out.push({
      text: `You played ${st.repertoire} different shot types. The rarest were the ${rare.slice(0, 2).join(" and the ")} — one or two each.`,
      tone: "neutral",
    });
  }

  return out;
}

/* ───────────────────────── court and placement ───────────────────────── */

export function courtInsights(match: Match, pid: PlayerId, kind: string): Insight[] {
  const st = match.stats[pid];
  if (!st) return [];
  const out: Insight[] = [];

  if (kind === "origin" || kind === "presence" || kind === "movement") {
    const t = topZone(st.originZones);
    if (t) {
      out.push({
        text: `Most of your shots came from ${ZONE_WORD[t.zone]} — about ${Math.round(t.share * 100)}% of them.`,
        tone: "neutral",
      });
    }
    const rearShare =
      (st.originZones["rear-left"] + st.originZones["rear-centre"] + st.originZones["rear-right"]) /
      Math.max(1, st.shotsPlayed);
    const frontShare =
      (st.originZones["front-left"] + st.originZones["front-centre"] + st.originZones["front-right"]) /
      Math.max(1, st.shotsPlayed);
    out.push({
      text: `You hit ${Math.round(rearShare * 100)}% of your shots from the rear court and ${Math.round(frontShare * 100)}% from the front.`,
      tone: "neutral",
    });
  }

  if (kind === "targeting" || kind === "landing") {
    const t = topZone(st.targetZones);
    if (t) {
      out.push({
        text: `Your opponents most often met your shots in ${ZONE_WORD[t.zone].replace("your", "their")} — about ${Math.round(t.share * 100)}% of the time.`,
        tone: "neutral",
      });
    }
    const left = st.targetZones["front-left"] + st.targetZones["mid-left"] + st.targetZones["rear-left"];
    const right = st.targetZones["front-right"] + st.targetZones["mid-right"] + st.targetZones["rear-right"];
    const skew = Math.abs(left - right) / Math.max(1, left + right);
    out.push({
      text:
        skew < 0.12
          ? "You spread your shots fairly evenly between their left and right."
          : `You favoured their ${left > right ? "left" : "right"} side — ${Math.round((Math.max(left, right) / Math.max(1, left + right)) * 100)}% of your shots went there.`,
      tone: skew < 0.12 ? "strength" : "watch",
    });
  }

  return out;
}

/* ───────────────────────── movement and work rate ───────────────────────── */

export function movementInsights(match: Match, pid: PlayerId): Insight[] {
  const st = match.stats[pid];
  if (!st) return [];
  const out: Insight[] = [];
  const activeMin = st.activeS / 60;

  out.push({
    text: `You covered about ${st.distanceM} m on court — roughly ${st.steps.toLocaleString()} steps — in ${activeMin.toFixed(1)} minutes of actual play.`,
    tone: "neutral",
  });

  const perRally = st.distanceM / Math.max(1, st.ralliesPlayed);
  out.push({
    text: `That is about ${perRally.toFixed(1)} m per rally. The longest rally alone accounted for roughly ${(((longestRally(match)?.shots.length ?? 0) / Math.max(1, st.shotsPlayed)) * st.distanceM).toFixed(0)} m.`,
    frame: longestRally(match)?.frames[0],
    tone: "neutral",
  });

  const others = match.players.filter((p) => p.id !== pid);
  const mine = st.distanceM;
  const theirs = others.map((p) => match.stats[p.id]?.distanceM ?? 0);
  const maxOther = Math.max(0, ...theirs);
  if (maxOther > 0) {
    const diff = Math.round(((mine - maxOther) / maxOther) * 100);
    out.push({
      text:
        Math.abs(diff) < 8
          ? "You and your opponents covered a similar amount of ground."
          : `You covered ${Math.abs(diff)}% ${diff > 0 ? "more" : "less"} ground than the busiest player on the other side.`,
      tone: "neutral",
    });
  }

  const rate = st.distanceM / Math.max(1, activeMin);
  out.push({
    text: `Your work rate was about ${rate.toFixed(0)} m per minute of play. This is an estimate from tracked position, not a fitness measurement.`,
    tone: "neutral",
  });

  return out;
}

/* ───────────────────────── rallies ───────────────────────── */

export function rallyInsights(match: Match, pid: PlayerId): Insight[] {
  const offs = officialRallies(match);
  if (offs.length === 0) return [];
  const lens = offs.map((r) => r.shots.length);
  const avg = lens.reduce((a, b) => a + b, 0) / lens.length;
  const short = offs.filter((r) => r.shots.length <= 4).length;
  const long = offs.filter((r) => r.shots.length >= 8).length;
  const out: Insight[] = [
    {
      text: `${offs.length} counted rallies, ${avg.toFixed(1)} shots on average. ${short} ended within four shots; ${long} ran to eight or more.`,
      tone: "neutral",
    },
  ];

  const yoursEnded = offs.filter(
    (r) => r.shots[r.shots.length - 1]?.player === pid && r.outcome !== "winner",
  );
  if (yoursEnded.length) {
    const avgLen = yoursEnded.reduce((a, r) => a + r.shots.length, 0) / yoursEnded.length;
    out.push({
      text: `The rallies that ended on your racket were ${avgLen.toFixed(1)} shots long on average, against ${avg.toFixed(1)} overall.`,
      frame: yoursEnded[0]?.frames[0],
      tone: avgLen < avg ? "watch" : "neutral",
    });
  }

  const byServe = offs.filter((r) => r.server === pid);
  const wonOnServe = byServe.filter((r) => r.winner === match.players.find((p) => p.id === pid)?.side);
  if (byServe.length >= 5) {
    out.push({
      text: `You served in ${byServe.length} rallies and won ${wonOnServe.length} of them.`,
      tone: "neutral",
    });
  }

  return out;
}

/* ───────────────────────── head to head ───────────────────────── */

export function h2hInsights(match: Match, pid: PlayerId): Insight[] {
  const me = match.stats[pid];
  const opponents = match.players.filter((p) => p.side !== match.players.find((x) => x.id === pid)?.side);
  const them = opponents.map((p) => match.stats[p.id]).filter(Boolean);
  if (!me || them.length === 0) return [];
  const out: Insight[] = [];

  const theirWinners = them.reduce((a, s) => a + (s?.winners ?? 0), 0);
  const theirErrors = them.reduce((a, s) => a + (s?.errorsOut ?? 0) + (s?.errorsNet ?? 0), 0);
  out.push({
    text: `Winners: ${me.winners} to ${theirWinners}. Unforced endings: ${me.errorsOut + me.errorsNet} to ${theirErrors}.`,
    tone: "neutral",
  });

  const theirSmashes = them.reduce((a, s) => a + (s?.smashes ?? 0), 0);
  if (me.smashes + theirSmashes > 0) {
    out.push({
      text: `Smashes: ${me.smashes} from you, ${theirSmashes} from the other side.`,
      tone: "neutral",
    });
  }

  if (me.pointsWonUnderPressure > 0) {
    out.push({
      text: `${me.pointsWonUnderPressure} of your points came at 20-all or on a game point.`,
      tone: "strength",
    });
  }

  return out;
}

/* ───────────────────────── doubles: the pair ───────────────────────── */

export function pairInsights(match: Match, pid: PlayerId): Insight[] {
  const me = match.players.find((p) => p.id === pid);
  const pair = me && match.pairs ? match.pairs[me.side] : undefined;
  if (!me || !pair) return [];
  const partnerId = pair.players.find((x) => x !== pid) as PlayerId | undefined;
  if (!partnerId) return [];
  const partner = nameOf(match, partnerId);
  const out: Insight[] = [];

  out.push({
    text: `You and ${partner} both hit the shuttle in ${pair.bothContributed} of your rallies. The longest you built together ran to ${pair.longestSharedRally} shots.`,
    tone: "strength",
  });

  if (pair.rescues > 0) {
    out.push({
      text: `${pair.rescues} times one of you played from under the shuttle and the other took the next shot.`,
      tone: "strength",
    });
  }

  if (pair.attackCombos > 0) {
    out.push({
      text: `${pair.attackCombos} rear-court attacks were followed by an interception at the net from your partner.`,
      tone: "strength",
    });
  }

  const mine = pair.frontRear[pid];
  const theirs = pair.frontRear[partnerId];
  if (mine && theirs) {
    const myFrontShare = mine.front / Math.max(1, mine.front + mine.rear);
    const theirFrontShare = theirs.front / Math.max(1, theirs.front + theirs.rear);
    out.push({
      text:
        Math.abs(myFrontShare - theirFrontShare) > 0.18
          ? `You took the ${myFrontShare > theirFrontShare ? "front" : "rear"} more often — ${Math.round(Math.max(myFrontShare, 1 - myFrontShare) * 100)}% of your shots — while ${partner} covered the other.`
          : `You and ${partner} split the front and rear court fairly evenly.`,
      tone: "neutral",
    });
  }

  return out;
}

/* ───────────────────────── momentum ───────────────────────── */

export function momentumInsights(match: Match, pid: PlayerId): Insight[] {
  const me = match.players.find((p) => p.id === pid);
  if (!me || match.momentum.length < 4) return [];
  const runs = match.momentum.filter((m) => m.run.side === me.side);
  const longestRun = runs.sort((a, b) => b.run.length - a.run.length)[0];
  const out: Insight[] = [
    {
      text: `The lead changed hands ${match.momentumShifts.length} times across the match.`,
      tone: "neutral",
    },
  ];
  if (longestRun && longestRun.run.length >= 3) {
    const rally = match.rallies.find((r) => r.no === longestRun.rallyNo);
    out.push({
      text: `Your longest run was ${longestRun.run.length} points in a row, ending at rally ${longestRun.rallyNo}.`,
      frame: rally?.frames[0],
      tone: "strength",
    });
  }
  return out;
}

export type { Insight };
