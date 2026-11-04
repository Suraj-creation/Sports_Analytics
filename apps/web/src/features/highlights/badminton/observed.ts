import type { MatchSummary } from "@/features/product/types";
import type { HighlightCollection, HighlightEvidence, HighlightInsight } from "../types";
import { badmintonHighlights } from "./catalogue";

function object(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}
function number(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : null;
}

/** Display existing server results. New scoring, history and tactical inference stay out. */
export function recordingCollection(
  match: MatchSummary,
  snapshot: unknown,
  subjectId: string,
): HighlightCollection {
  const data = object(snapshot);
  if (!data || data.schema_version !== 1 || !Array.isArray(data.rallies)) {
    throw new Error(
      "This recording's insight response is not supported. Its existing Moments view is still available.",
    );
  }
  const session = match.session;
  const roster = session.roster;
  const participants = (roster?.participants ?? []).map((person, index) => ({
    id: person.participant_id,
    name: person.name || `Unnamed participant ${index + 1}`,
    teamId: person.team_id,
  }));
  const teams = roster?.teams.length
    ? roster.teams.map((team, index) => ({
        id: team.team_id,
        name:
          participants
            .filter((person) => person.teamId === team.team_id)
            .map((person) => person.name)
            .join(" & ") || `Side ${index + 1}`,
      }))
    : [
        { id: "P1", name: session.players.find((p) => p.player_id === "P1")?.name || "Side 1" },
        { id: "P2", name: session.players.find((p) => p.player_id === "P2")?.name || "Side 2" },
      ];
  const sideName = (slot: string) => {
    const teamId = roster?.teams.find((team) => team.score_slot === slot)?.team_id ?? slot;
    return teams.find((team) => team.id === teamId)?.name ?? "Unresolved side";
  };
  const rallies: HighlightEvidence[] = data.rallies.flatMap((value) => {
    const row = object(value);
    if (!row || row.official !== true || typeof row.rally_id !== "string") return [];
    const start = number(row.frame_start);
    const end = number(row.frame_end);
    if (start === null || end === null || !Number.isInteger(start) || !Number.isInteger(end) || end < start)
      return [];
    return [
      {
        id: row.rally_id,
        label: typeof row.rally_no === "number" ? `Rally ${row.rally_no}` : "Recorded rally",
        start,
        end,
        shotCount: Number.isInteger(row.n_shots) ? number(row.n_shots) : null,
        outcome:
          row.winner === "P1" || row.winner === "P2"
            ? `Winning-side hypothesis: ${sideName(row.winner)} · point acceptance not verified here`
            : null,
        eventStatus: typeof row.status === "string" ? row.status : undefined,
        evidenceBand: typeof row.band === "string" ? row.band : undefined,
        modelScore: number(row.confidence),
        scoreAvailable: row.score_available === true,
      },
    ];
  });
  const configuredFormat = roster?.match_format ?? session.meta.match_format;
  const format =
    configuredFormat === "singles" || configuredFormat === "doubles" ? configuredFormat : "unknown";
  const revision = typeof session.meta.analysis_revision === "number" ? session.meta.analysis_revision : 0;
  const chosenPerson = participants.find((person) => `person:${person.id}` === subjectId);
  const chosenTeamId = chosenPerson?.teamId ?? (subjectId.startsWith("team:") ? subjectId.slice(5) : null);
  const chosenSlot =
    roster?.teams.find((team) => team.team_id === chosenTeamId)?.score_slot ??
    (chosenTeamId === "P1" || chosenTeamId === "P2" ? chosenTeamId : null);
  const insights: HighlightInsight[] = badmintonHighlights.map((definition) => ({
    definitionId: definition.id,
    headline: definition.question,
    summary:
      definition.id === "smile"
        ? "Choose a moment for your own reasons. Your selection stays a private draft on this device."
        : "This insight needs supporting evidence before it can tell your story.",
    availability: "missing",
    origin: "observed",
    support: definition.requires.join(" · "),
    subjectIds: [],
    metrics: [],
    evidence: [],
    visual: { kind: "invitation", label: definition.title },
  }));
  const update = (id: string, changes: Partial<HighlightInsight>) => {
    const item = insights.find((insight) => insight.definitionId === id);
    if (item) Object.assign(item, changes);
  };
  const longestCount = match.availability.analytics ? match.analytics?.longest_rally_shots : null;
  if (longestCount != null && longestCount > 0) {
    const candidates = rallies.filter((rally) => rally.shotCount === longestCount);
    update("rally", {
      headline: `${longestCount} shots. Worth another look.`,
      summary:
        "The server's longest observed rally count. Observed contacts still need human review before this becomes a verified match record. Your favourite is a separate choice.",
      availability: "review",
      metrics: [{ label: "Longest observed", value: `${longestCount} shots` }],
      evidence: candidates,
      support: candidates.length
        ? "Server result · unverified contact completeness"
        : "Server count available · matching source interval not supplied",
    });
  }
  const comeback = match.highlights.find((highlight) => highlight.categories.includes("comeback"));
  if (comeback) {
    const evidence = rallies.find((rally) => rally.id === comeback.rally_id);
    update("comeback", {
      headline: "A possible turning point.",
      availability: "review",
      summary:
        "The existing ranker suggested this rally. Review the score sequence and its starting deficit before accepting a comeback.",
      evidence: evidence ? [evidence] : [],
      support: "Ranker suggestion · complete recovery sequence not verified",
    });
  }
  update("record", {
    summary:
      "Link this player to previous reviewed sessions. Matching display names do not establish a personal best.",
  });
  update("save", {
    summary:
      "Choose a return and review the incoming attack, defender and successful return. A defensive rally label alone does not establish a best save.",
  });
  update("partnership", {
    summary:
      "Keep a private shared moment now. Partnership history needs both verified player links and shared-team membership.",
  });
  update("halves", {
    summary:
      "A first-versus-second-half projection is not supplied for this recording. Reviewed rally order, counts and winners are needed before comparing the halves.",
  });
  update("coverage", {
    availability: format === "singles" ? "not_applicable" : "missing",
    summary:
      format === "singles"
        ? "Pair coverage is not applicable to a singles session."
        : "Position summaries are not coverage-gap judgements. Calibration, simultaneous player visibility and coach review are required.",
  });
  if (format === "singles")
    update("partnership", {
      availability: "not_applicable",
      summary: "A partnership memory needs two players on the same team. This session is singles.",
    });
  update("smash", {
    summary:
      "Immediate smash outcomes are not supplied here. A smash followed by an eventual rally win is a different measure and is not presented as conversion.",
  });
  const tactics = object(data.tactics);
  const chosenTactics = chosenSlot ? object(tactics?.[chosenSlot]) : null;
  if (chosenTactics && Array.isArray(chosenTactics.rally_length)) {
    const rows = chosenTactics.rally_length.flatMap((value) => {
      const bucket = object(value);
      if (!bucket || typeof bucket.label !== "string") return [];
      const count = number(bucket.rallies);
      const won = number(bucket.points_won);
      const rate = number(bucket.win_rate);
      if (count === null || won === null || won > count) return [];
      return [
        {
          label: bucket.label,
          value: won,
          max: count,
          display: `${won} / ${count} won`,
          detail:
            rate !== null && rate <= 1
              ? `${Math.round(rate * 100)}% · ${sideName(chosenSlot ?? "")}`
              : "No known outcomes",
        },
      ];
    });
    if (rows.length)
      update("length", {
        headline: `The exchanges for ${sideName(chosenSlot ?? "")}.`,
        availability: "review",
        summary:
          "Existing server buckets for counted rallies with known winners. Contact completeness and excluded counts are not independently reviewed here.",
        support: "Server-provided counts and rates · unknown/excluded totals not supplied",
        subjectIds: participants
          .filter((person) => person.teamId === chosenTeamId)
          .map((person) => `person:${person.id}`)
          .concat(chosenTeamId ? `team:${chosenTeamId}` : []),
        visual: { kind: "bars", rows },
      });
  } else
    update("length", {
      summary:
        "Select a player with known team membership, or a scoring side, to see the server's rally-length outcomes.",
    });
  return {
    id: session.session_id,
    sport: session.sport,
    title: session.title,
    format,
    example: false,
    revision,
    sourceKey: `${session.source.sha256 ?? session.session_id}:${session.media?.n_frames ?? "unknown"}:${session.media?.fps_num ?? "unknown"}/${session.media?.fps_den ?? "unknown"}`,
    media: session.media,
    participants,
    teams,
    definitions: badmintonHighlights,
    insights,
    rallies,
    scope: `${rallies.length} counted rally intervals supplied · completeness not verified`,
  };
}
