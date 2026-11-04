# Executed event flow and score contracts — 3 November 2026

This describes the implementation at `cc736886` plus the uncommitted audit
candidate, not a proposed event-sourcing architecture. The
[component ledger](full-pipeline-phase-2-ledger.md),
[score investigation](event-score-integrity-20261103.md) and
[executed validation](full-pipeline-phase-2-validation.md) supply the corresponding
defects, detailed score diagram and test evidence.

## Ownership and identity

| Domain | Owner / durable representation | Identity, time and invariants |
|---|---|---|
| Original media | `engine/sources`, `SessionRepository`; content-addressed source file and catalogue Source | SHA256 of original bytes; source URI is private and public API redacts it. Source metadata/rotation/stream index do not constitute a per-frame source-PTS map. |
| Analysis media | `media/probe.py`, `proxy.py`, `timeline.py`, `decode.py` | One selected non-artwork stream → CFR proxy/HLS; rational FPS; canonical integer frame and integer-microsecond PTS. Inclusive event windows; clip end is converted to end+1. Proxy frames can duplicate source observations. |
| Analysis lifecycle | `runtime/runner.py:EngineService` and `SessionRepository` | Session ULID; `analysis_revision` increases and `analysis_generation` changes on reset. Sequence numbers restart only within the replacement event log. Reanalysis backs up prior events/tracks/exports/metadata first. |
| Observations | Sport perception adapters / `ChunkPerception`; Arrow track rows and diagnostic cache | Raw image pixels, camera reference and observation provenance; reconstructed vs measured flags; transient track IDs and participant episode IDs. Not named people, authoritative winners or calibrated probabilities. |
| Rally/contact/shot/outcome | `BadmintonMatchEngine`, FSM/contact/stroke/outcome/reconciler modules | Strict sequential chunks; segment/camera/calibration gates; provisional contacts/hitter hypotheses and heuristic stroke scores. An ended rally does not imply a known winner. |
| Team/person identity | Session roster, identity-review ledger, separate automatic hypotheses | P1/P2 are scoring slots; doubles T1/T2/team IDs and four roster participant IDs are distinct. Track continuity does not prove human identity. Review is explicit and revision-bound. |
| Point and score | `rules/bwf.py`, engine `_finalize_rally/_point_events/_refold`; accepted effective events | One known eligible P1/P2 winner; point includes before/after rule state and parent rally. State snapshots and in-memory MatchState are derived. There is no independent mutable score field in the catalogue or frontend. |
| Presentation | `SessionSocket`, `EventLog`, `useSession`, `stateAt`, `ScoreBug` | Active session + generation/revision + durable seq + presented frame. Accepted point/seed history owns score; separately labelled corroborated broadcast readings are source observations. |

## Shared event envelope and publication contract

`engine/src/bai_engine/schema/events.py:Event` is schema version1. It carries an
immutable event ULID, owning session ID, open sport `type`, inclusive nonnegative
`frame_start/end`, canonical `pts_us`, actors, payload, confidence/band, lifecycle
status, evidence, provenance, optional `supersedes`/`parent_id`, and store-assigned
sequence. A corrected/retracted event requires `supersedes`; the store rejects
unknown superseded IDs and wrong-session appends. Payloads are currently open
dictionaries, not a discriminated versioned sport union.

There is no explicit processing-time field on Event. ULID generation time and
structured logs are incidental processing clues; neither substitutes for source
PTS or a causal trace. Evidence can reference track windows, pose, court, OCR,
component scores, another event, dataset or human input. Provenance records
model/version plus optional parameter hash, worker and profile. Confidence bands
are heuristic display labels; lifecycle `confirmed` is not a universal accuracy
or human-review assertion.

The following rules apply to **every durable event family** below:

- `EventStore.append_many` allocates sequence in a SQLite write transaction.
  Retrying an identical ID/body returns its original sequence. Reusing that ID
  with different content fails explicitly. IDs alone do not deduplicate two
  independently generated semantic decisions; the sport engine additionally
  serializes/deduplicates known rally intervals and repeated review commands.
- Effective reads fold supersession/retraction globally; raw `since(seq)` retains
  audit history. Same-frame snapshots select their latest revision for projection.
  Related queries use a SQLite read snapshot and repository generation guard.
- Score mutations enclose rally, point, transitions, retractions and snapshots in
  one transaction and restore in-memory scoring bookkeeping on failure. Events
  are notified only after commit. Notification failure is logged and durable
  replay remains possible; it does not undo an already committed decision.
- Replay order is durable sequence, not frame order. Corrections may refer to
  earlier video frames. Reanalysis replaces the generation after backup; it does
  not append another match's points to the old log. General multiple temporal
  writers and cross-process reset fencing are not implemented.

