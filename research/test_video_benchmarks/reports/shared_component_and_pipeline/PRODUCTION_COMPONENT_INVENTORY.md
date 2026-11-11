# Actual component inventory

## Evidence boundary

This inventory invokes all three explicit registration functions and `ComponentRegistry.describe()` only. A guard prohibits `create()`: zero factories, providers or models are constructed. It reads source, package metadata, existing local model files and completed run JSON; it opens no media, annotations or sealed labels and launches no inference, GPU job or encode. The exact 22 contracts, model hashes, selected configurations, actual runtime/degradation records and source snapshots are saved separately.

Registration declares compatibility, required evidence, devices, schema, lifecycle and failure policy. It does not prove a provider can load, that a declared backend executed, or that a physical event is accurate. `supported_formats=[singles,doubles,unknown]` means acquisition/abstention compatibility, not reviewed doubles accuracy. The implementation defaults below are distinct from optional-stage enablement and the research-selected rally profile.

## Implemented, executed and unwired responsibilities

| Component | Owner/source | Actual status | Limitation/fallback |
|---|---|---|---|
| Input and source | `engine/sources.py; API routes/sessions.py` | Upload and rights-gated YouTube VOD are wired. | RTSP/SRT/WebRTC/camera enum values are not an implemented true-live ingest path. |
| Probe and clock | `engine/media/probe.py; timeline.py` | Selected-video packet-PTS cadence and exact CFR clock are implemented. | Generic original VFR frame↔CFR proxy correspondence is not persisted as a source-frame map. |
| Proxy/HLS/decode | `engine/media/proxy.py; decode.py` | FFmpeg fMP4 HLS/MP4 and SegmentDecoder execute; current media-origin correction has separate browser controls. | Tiny CFR/VFR/browser tests do not certify all codecs, long streams or live interruption latency. |
| Task orchestration | `engine/bus.py; runtime/runner.py` | LocalBus/RedisBus transport; EngineService and SessionRunner own sequential stages, stop/retry and event storage. | Actual local model-free lifecycle tested; Redis/distributed quota/cancellation and deployment load remain separate. |
| Q&A and providers | `agents/{agent,providers,tools,kb}.py; API routes/agents.py` | Eight read-only tools, six-round loop, grounding repair, sequence fence and deterministic fallback are implemented. | No persistent multi-agent CV research scheduler; remote/local-neural provider accuracy untested; configured session token budget not enforced. |
| Plugin and composition | `engine/sport.py; engine/components.py; badminton/plugin.py` | Explicit sport/provider registries, independent ports, fingerprints and lifecycle contracts. | A declaration or successful construction is not physical component accuracy; provider availability may fail explicitly. |
| View and histogram cut | `perception/scene.py; events/scene.py` | Histogram cut/view/replay heuristics execute in historical and current inference. | Same-camera foreground edits can preserve global histograms. |
| Court and camera | `perception/{court_lines,camera,calibration_state}.py; court.py` | Court lines, homography/camera tracking, recovery and manual calibration paths execute. | Floor projection is not airborne 3D geometry; uncertain calibration and image visibility are distinct. |
| Content continuity | `perception/{scene_change,content}.py` | Optional causal previous-ROI pixel hypothesis; diagnostic or explicit experimental barrier; current scene fresh arm selects it. | Underlying evidence never claims authoritative cut truth; 13 source proposals reviewed by assistant, no independent recall denominator. |
| Shuttle perception | `perception/{tracknet,diagnostics,isolation}.py` | Existing TrackNetV3 eight-frame model, background, masks and opt-in bounded heatmap components execute. | Model support is uncalibrated; masks are image priors; no physical trajectory accuracy from rally F1. |
| Shuttle association | `perception/association.py` | Optional causal co-observed static ambiguity, bounded witnesses/expiry and typed raw-source provenance execute in both new arms. | Raw points remain; no predicted coordinate is substituted; independent association labels missing. |
| Player detector | `perception/players.py; PlayerDetectorPort` | RF-DETR-small executes; detector candidates/ROI rejects and unique fresh matches are distinguishable. | Other locally cached detectors are alternatives, not all executed in this full run; carried boxes are not fresh detections. |
| Tracking and identity | `perception/{players,player_association}.py; participation.py; identity.py; teams.py` | ByteTrack, track episodes, HSV/context continuity and anonymous two/four-player retention execute. | Track, participant, named athlete, team and scoring slot remain separate; no fabricated identity labels. |
| Optional neural ReID | `perception/offline_reid.py; PlayerReIDPort` | OSNet adapter/contract exists and requires pinned FP32 weights. | Weights absent locally and full-run capability explicitly unavailable; no embeddings or ReID accuracy claimed. |
| Pose | `perception/players.py; PosePort` | RTMPose-M executes at declared cadence. New canonical pose_frame_idx records actual valid execution per person. | Legacy absent source stays unknown; a scheduled/non-null pose alone cannot prove freshness; no reviewed keypoint accuracy. |
| Racket | `perception/racket.py; RacketPort` | Weightless OpenCV ellipse/shaft near a wrist executes with actual-frame provenance. | This is geometric evidence, not the optional pretrained RacketVision racket model or a calibrated physical overlap detector. |
| OCR | `perception/scoreboard.py; score_ocr.py` | RapidOCR package-selected detection/classification/recognition execute with actual stage hashes/providers. | rapidocr_v4 is a legacy alias; actual selected run uses PP-OCRv6 det/rec and older cls. OCR is a source-board reading, not a scored point. |
| Contact | `events/{contact,contact_evidence}.py; participant_contact.py` | Default legacy candidate support remains; optional evidence policy separates trajectory, physical impact and actor support. | Lifecycle confirmed is finalization, not physical impact. Automatic probable/ambiguous/insufficient are uncalibrated policy states; external review required for physical confirmed. |
| Stroke | `events/stroke.py; StrokeClassification` | stroke-rules-v0 executes and preserves unknown classes plus parent-impact provenance. | Known heuristic class does not validate contact, named hitter or speed/landing physics; reviewed shot labels absent. |
| Optional BST | `events/bst.py; _bst_network.py` | Implemented verified-weight singles shadow adapter, not selected live classifier or registered default stroke replacement. | Local checkpoint absent; exactly two-player pretrained contract excludes doubles; checkpoint grant not independently verified. |
| Activity and rally | `events/{activity,rally_fsm,rally_evidence,rally_motion}.py` | Independent activity and legacy/evidence/qualified-tracklet rally ports execute; half-open intervals and exactly-once lifecycle retained. | Selected tracklet profile is opt-in development evidence. Curves optional/off; available-window VOD lookahead is not immediate true-live evidence. |
| Outcome and score | `events/rally_outcome.py; rules/{bwf,doubles}.py` | Observed-terminal outcome abstains unknown; BWF scoring applies accepted winners/known format. | No reliable landing or winner is inferred merely from missing shuttle; score rules correctness is not winner-estimation accuracy. |
| Format and doubles | `format_understanding.py; teams.py; analytics/doubles_service.py` | Configured or sustained fresh target-court format contract plus independent four-player/team/service estimates. | Configured names/format do not bind athletes. No reviewed four-player accuracy or prospective held-out validation. |
| Analytics and storage | `analytics/*; TransactionalAnalytics; engine/store/*` | Append-only event fold, journal checkpoint/rollback, match/individual/reviewed/estimated views and heatmaps exist. | Counts and aggregates inherit parent uncertainty; old estimates remain labelled, not silently converted into reviewed statistics. |
| API, wire and browser | `API routes/ws; web/lib/{socket,tracks}; player/overlay` | Wire v2 pf source fields and v1 legacy reads, revision fences, anonymous doubles boxes and estimate labels are implemented. | poseObservedFrame is stored truthfully; historical displayPose age/badge still uses display sample frame, not canonical pf. No UI physical-freshness claim. |
| Exports and evaluation | `API routes/exports.py; engine/evaluation.py; research/evaluation` | JSONL, application CSV/legacy CSV/PDF/summary/clips and separate unchanged rally evaluator exist. | Seven-column benchmark CSV is a separate contract. Application official-rally filters and eight-column legacy CSV must not be confused with benchmark matching. |
| Unwired optional stages | `Profile fields; plugin.capabilities` | shuttle_live, shuttle_second_opinion and inpaint settings are declared and reported unsupported when requested. | RacketVision-balltrack has no runtime adapter; wasb_badminton is not in the model manifest; cached InpaintNet is not integrated. Escalation/racket-window settings do not establish event-triggered specialists. |

