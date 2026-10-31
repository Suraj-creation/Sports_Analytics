import { expect, it } from "vitest";
import { ev } from "@/test/fixtures";
import { EventLog } from "./events";
import { reviewedIdentity } from "./reviewedIdentity";

it("labels an exact reviewed episode and removes the name on revoke, missing evidence or reset", () => {
  const events = new EventLog();
  const birth = ev("participant_observation", 1, {
    event_id: "birth",
    status: "provisional",
    payload: { kind: "PLAYER_ENTERED", participant_id: "participant-abcd-000004", track_id: 4 },
    provenance: { model: "participant_tracker_v1" },
  });
  const review = ev("identity_review", 1, {
    event_id: "review",
    frame_end: 30,
    status: "human_verified",
    actors: { player_id: "person-four", track_id: 4, opponent_id: null },
    provenance: { model: "human" },
    payload: { observation_id: "birth", participant_id: "participant-abcd-000004", tracker_instance: "abcd" },
  });
  birth.provenance = { model: "participant_tracker_v1" };
  review.provenance = { model: "human" };
  events.apply([
    ev("identity_ambiguity", 0, {
      frame_end: 40,
      payload: { reason: "visual_tracker_reset", tracker_instance: "before" },
    }),
    birth,
    review,
  ]);
  const person = { track: 4, observationId: "birth" };
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })?.name).toBe("Dev");
  expect(
    reviewedIdentity(events, { ...person, observationId: "other" }, 10, { "person-four": "Dev" }),
  ).toBeNull();
  expect(reviewedIdentity(events, person, 31, { "person-four": "Dev" })).toBeNull();
  expect(reviewedIdentity(events, person, 10, {})).toBeNull();
  const conflicting = ev("participant_observation", 1, {
    event_id: "conflicting",
    seq: (birth.seq ?? 1) - 1,
    status: "provisional",
    payload: { kind: "PLAYER_ENTERED", track_id: 4, participant_id: "participant-abcd-000099" },
  });
  events.apply([conflicting]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })).toBeNull();
  events.apply([ev("participant_observation", 1, { supersedes: "conflicting", status: "retracted" })]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })?.name).toBe("Dev");
  events.apply([
    ev("identity_ambiguity", 20, {
      event_id: "other-epoch",
      payload: { reason: "coverage_warning", tracker_instance: "different" },
    }),
  ]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })).toBeNull();
  events.apply([ev("identity_ambiguity", 20, { supersedes: "other-epoch", status: "retracted" })]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })?.name).toBe("Dev");
  events.apply([
    ev("identity_ambiguity", 20, { payload: { reason: "visual_tracker_reset", tracker_instance: "new" } }),
  ]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })).toBeNull();
  events.apply([ev("identity_review", 1, { supersedes: "review", status: "retracted" })]);
  expect(reviewedIdentity(events, person, 10, { "person-four": "Dev" })).toBeNull();
});
