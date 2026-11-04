import type { HighlightDefinition } from "../types";

export const badmintonHighlights: HighlightDefinition[] = [
  {
    id: "rally",
    title: "Rally of the Match",
    group: "moments",
    question: "Which rally deserves another watch?",
    definition:
      "The longest completed rally by contact count, including the serve. Your favourite is a separate personal selection. Ties share the longest-rally distinction; incomplete counts support only a longest observed rally.",
    requires: [
      "Complete rally boundaries",
      "Contact counts and count convention",
      "Player selection for a favourite",
    ],
    pickKind: "favourite",
  },
  {
    id: "smile",
    title: "Made Me Smile",
    group: "moments",
    question: "What would you like to remember?",
    definition:
      "A moment chosen by a player for their own reasons. It can happen during or between rallies and does not need a winner, shot label or performance claim.",
    requires: ["Source clip interval", "Selecting player or explicit unknown", "Private sharing preference"],
    pickKind: "smile",
  },
  {
    id: "comeback",
    title: "Comeback Moment",
    group: "moments",
    question: "Where did the score turn around?",
    definition:
      "Proposed rule: within one game, recover from a deficit of at least five points to the first level score or lead. A recovery is distinct from a game or match win. Missing or contradictory points break the sequence.",
    requires: [
      "Verified score before and after each point",
      "Known point-winning sides",
      "Start of the deficit and recovery sequence",
    ],
  },
  {
    id: "record",
    title: "Keep-Alive Personal Best",
    group: "history",
    question: "Is this your longest rally yet?",
    definition:
      "The longest verified rally the same linked player participated in, compared with prior reviewed sessions under the same contact-count rule and format scope. The first session establishes a baseline. Participation does not establish the number of personal returns.",
    requires: [
      "Verified cross-session player link",
      "Comparable prior rally records",
      "Reviewed participation and contact counts",
    ],
  },
  {
    id: "save",
    title: "Best Save",
    group: "moments",
    question: "Which return kept the rally alive?",
    definition:
      "A player- or coach-selected difficult defensive return. Incoming attack, defender and successful return need their own evidence. The later rally outcome is separate: a good save can happen in a rally you lose.",
    requires: [
      "Incoming attack and return timestamps",
      "Defender and successful-return review",
      "Player or coach selection and difficulty reason",
    ],
    pickKind: "save",
  },
  {
    id: "partnership",
    title: "Partnership Memory",
    group: "history",
    question: "What have you built together?",
    definition:
      "A shared rally or memory associated with two verified partners. Historical claims require stable player links and shared-team membership. Individual contributions require reviewed contacts; matching names alone do not prove identity.",
    requires: [
      "Both partner IDs and shared-team membership",
      "Verified links for historical sessions",
      "Each player's sharing preferences",
    ],
    pickKind: "partnership",
  },
  {
    id: "halves",
    title: "Start vs Finish",
    group: "patterns",
    question: "How did the two halves compare?",
    definition:
      "Compare the first and second halves by chronological counted-rally order. For an odd total, the middle rally belongs to the second half. Fix the split before excluding missing measurements. This describes the session, not fatigue or a cause of improvement.",
    requires: [
      "Complete ordered rally list",
      "Known winners and contact counts",
      "Declared match scope and half-split rule",
    ],
  },
  {
    id: "length",
    title: "Short vs Long Rally Outcomes",
    group: "patterns",
    question: "Which exchanges went your way?",
    definition:
      "Proposed groups: short 1–4, medium 5–8, long 9+ contacts, including the serve. Win rate is points won divided by rallies with known winners in that group. Unknown counts and outcomes remain excluded and visible.",
    requires: [
      "Reviewed contact count per rally",
      "Known point-winning side",
      "Visible bucket boundaries and denominators",
    ],
  },
  {
    id: "coverage",
    title: "Doubles Court Coverage",
    group: "patterns",
    question: "What did the pair's positioning show?",
    definition:
      "Court positions and coach-reviewed coverage intervals in doubles. Side-by-side or same-side positioning alone does not establish a gap or tactical fault. Occlusions, camera cuts and invalid calibration interrupt position evidence.",
    requires: [
      "Valid target-court calibration",
      "Four-player identities and visibility intervals",
      "Coach-reviewed coverage-gap evidence",
    ],
  },
  {
    id: "smash",
    title: "Smash Conversion",
    group: "patterns",
    question: "What happened after the attack?",
    definition:
      "Immediate winning conversion is direct winners plus reviewed forced errors, divided by smashes with resolved immediate outcomes. Continued rallies and own errors stay in the denominator; uncertain attempts are reported separately. Eventual rally wins containing a smash are a different measure.",
    requires: [
      "Reviewed smash label and hitter",
      "Linked immediate outcome per attempt",
      "Direct, forced, continued, own-error and uncertain categories",
    ],
  },
];