## Exact registry snapshot

| Kind | Implementation | Version / output schema | State / failure |
|---|---|---|---|
| activity | temporal-activity-v3 | 1 / badminton-activity-output:v1 | stateful / abstain |
| analytics | match-analytics-v1 | 1 / badminton-analytics-output:v1 | stateful / abstain |
| contact | contact-evidence-v1 | 1 / badminton-contact-output:v3 | stateless port / abstain |
| contact | contact-fusion-v1 | 2 / badminton-contact-output:v3 | stateless port / abstain |
| contact | contact-motion-reliability-v1 | 2 / badminton-contact-output:v3 | stateless port / abstain |
| content_continuity | foreground-content-continuity-v1 | 1 / foreground-scene-hypothesis:v2 | stateful / abstain |
| format | sustained-court-v1 | 1 / format-decision:v1 | stateful / unknown |
| identity | participant-identity-v1 | 1 / badminton-identity-output:v1 | stateless port / abstain |
| ocr | rapidocr-v1 | 3 / badminton-ocr-output:v1 | stateful / unavailable |
| outcome | observed-terminal-v1 | 1 / badminton-outcome-output:v1 | stateless port / abstain |
| player_detector | person-onnx-v1 | 1 / badminton-player_detector-output:v1 | stateless port / unavailable |
| player_reid | osnet-appearance-v1 | 1 / badminton-player_reid-output:v1 | stateless port / unavailable |
| pose | rtmpose-v1 | 1 / badminton-pose-output:v1 | stateless port / unavailable |
| racket | racket-geometry-v1 | 1 / badminton-racket-output:v1 | stateless port / unavailable |
| rally | rally-evidence-tracklets-v1 | 1 / badminton-rally-output:v1 | stateful / abstain |
| rally | rally-evidence-v2 | 2 / badminton-rally-output:v1 | stateful / abstain |
| rally | rally-fsm-v1 | 2 / badminton-rally-output:v1 | stateful / abstain |
| scoring | bwf-rally-point-v1 | 1 / badminton-scoring-output:v1 | stateless port / abstain |
| shuttle | tracknet-v3 | 1 / badminton-shuttle-output:v1 | stateful / unavailable |
| shuttle_association | coobserved-static-hypotheses-v1 | 1 / badminton-shuttle-association:v2 | stateful / abstain |
| stroke | stroke-rules-v0 | 1 / badminton-stroke-output:v1 | stateless port / abstain |
| tracking | court-player-episodes-v1 | 1 / badminton-tracking-output:v1 | stateful / unavailable |