## Actual durable event families

Producer abbreviations: **Engine** =
`sports/badminton/src/bai_badminton/engine.py`; **Review** =
`identity_review.py`; **API Review** =
`apps/api/src/bai_api/routes/identity_reviews.py`.
All consumers also have access to raw/effective event exports and diagnostic
evidence; entries below identify the material domain consumers.

| Event type | Producer / precondition and principal payload | Authority / consumers / replay behavior |
|---|---|---|
| `calibration` | Engine `set_calibration`, via plugin automatic/manual calibration; H/reference/frame size, court/net parameters and provenance | Calibration evidence, not 3D shuttle truth. Plugin restore, camera/geometry gates, overlays and review. Replacement calibration must not reinterpret already buffered old evidence. |
| `broadcast_score` | Engine `_append`, corroborated distinct-frame ScoreReading rows; names/points, optional row mapping, source/confirmation | Source OCR observation; may supply labelled display/seed evidence but cannot by itself award arbitrary points. ScoreBug and reconciler consume it. Unknown mapping remains unknown. |
| `scene` | Engine `_append`, perception scene ranges; view/camera/analysed/court quality | Describes classified view eligibility. Consumers: timeline and temporal geometry gates. Current excluded-view/replay semantics do not recognize same-camera replay content. |
| `activity_interval` | Engine activity classifier; state/basis/evidence coverage/match intent over canonical interval | Activity evidence consumed by match-phase/review UI. Motion/activity is not an official scored rally. |
| `participant_observation` | Engine participant tracker event; observation kind, participant episode/track/side/continuity fields | Provisional visual episode evidence; review, estimated individual analytics and diagnostics. Does not assert roster identity. |
| `identity_ambiguity` | Engine identity/track gate; conflicting/missing identity or multiple tracks, reason/epoch | Provisional ambiguity marker; gates attribution and informs review. Must not be converted into an arbitrary person. |
| `doubles_team_hypothesis` | Engine `DoublesTeamEstimator`; provisional team continuity hypothesis/version | Estimated team evidence; separate from reviewed roster/score slots. Never a substitute for explicit person identity/service setup. |
| `shuttle_turn` | Engine candidate with insufficient player proximity; raw shuttle point/support/reason, contact_eligible false | Diagnostic turn, not a contact/shot. Evidence UI may display it; it cannot award a point. |
| `rally_start` | Engine `_handle_fsm`; onset and candidate rally number | Provisional FSM onset; links eventual rally. An unclosed/motion-only interval need not produce a point. |
| `contact` | Engine `_on_contact`; bounded observed motion, player/pose/racket cues, possible actor, component scores and participant hypothesis | Provisional contact estimate; payload explicitly distinguishes estimated contact from confirmed racket impact. Stroke/rally construction consumes it; human verification is separate. |
| `stroke` | Engine delayed stroke finalization; parent contact, class/distribution, image-flight evidence and possible hitter | Rule-based heuristic, potentially unknown; not live learned BST inference. Rallies, shot analytics, highlights and person review consume it. Hitter review does not verify stroke class. |
| `rally_end` | Engine `_finalize_rally`; interval/end reason, shot references, phase/official status, outcome/winner or unresolved reason, score availability | Closed rally evidence. Lifecycle confirmation can coexist with unknown winner. Restore/analytics require an accepted point child before treating it as scored. Cut/EOF alone does not prove winner. |
| `match_phase` | Engine phase updates/opening seed; or reviewed match_start/interval marker | Algorithmic phase evidence or explicit human input; opening base_state requires supported source scoreboard evidence. Phase changes can require downstream refold. Consumed by restore, rules, analytics and UI. |
| `point` | Engine `_point_events`, only after legal `apply_rally`; winner, rally_no, state_before/state_after, parent rally, source | Accepted confirmed/corrected/human-reviewed point in effective history owns score. Unknown/provisional/retracted/invalid-side candidates do not count. Restore, API, analytics, service and ScoreBug use the same authority. |
| `interval` | Engine from `rules/bwf.py:Transition`; parent accepted point and interval payload | Deterministic rule projection; not evidence that a real-world umpire observed an interval. Regenerated/retracted on score correction. |
| `game_end` | Engine rule transition; parent point, completed game state | Derived game boundary; score/game UI and analytics. Refold follows corrected point history. |
| `side_switch` | Engine rule transition; parent point and ends | Derived ends change; coordinate-side attribution and presentation use match state. Not automatic four-person identity reassignment. |
| `match_end` | Engine rule transition; parent point and match winner | Terminal rule state; no further ordinary point accepted. Does not model all retirements/forfeits/lets/faults. |
| `highlight` | Engine after official rally analytics; ranked interval/player/reasons/evidence | Heuristic recommendation, not ground truth/probability. Highlight API can derive current ranking from corrected analytics; evidence remains inspectable. |
| `identity_review` | Review ledger through API, completed current generation, valid episode/roster person and finite interval | Human-verified association with explicit references; supersede/revoke rather than mutate. Reviewed individual/pair analytics consume it. Generic verify cannot manufacture identity review. |
| `stroke_participant_review` | Review ledger through API, valid stroke and roster participant/current revision | Human-verified hitter association only; individual totals and evidence UI. Correction/retraction preserves history. |
| `doubles_service_setup` | API Review, explicit team/server/receiver/frame/current revision and reviewed score-prefix signature | Human-verified seed for separate named doubles service fold. Changed score prefix can invalidate setup; absent/ambiguous setup stays unavailable. |

