# Production rally boundary path at 301baf08

The benchmark changes no file under `engine/` or `sports/`. This is a trace of
the actual production code inspected before execution, not a replacement detector.

| Stage | Production implementation | Boundary implications |
| --- | --- | --- |
| Inference entry | `engine/src/bai_engine/runtime/runner.py`, `SessionRunner._ensure_media()` then `_analyse()` | Same upload analysis methods used by `SessionRunner.run()`, called directly to avoid its resident command-service wait. A fresh repository isolates the benchmark from application sessions. |
| Source ingest | `media/probe.py`, `media/proxy.py`, `plan_proxy`, `transcode` | Probes the original file, builds ordinary 720p CFR HLS/MP4 proxy; source bytes remain intact. Standard source rates are retained; unsupported rates can normalize, which the benchmark rejects without an established mapping. |
| Frame numbering | `engine/src/bai_engine/decode.py`, `SegmentDecoder` | HLS segment k has absolute indices `k*F .. k*F+len-1`. PyAV decodes BGR frames. `frame_idx` is zero-based on the analysis proxy. |
| Plugin composition | `sports/badminton/src/bai_badminton/plugin.py`, `BadmintonPlugin.create_session`, `BadmintonSession` | Registries select declared perception and domain components; format inference remains automatic when unspecified. No Part2 court/roster/track data is injected. |
| Perception | `perception/pipeline.py`, `BadmintonPerception` | Cut/replay/court/view/calibration filtering, player detection/tracking, pose and shuttle model loading are profile driven. Missing stages degrade explicitly. |
| Shuttle | `perception/tracknet.py`, `TrackNetV3` | Existing pinned checkpoint, 8-frame windows, step 8, threshold 0.5, 512×288 model input, per-shot background. GPU profile requests torch CUDA FP16, batch 4. No substitution or reimplementation. |
| Player/pose/contact cues | `perception/players.py`, `perception/components.py`, `events/contact.py`, participant geometry modules | RF-DETR Small; RTMPose M Body7; geometric racket evidence. Contact fusion uses observed shuttle redirect, impulse, player proximity and swing cues. It is heuristic, not calibrated contact ground truth. |
| Postprocessing | `perception/shuttle_post.py`, `BadmintonMatchEngine._window` and `_advance` | Reject adjacent spikes (300 px backward / 130 px both neighbors); bounded interpolation (25-frame maximum, 120 px/frame implied-speed gate, 5-frame anchors). Scene/coordinate discontinuities split windows. Interpolated shuttle points are excluded from observed motion and contact evidence for the rally FSM. |
| Contact gates | `BadmintonMatchEngine._advance` | Participant/target-court evidence gates contacts, insufficient proximity becomes diagnostic shuttle turns; singles same-player candidates within 0.9 s are suppressed. Accepted candidates call `fsm.on_contact` before that frame's `fsm.step`. These internal dependencies remain enabled. |
| Temporal context | `EngineConfig`, `BadmintonMatchEngine.ingest/flush` | 40-frame future context and 45-frame backward context; end-of-stream flush processes remaining frames and finalizes pending exchanges. Raw perception caches and events remain in the isolated runtime. |
| Rally segmenter | `events/rally_fsm.py`, `components.py` provider `rally-fsm-v1` | Start after 3 consecutive observed moving frames above 3 px/frame, backdated to run start, or at an accepted contact while idle. |
| End and merge | Same FSM | End candidate after 10 invisible frames, or at least 7 of the last 10 observed samples below 3 px/frame. Candidate cannot precede last accepted contact. Fifteen-frame lookahead; visible speed >6 px/frame or a contact can cancel an end. Closed intervals can reopen within 0.75 s; intervals shorter than 2 s are cancelled. |
| Discontinuity | `RallyFSM.on_discontinuity` | Cuts/replays/coordinate-context breaks close the previous exchange before the new frame and clear history; no gap merge crosses a discontinuity. This can fragment an otherwise manually annotated interval. |
| Final events | `BadmintonMatchEngine._handle_fsm`, `_finalize_pending`, rally finalization | Provisional `rally_start` events may be retracted. Final `rally_end.frame_start/frame_end` store the full segment, even for exchanges not accepted as official points. Match-state/outcome processing may delay publication but is not a benchmark filter. |
| Serialization | `engine/src/bai_engine/store/events.py`, `EventStore.query` | SQLite append-only log; current view folds superseding corrections and retractions. Benchmark exports all current `rally_end` segments and preserves raw events separately. |
| CSV adapter | `scripts/benchmarking/evaluate_rallies.py`, `write_predictions` | Pure integer-boundary serialization. Recomputes full-precision timestamps and endpoint-span duration; it never consumes ground truth. Production's rounded inclusive `payload.duration_s` is deliberately not copied into this schema. |

Player movement, classification, outcome, OCR and scoring may execute as part of
the production composition. Their accuracy is not evaluated here, and no event
from those stages is allowed to exclude an exported final rally. In particular,
there is no requirement for a known winner, official point, named player, minimum
shot count, or a prediction count of 36.