The domain implementation defaults are participant-identity-v1, contact-fusion-v1, stroke-rules-v0, temporal-activity-v3, rally-fsm-v1, observed-terminal-v1, bwf-rally-point-v1 and match-analytics-v1. The selected development runs explicitly choose rally-evidence-tracklets-v1; they do not promote it to the application default. Current contact contracts carry v3 output evidence while the historical run used older metadata: identical implementation IDs do not imply identical source/schema executions.

## Models and dependency availability

License strings below are preserved local registry declarations, not independent legal clearance. First-fetch pins establish subsequent integrity, not publisher authenticity, safe deserialization or rights to training/video data. Builtins have no weights; a package alias is not a pinned checkpoint. Full digests, actual local-file hashes, URLs, package versions and recorded runtime OCR stage hashes are in the JSON artifact.

| Model | Local state | Pin/file SHA-256 | Recorded license scope |
|---|---|---|---|
| osnet_ain_x0_25 | file absent | `ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347` | MIT (Torchreid/LibreYOLO weights and code); research-data provenance documented in model card |
| tracknetv3 | file verified | `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` | MIT (qaz812345/TrackNetV3 code + checkpoints); HF mirror of the official Google Drive release |
| inpaintnet | file verified | `5749b66b8002f3ad9e0af841604004706fc796df30599e6bf01952696009688c` | MIT (qaz812345/TrackNetV3) |
| racketvision_balltrack | file absent | `none` | MIT (RacketVision, AAAI 2026); YouTube-sourced training data — check content rights |
| rfdetr_nano | file verified | `aceebff282d046fae831217136c4c0ce91fb28a6b834dfd48f3a3f46fddc1d9e` | Apache-2.0 (RF-DETR N/S/M/L); ONNX export mirror |
| rfdetr_small | file verified | `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` | Apache-2.0 (RF-DETR); ONNX export mirror |
| rfdetr_medium | file verified | `7fc5834e2fc7205e399a77d29dd0e89b694b075eeb496d5c8464d25137cad788` | Apache-2.0 (RF-DETR); ONNX export mirror |
| yolox_m_humanart | file verified | `3dea6513388889f0fff4b77bf7a26013600321b9eb9ceb0e9a400a82572f5f23` | Apache-2.0 (MMPose / YOLOX) |
| rtmpose_m_body7 | file verified | `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741` | Apache-2.0 (MMPose RTMPose) |
| rtmpose_x_halpe26 | file verified | `1174dd5ccf780501835017eb7376a93fc202238457549a8af8f6aa6d44ae548a` | Apache-2.0 (MMPose RTMPose) |
| racket_geometry_v1 | builtin | `none` | project (OpenCV runtime) |
| racketvision_racketpose | file absent | `none` | MIT (RacketVision); mmpose checkpoint — exported to ONNX in the research container |
| bst_cg_ap_shuttleset | file absent | `997f43e52b20cb47517132c71d3e147d7d717a2d9651cfbe7651a5003bd66809` | MIT source; separate checkpoint grant not independently verified (Va6lue/BST-Badminton-Stroke-type-Transformer) |
| rapidocr_v4 | package 3.10.0 | `none` | Apache-2.0 (RapidOCR / PP-OCR models) |
| contact_fusion_v2 | builtin | `none` | project |
| contact_fusion_v0 | builtin | `none` | project |