Corrections retain the original event type and append new status/supersession
records. They are not a parallel mutable table. Dedicated winner/official/phase
commands refold score. Generic `verify_event` is prohibited for scoring and
identity-review event families; otherwise it may review a contact/stroke without
changing unrelated rule state.

## Transport and API contracts

| Boundary | Actual delivery / response | Ordering, error and recovery |
|---|---|---|
| API → LocalBus / RedisBus → EngineService | Command maps, including start/stop/reanalyse/playhead/seek/calibration/corrections | Local queue is volatile. Redis list is destructive BLPOP without processing ack; pub/sub is a hint. Fractional timeout must remain fractional. External mode requires Redis; neither transport is an exactly-once command system. |
| Generic control/correction HTTP | Most return202 queued; no arbitrary public score-counter mutation | Typed/semantic admission failures return4xx. Worker-side correction failure may only log without reply_to; durable acknowledgement/correlation remains missing.202 does not mean applied. |
| Identity/service review HTTP | Returns persisted review event after transactional validation/commit | Requires revision; stale/invalid evidence rejected. Notifications follow commit; roster IDs and review IDs remain auditable. |
| Durable events/state HTTP | Effective events or raw since_seq delta; state at frame/latest and score timeline | Event seq is independent of frame index. Missing state may be null. Snapshot reads prevent mixed corrections; detected generation crossing refuses rather than closing an active store. General cross-process reset atomicity remains unsupported. |
| WebSocket initial/reconnect | `hello`, `events`, `analysis_reset` plus generation/revision/seq | Subscribe before paged durable replay. Cursor rollback/new generation resets client. Bus loss does not erase committed events; reconnect/seek replays. Binary msgpack is the normal wire representation. |
| WebSocket live/control | `tracks`, `status`, `ingest`, `state`, `state_at`, `reply`; client playhead/seek/track requests | Status/tracks are disposable hints; store rejects stale session/revision. State packet must not override newer accepted effective event history. Partial network chaos and real Redis fan-out are not established by local integration tests. |
| Analytics/product/export projections | Derived totals, tactics, heatmaps, availability and lineage | One per-match event snapshot for combined reads; same-generation corrections invalidate client evidence queries. Unknown score/measurement is null/unavailable rather than invented zero. Clip cache binds actual proxy identity, FPS/range and encoding contract. |
| Agent Q&A | Evidence tools → answer/citations/provider/grounded/issues | Numeric/citation validation is narrower than semantic truth. Deterministic fallback is supported. Provider services and raw-handle lifetime across asynchronous reanalysis remain unverified. |

Structured logs (`session`, event/command type, frame/sequence where recorded),
durable parent/supersession/evidence IDs and exported history provide existing
traceability. They are not a full distributed trace or a durable command receipt.

## Score acceptance and failure evidence

`test_score_event_integrity.py` and `test_event_transactions.py` cover atomic
decision/state/history, injected failures/rollback, repeated review, duplicate ID,
concurrency and retry. `test_score_ocr_delay.py` reproduces the initially unchanged
broadcast reading that hid a later legal score change. `test_score_read_snapshot.py`,
`test_score_synchronization.py` and `test_product_projection_integrity.py` exercise
API/reload/correction/projection boundaries. Frontend derivation/store/ScoreBug
tests reject stale/provisional/retracted evidence. The browser
`e2e/score-integrity.spec.ts` uses controlled observations with the real API,
SQLite, worker, WebSocket and rendered score to verify accepted decisions,
correction, refresh/reconnect and frame navigation. Backend app/repository
recreation is tested separately; synthetic point observations do not prove
perception/outcome accuracy on real footage.

Singles scoring slots, doubles team scoring slots, reviewed four-person attribution
and named service setup have separate tests. A roster/name alone does not establish
visual identity. The exact executed test commands/counts, missing external services,
model-export dependencies and independent labels are in the validation record.
