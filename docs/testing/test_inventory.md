# Comprehensive Test Inventory & Verification Traceability

**Platform:** Real-Time Badminton Analytics Platform (`badminton-ai`)  
**Hardware Evaluated:** NVIDIA GeForce RTX 4080 SUPER (16 GB VRAM), Intel Core i7-14700 (28 threads), 32 GB RAM, Ubuntu Linux  
**Evaluation Date:** October 2026  
**Test Suite Coverage:** 115 pytest backend tests + 23 vitest frontend tests + 7 agentic Q&A scenarios + 5 failure injection tests + 1 full 8-minute match ground-truth evaluation.

---

## 1. Test Suite Categories & Inventory

| Test ID | Category | Subsystem / Capability | Fixture / Input Source | Expected Behavior | Measured Result / Status | Severity on Failure |
|---|---|---|---|---|---|---|
| **ING-01** | Ingestion | Local MP4 File Upload | `sample_rally1.mp4` (16s, 480 frames, 30fps) | SHA-256 hashed, content-addressed storage, session created | **PASS** (Session created, media probed) | P1 |
| **ING-02** | Ingestion | YouTube Video Ingest | `https://youtu.be/oFktPRzCxMo` (8m 4s, 12099 frames) | Download via `yt-dlp`, transcode to 720p HLS proxy | **PASS** (Downloaded & transcoded in 22s) | P1 |
| **ING-03** | Ingestion | SSRF & Domain Validation | `https://malicious-site.com/video.mp4` | Reject non-YouTube domain with HTTP 422 | **PASS** (422 Unprocessable Content) | P0 |
| **ING-04** | Ingestion | Unprocessed Hash Regression | YouTube session initialization | Pre-download `sha256=None` must not crash `media_paths` | **PASS** (Bug resolved; verified end-to-end) | P0 |
| **DEC-01** | Decoding | HLS fMP4 Segment Decode | 720p HLS segments (50 fr/seg) | PyAV decodes in-memory segments to BGR uint8 | **PASS** (220.24 FPS decode throughput) | P1 |
| **DEC-02** | Decoding | Random Keyframe Extraction | Segment IDR frames | Rapid keyframe lookup for background seeding & calibration | **PASS** (sub-15ms per keyframe) | P2 |
| **SHU-01** | Perception | Shuttle Detection (TrackNetV3) | 8-frame sliding windows, 512×288 | TrackNetV3 FP16 Torch-CUDA inference & heatmap argmax | **PASS** (351.97 FPS, 22.73 ms / 8-fr window) | P1 |
| **SHU-02** | Perception | Shuttle Postprocessing | Noisy TrackNet coordinates | Spike removal, parabolic gap filling, confidence estimation | **PASS** (Unit test green; tracks stored in Parquet) | P2 |
| **SHU-03** | Perception | Shuttle Second Opinion | Low-confidence recovery | `wasb_badminton` fallback | **BLOCKED / PLACEHOLDER** (No weights in manifest) | P3 |
| **DET-01** | Perception | Person Detection (RF-DETR) | 512×512 BGR frames | ONNX Runtime CUDA FP16 person bounding boxes & scores | **PASS** (122.39 FPS, 8.17 ms / frame) | P1 |
| **DET-02** | Perception | Multi-Rate Scheduling | In-play vs Idle state | Stride 2 in-play, Stride 6 idle | **PASS** (Pipeline throughput: 59.6 FPS in-play vs 139.6 FPS idle) | P1 |
| **TRK-01** | Perception | Player Tracking & Identity | Consecutive player detections | ByteTrack persistence, near/far court side assignment | **PASS** (Identity stable across rallies) | P1 |
| **POS-01** | Perception | Pose Estimation (RTMPose-M) | 192×256 player crops (2 players) | ONNX Runtime CUDA FP16 17 COCO keypoints | **PASS** (254.96 FPS, 3.92 ms for 2 players) | P1 |
| **CRT-01** | Court | Auto-Court Proposal | Broadcast keyframes | Green-mat contour detection and 4-corner proposal | **PASS** (Auto score 0.9–1.0 on broadcast view) | P2 |
| **CRT-02** | Court | Homography Calibration | Proposed 4 court corners | Planar homography fit, RANSAC outlier rejection | **PASS** (Reprojection error 0.00002 px) | P1 |
| **CRT-03** | Court | Court Color Invariance | Non-green courts (blue/red mats) | Detect court regardless of mat color | **FAIL** (Hardcoded green HSV ranges [30,35,35]-[90,255,255]) | P2 |
| **RCK-01** | Perception | Racket Pose Specialist | Contact window player crop | Racket localization around impact | **NOT RUN / UNWIRED** (Candidate in manifest, not in pipeline) | P3 |
| **CNT-01** | Events | Contact Detection Fusion | 4-cue logistic fusion (`contact_fusion_v0`) | Detect hit frame and attribute player | **PASS** (F1=0.941, Mean error=0.88 frames / 29.2 ms) | P1 |
| **STR-01** | Events | Rule Stroke Classifier | Kinematic & pose features | Classify smash, clear, drop, drive, lift, net_shot, serve | **PASS** (Deterministic rule classifier active) | P2 |
| **STR-02** | Events | Transformer Stroke Classifier | `bst_cg_ap_shuttleset` | Fine-grained stroke prediction from bone sequences | **BLOCKED** (Weights require manual GDrive download) | P3 |
| **SMA-01** | Events | Smash Detection | Shuttle speed, trajectory downward angle | P_smash > 0.8 on high-speed downward trajectory | **PASS** (Detected smashes across match) | P2 |
| **SMA-02** | Events | Jump-Smash Classification | Ankle/hip vertical lift + smash | P_jump > 0.7 when ankle lift > 0.1 normalized height | **PASS** (Tested on synthetic and match footage) | P2 |
| **RAL-01** | Events | Rally Segmentation FSM | Shuttle motion + contact serve trigger | Segmentation into rally start, end, and idle states | **PARTIAL** (22/36 GT rallies matched, 5 false rallies detected) | P1 |
| **RAL-02** | Events | Rally Winner Determination | Landing coordinate & net geometry | Determine rally outcome (out, net, winner) and winner | **PARTIAL** (61.5% winner accuracy on broadcast footage) | P1 |
| **BWF-01** | Scoring | Standard Game Progression | Rally winner sequence | Accumulate points to 21, rotate server, change ends | **PASS** (100% formal invariant verification) | P0 |
| **BWF-02** | Scoring | Deuce Rule (20–20) | Tied score at 20 | Require 2-point lead to win | **PASS** (Verified) | P0 |
| **BWF-03** | Scoring | 30-Point Sudden Death Cap | Tied score at 29–29 | First to 30 points wins immediately | **PASS** (Verified: 30–29 ends game) | P0 |
| **OCR-01** | Scoring | Scoreboard OCR Reconciler | `rapidocr_v4` on broadcast bug | Reconcile geometric winner with scoreboard reading | **NOT RUN / UNWIRED** (Code exists, not called in pipeline) | P1 |
| **PHS-01** | Context | Explicit Match Phase Model | Pre-match, warm-up, active, interval | Prevent warm-up activity from starting official rallies | **FAIL / MISSING** (No match phase model; warm-up counts as play) | P0 |
| **STR-03** | Storage | Canonical Event Store | SQLite event log with append/query/fold | Append events, sequence numbers, immutable audit trail | **PASS** (481 contacts, 41 rallies, 225 strokes verified) | P0 |
| **STR-04** | Storage | Parquet Track Store | Chunked Parquet partitions | High-frequency trajectories partitioned by frame chunks | **PASS** (219 player chunks, 242 shuttle chunks verified) | P1 |
| **ANL-01** | Analytics | Match Statistics Aggregation | Event store & track tables | Compute winners, errors, distance, stroke breakdown | **PASS** (P1 334m, P2 strokes, win rates computed) | P1 |
| **ANL-02** | Analytics | Court Heatmaps | Transformed court coordinates | 62×32 grid presence aggregation | **PASS** (P1: 1001 counts, P2: 1022 counts verified) | P2 |
| **ANL-03** | Analytics | Highlight Detection | Rule & statistical scoring | Top-K highlights categorized by momentum, jump smash | **PASS** (Top highlights ranked with reason decomposition) | P2 |
| **AGT-01** | Intelligence | Agent Loop & Tool Calling | User natural language questions | LLM calls read-only tools over event store | **PASS** (Llama 3.1 8B called tools across 7 test queries) | P1 |
| **AGT-02** | Intelligence | Fact Grounding & Citations | Verified event IDs | All factual assertions cite `[[ev:...]]` | **PARTIAL** (Strict digit validator flags numbers in abstentions) | P1 |
| **AGT-03** | Intelligence | Adversarial Query Abstention | Unseen rally #50, Game 3, racket brand | Refuse to hallucinate absent match facts | **PASS** (Model abstains on unrecorded events) | P1 |
| **WSS-01** | Transport | WebSocket Real-Time Feed | Session stream (`/ws/sessions/...`) | Stream tracks, events, state snapshots to frontend | **PASS** (Binary MessagePack + JSON events verified) | P1 |
| **TUN-01** | Deployment | Cloudflare Tunnel Integration | Public URL routing | Reverse-proxy loopback server to public HTTPS | **PASS** (Live at trycloudflare.com) | P2 |
| **ROB-01** | Robustness | Error Handling on Invalid Input | Bad session ID, bad YouTube URL, bad coords | Return standard HTTP 404/422 without crashing | **PASS** (All 5 injection tests passed) | P1 |

---

## 2. Summary Statistics

- **Total Test Cases Inventoried:** 40
- **PASS:** 28 (70.0%)
- **PARTIAL:** 3 (7.5%)
- **FAIL / MISSING ARCHITECTURE:** 2 (5.0%)
- **BLOCKED / PLACEHOLDER:** 3 (7.5%)
- **NOT RUN / UNWIRED:** 4 (10.0%)