The RTMPose-X name contains `halpe26`, but its manifest explicitly identifies a body7 384×288 export with heel/toe work still deferred. It must not be advertised as demonstrated 26-keypoint inference. Optional RacketVision/BST/ReID absence is distinct from missing adapters; cached InpaintNet has weights but is still unwired. `wasb_badminton` is referenced by profiles but absent from the manifest. TensorRT appearing in a contract or ORT advertised-provider list is not a verified TensorRT engine.

## Actual execution evidence and throughput

| Completed run | Source | Offline seconds / FPS | Degradation |
|---|---|---|---|
| next_20261105_fresh_air_tracklet_v1 | `33d3a5b1bcfd` | 1516.497 / 11.38677 | player_identity: osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`; player_reid: baseline player_reid provider is unavailable |
| prod_20261105_fresh_association_v1 | `85993259a3a2` | 1649.780 / 10.46685 | player_identity: osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`; player_reid: baseline player_reid provider is unavailable |
| prod_20261105_fresh_association_scene_v1 | `85993259a3a2` | 1794.365 / 9.62346 | player_identity: osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run `bai models fetch osnet_ain_x0_25`; player_reid: baseline player_reid provider is unavailable |

The two new full-pipeline runs completed while this inventory was prepared; their exact own-cache semantic audits and boundary investigations are still pending here. Their throughput is measured during concurrent runs on separate leased GTX1080Ti cards and shared CPU resources. The ~10 FPS quality-mode rates are below the 30 FPS source, so neither this measurement nor buffered VOD playback is a real-time claim. Stage times overlap/nest and must not be summed as independent critical-path fractions.

Historical actual runtime records show TrackNet Torch CUDA FP16 and OpenCV CPU racket geometry, with ONNX CUDA+CPU provider registration for detector, pose and OCR. The separate executed-node probe confirms 758 RF-DETR CUDA nodes and RTMPose 185 CUDA plus two CPU shape nodes for its fixed inputs. It does not profile OCR or every full-video invocation. ONNX image tensors there are FP32 despite YAML precision=fp16. No TensorRT execution, TF32 arithmetic, RTX4000Ada throughput or optional-model inference is inferred from configuration strings.

RapidOCR's legacy alias `rapidocr_v4` resolved in the historical run to package3.10.0 with PP-OCRv6 det/rec and a mobile v2 classification graph. Actual weight hashes and all stage providers are retained in the runtime JSON. Missing OSNet is explicit degradation; neither constant embeddings nor names are substituted. Locally present alternate detector/pose files establish integrity/availability only; this inventory does not load them.

## Explicitly unresolved system contracts

True-live ingestion remains unwired even though SourceKind and profile fields exist. VFR is detected from packet PTS and converted to canonical CFR, but the generic original-source frame↔proxy correspondence map is absent. A corrected/browser-tested presentation origin is not a full VFR provenance map or proof of RTSP/SRT/WebRTC causality. The current source-clock and browser reports own their exact tested scope.

Frontend wire v2 preserves canonical `poseObservedFrame`; absent legacy pf remains null. Existing displayPose/overlay rendering still derives display hold age from stored sample frames and does not consume pf as a physical freshness badge. This inventory therefore claims provenance transport, not UI physical freshness. Existing machine/reviewed labels distinguish estimates from human events; they do not verify contacts, strokes or identities.

The Q&A agent can fall back deterministically when its provider is unavailable. It never schedules perception or writes reviewed sporting truth. Its configured token budget has no durable consumption/reservation enforcement. Local scripted-provider and service lifecycle tests establish software behavior, not remote model accuracy, distributed durability or deployment reliability.

Independent source-bound labels for physical impacts, first/last sporting observations, player identities, shot classes, landmarks and match-disjoint four-player doubles remain missing. The dataset manifest has zero eligible prospective held-out recordings. No component-performance claim is manufactured from complete software tests or Test1 rally F1. Experimental profiles remain unsuitable for production promotion.

Artifact: `artifacts/benchmarking/experiments/prod_20261105_component_inventory_v1/component_inventory.json`; exact registration/source provenance: `source_sha256.json` and `source/`.

## Final application contract additions

The recorded22 sport contracts/27 responsibility rows/16 model entries above are the source-frozen inventory snapshot. Subsequent application commit `f85b1df` adds independently testable Q&A accounting/admission in `agents/{accounting,budget}.py`, explicit physical-event/source-contact projection in tools, shared public failure projection for HTTP/WS, a fixed application CSV header and truthful media/coverage/export states. The calibration Save request now carries click-time variables. These changes add no neural weights, sport event thresholds or default profile promotion.

The final main/research/frontend counts are2,280/458/226, with typecheck/build and actual browser workflow passes. Runtime/provider, source/annotation/model rights, original-proxy mapping, true-live, independent four-person/physical accuracy and remote/distributed-service limits remain as recorded in the final readiness matrix. Existing raw Test7 neural event IDs/counts and21 official application export boundaries were also verified through an isolated actual browser/API replay; that evidence uses the prior v4 build, while final calibration-fixed v5 has its own full browser fixture proof.
