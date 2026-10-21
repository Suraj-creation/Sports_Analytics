# Real-Time Badminton Intelligence: Research, Model Discovery and Architecture Validation Report

> **Status:** research and architecture validation phase. **No implementation has been done.** No model has been run on the target GPU yet.
> **Date:** 2026-10-08. **Branch context:** `SportsVideoAnalysis` on `upgrading` (HEAD `4e7895f`), plus `origin/badminton-rally-detection` (unrelated history, 1,031 files).
> **Target hardware:** NVIDIA RTX 4000 Ada, 20 GB. **The development laptop that produced this report has no NVIDIA GPU** (i3-1115G4, 7.8 GB RAM, Intel UHD). Every performance number below is therefore REPORTED or ESTIMATED until the Phase 0 benchmark runs on the real card.
> **Supersedes:** the model choices in `~/.claude-work/plans/read-through-codebase-guide-md-research-quirky-tide.md` (the "earlier plan"). That plan's platform design (timeline, event store, WebSocket, HLS, profiles) is kept. Its perception stack is revised (see §13 and §18).

### Evidence tags (used throughout)
| Tag | Meaning |
|---|---|
| **[V]** VERIFIED | Seen directly in this repository, a Hugging Face repo, file listing or model card, or an official README or licence |
| **[R]** REPORTED | Claimed by a paper, model card or repository; not tested by us |
| **[E]** ESTIMATED | Our engineering estimate, with the assumption stated |
| **[U]** UNKNOWN | Must be benchmarked or investigated |

### How this research was done
- **Hugging Face MCP** was used for about 300 Hub operations: model, dataset, Space and paper search; `ls` and `cat` of repo files, cards and annotation JSON; dataset structure inspection. URIs are cited inline. The Hub rate-limited some calls (HTTP 429); those were retried.
- **Repository:** every Stage-1/Stage-2 file on `upgrading` and every relevant file on `origin/badminton-rally-detection` was read with `git show`.
- **Papers and repos:** these were read through the HF papers index, arXiv and GitHub.
- **Research corpus:** `research/*.md`, `CODEBASE_GUIDE.md` and the limitations document.

---

# PART 1 — Executive conclusion

**Is a useful real-time, video-native badminton intelligence system achievable today on one RTX 4000 Ada? Yes for uploaded and YouTube video (VOD). Mostly yes for live, with a 0.5–1.5 s semantic delay.** The reason is that the frame-critical perception stack (shuttle, two players, two poses) is small. Our estimate is 5–15 ms of GPU time per frame [E], against a 33 ms budget at 30 fps. The genuinely hard parts are **accuracy problems, not compute problems**: contact timing, jump-smash, court automation, and domain shift to non-broadcast cameras.

| Confidence | Capability |
|---|---|
| **HIGH** | Shuttle tracking at ≥30 fps (TrackNetV3, official MIT weights, FP16). Two-player detection and tracking with stable identity in singles. Top-down pose for both players every frame. Synchronised in-browser playback with overlays for VOD, using an analysis "lead buffer". Deterministic BWF score state machine. Rally outcome via the branch rule engine (85.7% reason / 68.9% winner reported on 8 matches [R]). Score cross-checked with scoreboard OCR on broadcasts. |
| **MEDIUM** | Stroke classification by BST with released ShuttleSet weights (macro-F1 0.80 on ShuttleSet [R]). It is expected to degrade on our pipeline's pose and shuttle inputs, so a zero-shot check (Experiment E7) decides whether fine-tuning is needed. Hit/contact detection with a heuristic first (F1 unknown) and then a small trained causal model; published HitNet reached F1 0.946 [R], but it has no public weights. Smash detection (BST class plus shuttle kinematics). Court homography (manual or semi-automatic first). Racket keypoints with RacketVision weights, event-triggered. |
| **RESEARCH REQUIRED** | Jump-smash vs standing smash from a single broadcast camera (no pretrained model; the only labelled source is FineBadminton sub-types, which we have not yet checked). True 3D shuttle speed and contact height. Fully automatic court calibration across arbitrary venues and cameras. Robustness to amateur, phone and side-view footage. Doubles. Live causal shuttle tracking accuracy (TOTNet and RacketVision balltrack are causal but unbenchmarked). |

**The biggest finding of this phase is in the data, not the models.** **FineBadminton-20K** is public on the Hub under **Apache-2.0** [V] (`hf://datasets/iLearn-Lab/Finebadminton-20K`). It contains **70 full-match broadcast videos (720p) with 2,066 rallies and 20,757 hit annotations**. Each hit carries a frame range, player name, top/bottom hitter, hit type and sub-type, forehand/backhand and ball area. Each rally carries server/receiver and the point reason. With this, hit detection, stroke classification, rally segmentation, server tracking and (partly) score can be **evaluated, and if needed fine-tuned, on full matches immediately, without manual labelling**.

**The second biggest finding** is that the current branch spends compute badly. TrackNetV3 runs with `sliding_step=1` at batch 1 in FP32. That is about 8× redundant forward passes (about 228 GFLOP per frame [E]), plus 1,800 random seeks for the background median that need an estimated 5–15 GB of RAM on a 30-minute video. Fixing how inference is executed, not replacing the model, is the first performance win.

---

# PART 2 — Current system analysis (component classification)

| Component | Where | Classification | Evidence |
|---|---|---|---|
| Streamlit app, LangGraph 3-node graph | `src/app.py` | IMPLEMENTED | Works on CSV input. Results are UI side effects; the graph returns nothing [V]. |
| LLM providers (Azure, OpenAI, LM Studio) | `src/core/llm_provider.py` | IMPLEMENTED; **SECURITY DEFECT** | A live Azure key and endpoint are hard-coded as fallbacks at L46-47 and committed locally in `4e7895f` (not pushed) [V]. |
| Q&A | `src/qa.py` | PARTIALLY IMPLEMENTED | Variables and import fixed in `4e7895f`, but answers are still grounded on a 4-line stats stub [V]. |
| Summary | `src/summarization.py` | PARTIALLY IMPLEMENTED | Ungrounded; same stub [V]. |
| Highlights ranking | `src/highlights.py` | IMPLEMENTED, with defects | `getattr` on a dict ignores the config. Substring match on "clear". "Match point" = score ≥ 20. New regression: an AI score ≤ 1.0 is multiplied by 10 (L452) [V]. |
| Timestamps | 5 parsers in `src/` | BROKEN | `MM:SS:00` is read as hours in 3 of the 5 parsers [V]. |
| RAG (FAISS + MiniLM) | `src/build_db.py` | IMPLEMENTED | `index.pkl` is gitignored, and the index is loaded with `allow_dangerous_deserialization` [V]. |
| Clip/narration/PDF/audio | `src/utils/*` | PARTIALLY IMPLEMENTED | Narration replaces the original audio. WAV data is saved as `.mp3`. The mute fallback can never run [V]. |
| Stage-1 V1/V2 notebooks | `codebase/code/*.ipynb` | PLACEHOLDER / BROKEN | Wrong COCO indices (V1). Random-forest shot classifier trained on `np.random` (V2). Vertical-net court model. Left/right player IDs. Cumulative score [V]. |
| `rally_detector_complete.py` | `codebase/outputs/` | EXPERIMENTAL | Roboflow cloud call per frame. **Hard-coded Roboflow key** at L53 [V]. |
| TrackNetV3 (vendored) | branch `TrackNetV3/` | IMPLEMENTED, inefficient, UNVALIDATED on our footage | Step 1, batch 1, FP32. No InpaintNet. `CONF_TH` has no effect (it is tested on an already-binarised map). Weights not committed [V]. |
| Trajectory filter / gap fill | branch `filter_trajectory.py`, `fill_gaps.py` | IMPLEMENTED, non-causal | Needs up to about 90 frames of look-ahead. CLI flags are parsed but not passed through [V]. |
| Player detection | branch `analysis/player_detection.py` | IMPLEMENTED (no tracking) | YOLO11x on every frame, batch 1, FP32, AGPL. Slots are assigned arbitrarily [V]. |
| Pose | — | **ABSENT** on the branch | — |
| Court | branch `auto_court.py`, manual 8-click, `court_dataset/` | PARTIALLY IMPLEMENTED | HSV + Hough heuristic. The keypoint dataset has only 5 unique annotations and leaks validation data. No trained weights [V]. |
| Court presence / cut detection | branch `court_presence.py` | IMPLEMENTED | Green-fraction + homography reprojection test. Decodes every frame [V]. |
| Rally detection | branch `detect_rallies.py` | IMPLEMENTED, heuristic, VALIDATED (weakly) | Speed/visibility FSM, 15-frame look-ahead, 150-frame look-back. Rally counts close to ground truth on 8 matches [R]. |
| Rally outcome | branch `win_predictor/rule_engine.py` (+ CNN/RF fusion) | IMPLEMENTED, VALIDATED (8 matches) | 85.7% reason, 68.9% winner [R, docs/10]. CNN/RF weights missing [V]. |
| Shot classification | branch `extract_features.py` rules; fusion `ball_types` | PLACEHOLDER | Threshold rules, not on the main path. `ball_types` actually holds the win-reason class [V]. |
| Score | branch `rule_engine.track_scores` | PARTIALLY IMPLEMENTED | Resets at 21 (win by 2) or 30. No service, ends, interval or games beyond reset [V]. |
| V-JEPA probe | branch `vjepa_setup/` | RESEARCH-ONLY | 132 rallies, not wired in [V]. |
| Webapp (Flask + React) | branch `webapp/` | IMPLEMENTED | Auth, roles, jobs, review UI. Polling, one worker thread, finished MP4 only [V]. |
| Benchmark / profiling code | anywhere | **ABSENT** | Only tqdm and print timing [V]. |
| Tests | anywhere | **ABSENT** | Branch has evaluation scripts, but their data is missing [V]. |

**Data on hand** [V]:
- `vjepa_setup/sample_rally1.mp4` (8.5 MB, a 16 s clip) is the only video.
- 29 corrected TrackNet test-label CSVs exist, but their videos do not.
- Rally/winner ground-truth CSVs exist for 4 matches (videos absent).
- 400 court-pose images exist, but only 5 distinct labels.
- **There are no project videos in the repository.** E0 (§12) addresses this.

---

# PART 3 — Current bottleneck map (computational)

| # | Stage | Current implementation | CPU/GPU, sync | Bottleneck | Skip/cache/ROI/lower-rate/fuse/TensorRT? | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Decode | `cv2.VideoCapture.read()` on the main thread; `DataLoader(num_workers=0)` [V] | CPU, synchronous | GPU waits for decode; no NVDEC | Use NVDEC (FFmpeg `-hwaccel cuda` / PyAV / torchcodec) and a separate decode thread or process | **Replace:** NVDEC → GPU tensor, decode once per session, fan out to all models |
| 2 | Resize/normalise | PIL resize of all 8 frames for **every** window (8× redundant). float64 arrays of about 32 MB per sample [V] | CPU | Redundant work, float64, pageable H2D copies | Resize each frame once on the GPU; uint8 → fp16 on the GPU; pinned memory | **Replace** with a GPU preprocessing kernel |
| 3 | TrackNet background median | 1,800 random `cap.set` seeks + `np.median` → about 5–15 GB RAM for 30 min, minutes of seeking [V/E]. Repeated per segment in broadcast mode | CPU | RAM explosion, slow seeks | Compute once at ingest from **sequential** sampled frames (`grab`/`retrieve`, which the branch measured as 6.6× faster [R]); one median per camera segment; cache to disk | **Fix:** per-segment median from ~200–300 frames, computed during ingest |
| 4 | TrackNetV3 inference | `sliding_step=1`, batch 1, FP32, no AMP, two full D2H syncs per batch, Python postprocess loop [V] | GPU, synchronous | ~8× redundant forward passes; launch-bound at batch 1 | Step 8 (non-overlap) or step 4; batch windows; FP16 → TensorRT; GPU argmax/peak instead of `findContours` | **Keep the model, change execution** (Experiment E2) |
| 5 | Trajectory filter / gap fill | pandas, `iterrows`, O(N²) worst-case rescan; non-causal (~90 frames) [V] | CPU | Fine offline; look-ahead adds latency | Vectorise; run per rally on the temporal engine | **Port** as a bounded-latency stage (VOD: fine; live: async correction) |
| 6 | Player detection | YOLO11x on every frame, batch 1, FP32, default `imgsz=640`, per-box `.cpu()` [V] | GPU | Oversized model (x variant), AGPL | Small detector on the court ROI; every 2nd frame + tracker; TensorRT | **Replace** with D-FINE-S or RF-DETR-N/S (Apache) + ByteTrack |
| 7 | Player tracking | none [V] | — | Identity unstable | — | **Add** ByteTrack + court-side identity |
| 8 | Pose | none [V] | — | — | — | **Add** RTMPose-m top-down, batch 2, every in-play frame |
| 9 | Court | heuristic on a few frames [V] | CPU, cheap | Accuracy, not compute | Only on camera cuts plus periodic verification | **Keep the cheap heuristic + manual fallback**; train a keypoint model later |
| 10 | Court presence / segmentation | full decode; `extract_segments` re-decodes the whole video **per segment** via the FFmpeg `select` filter; new process and checkpoint reload per segment [V] | CPU | K× full decodes; process churn | One decode pass; a cut index at ingest; frame-index ranges instead of physical cuts | **Replace** physical segment extraction with logical ranges |
| 11 | Rally detection | pandas FSM, 15-frame look-ahead, 150-frame look-back [V] | CPU, cheap | Look-ahead latency only | — | **Port** to an online FSM with bounded look-ahead |
| 12 | Rally outcome | rule engine on the last 3 s; CNN clip seeks [V] | CPU/GPU, cheap | Fine | — | **Port** unchanged; fix fault-side attribution |
| 13 | Stage 2 LLM | 1 paid LLM call per rally, possibly twice; LM Studio timeout 240 s × 2 on the branch [V] | Network | Cost and latency, ungrounded | Async, budgeted, per-rally only when needed | **Move** to async agents over the event store |
| 14 | Serialisation | CSV between subprocesses; JSON `indent=2` dumps [V] | CPU/disk | Process boundaries | In-memory event bus; Parquet for tracks | **Replace** |
| 15 | Transport/UI | polling; only the finished MP4 is playable [V] | — | No live updates | HLS + WebSocket deltas | **Replace** |

**Ranked compute bottlenecks [V/E]:**
1. TrackNet with step 1 and batch 1 (~8× waste).
2. The median computation (RAM and seeks).
3. YOLO11x on every frame in FP32.
4. Repeated full decodes in broadcast mode.
5. CPU-side preprocessing that starves the GPU.

Everything after detection is computationally negligible but **non-causal (90–150 frames of look-ahead or look-back)**. That is harmless for VOD (absorbed by the lead buffer) and must be redesigned for live.

---

# PART 4 — Current accuracy and robustness limitations (validated)

The 75-item limitations document was validated against the code earlier (see the earlier plan, §B). The ones that matter for perception and real time:
1. **Shuttle:** TrackNetV3 is untested on our videos [U]. Long occlusions (>16 frames) are unrecoverable by InpaintNet, which "invents" positions without flagging them ([R], TrackNetV3 issue #22). The median background breaks on camera cuts [E].
2. **Players:** no tracking. Identity is far = A / near = B, fixed per match, so it is wrong after end changes [V].
3. **Pose:** absent on the branch; wrong indices in V1; a meaningless "jump" test in V2 [V].
4. **Contact:** no detector. The branch infers only the *last* hit from a ≥60° direction change [V].
5. **Stroke:** none on the main path [V].
6. **Court:** heuristic; there is effectively no learned model [V].
7. **Score:** no service, ends or interval. 69% of winner errors are the right reason but the wrong fault side [R, docs/10].
8. **Timeline:** frame indices, float seconds and `MM:SS` strings truncated to whole seconds all coexist. The branch evaluation scores against truncated strings, losing up to 1 s [V].
9. **Evaluation:** the 8-match ground truth the docs cite (`vk15b_dataset`) is not in the repo, so no result can currently be reproduced [V].

---

# PART 5 — Research findings (Hugging Face + literature)

## 5.1 Shuttle perception

| Candidate | Source | License | Weights | Input → output | Causal? | Reported accuracy | Reported speed | Our view |
|---|---|---|---|---|---|---|---|---|
| **TrackNetV3** (+InpaintNet) | github.com/qaz812345/TrackNetV3; HF mirrors `TanmaySarda/tracknetv3-weights` (TrackNet_best.pt 136,190,877 B + InpaintNet_best.pt 6,264,451 B) [V], `rahulanantharama/TrackNetV3-badminton` (TrackNet only, same size) [V] | MIT (code + checkpoints per README) [V]; mirror provenance unverified [U] | **Yes** | 8 frames + median bg @288×512 → 8 heatmaps; InpaintNet seq 16 | No (window; InpaintNet bidirectional) | F1 98.56 / Acc 97.51 on Shuttlecock Trajectory test [R] | 25.11 fps end to end, hardware not stated [R] | **Baseline. Keep.** About 11.3M params; 114–116 GMAC per forward [E] |
| **RacketVision balltrack** (multi-scale TrackNetV3) | `hf://models/linfeng302/RacketVision-Models/checkpoints/balltrack_best.pth` (46.6 MB) [V] | MIT tag [V]; trained on YouTube broadcasts (content rights [U]) | **Yes** | bg + target + preceding frames, 1080p-trained | **Yes** (past frames) [R] | Badminton P 0.915 / R 0.865, MDE 1.54 px @1080p [R] | U | **Strong candidate for live** and for broadcast diversity (461 badminton clips) |
| **TOTNet** | github.com/AugustRushG/TOTNet; badminton weights committed (94 MB) [V via GitHub API] | MIT [V] | **Yes** | 5 past frames @288×512 | **Yes** [R] | Badminton acc 0.89 visible / 0.84 occluded; beats WASB on the same split [R] | 28 fps, GPU not stated [R] | **Live candidate**; benchmark speed |
| **WASB-SBDT** | github.com/nttcom/WASB-SBDT MODEL_ZOO (Drive) [V] | MIT [V] | **Yes** (WASB, TrackNetV2, MonoTrack reimpl. for badminton) | 3 frames @288×512, HRNet | No (3-frame window) | Badminton F1 93.1 (step 1), stricter τ=4 px protocol [R] | 34–70 fps on V100 [R] | **Cheap second opinion** (1.5M params) for disagreement checks |
| TrackNetV4 (motion attention) | arXiv 2409.14543; HF paper has no linked models or datasets [V] | Code "coming soon"; data non-commercial [R] | **No** | V2/V3 + frame-difference motion prompt (+2 params) | No | V3 97.5 → 97.9 F1 [R] | ~1% overhead [R] | **Reimplement only as an ablation** (trivial layer) |
| TrackNetV5 (WUT) | arXiv 2512.02789 | U | **No** (only an unrelated soccer run on HF, `bambezius/tracknetv5-*`) [V] | t−1, t, t+1 | 1-frame look-ahead | F1 98.59 [R] | 38 fwd/s on T4 [R] | Research only |
| TrackNetV5 Lite (NYCU) | course PDF | U | **No** | 5 frames | U | F1 98.06 at 135 fps on RTX 5080 [R] | — | Distillation target idea |
| YOLO11s shuttle | `hf://models/Huydinh1205/shuttle_yolo11s` [V] | AGPL [V] | Yes | single frame @1280 | Yes | mAP50 0.709, R 0.631 [V card] | — | **Reject** as primary (single-frame detectors lose 10–30× in localisation [R, RacketVision]) |

## 5.2 Players: detection, tracking and ReID

| Candidate | HF / repo | License | T4 TRT FP16 latency [R] | COCO AP [R] | Verdict |
|---|---|---|---|---|---|
| **D-FINE-S / M** (obj2coco) | `ustc-community/dfine-small-obj2coco`, `dfine-medium-obj2coco` [V] | Apache-2.0 [V] (Obj365 data terms to review) | 3.49 / 5.62 ms | 50.7 / 55.1 | **Fast profile primary** |
| **RF-DETR N/S/M** | `Roboflow/rf-detr-*`, `onnx-community/rfdetr_nano-ONNX` [V] | N/S/M/L Apache-2.0; XL/Atto etc. PML [V] | 2.3 / 3.5 / 4.4 ms | 48.4 / 53.0 / 54.7 | **Equal candidate**; benchmark against D-FINE |
| RT-DETRv2 r18 | `PekingU/rtdetr_v2_r18vd` [V] | Apache-2.0 [V] | 4.59 ms | 47.9 | Backup |
| RTMDet / YOLOX-humanart | rtmlib ONNX `Tau-J/RTMPose` [V] | Apache-2.0 | ~2.5–7 ms on a 1660 Ti | person AP 62.5 (m) | Backup; same toolchain as RTMPose |
| YOLO11/YOLO26 | Ultralytics [V] | **AGPL-3.0** | 1.5–11.8 ms | 39.5–57.5 | **Do not use by default** (licence) |
| DEIMv2 | `Intellindust/DEIMv2_*` [V] | **Non-commercial** [V] | — | — | Reject |
| **ByteTrack** | `pip install trackers` (Roboflow, Apache-2.0) / ifzhang MIT [V] | Permissive | negligible | SportsMOT HOTA 73.0 [V README] | **Default tracker** |
| OC-SORT / BoT-SORT / McByte | roboflow trackers [V] | MIT/Apache | negligible | SportsMOT 71.7 / 73.8 / 76.5 [V] | BoT-SORT for camera motion; McByte to test |
| StrongSORT / boxmot | — | GPL-3.0 / AGPL [V] | — | — | Reject (licence) |
| OSNet ReID | `kaiyangzhou/osnet` [V] | MIT code; MSMT17 weights research terms [U] | <1 ms for 2 crops [E] | — | **Not needed per frame**; only re-link after cuts (an HSV shirt histogram usually suffices) |

**Key reasoning [E]:**
- In singles the two players never cross the net. Identity = court side (in court coordinates) + the end-change rules from the BWF state machine + a shirt-colour signature.
- The far player is about 40–75 px tall in a 640-letterboxed 720p frame. Cropping to the court plus a margin raises that to about 53–100 px.
- A small detector is therefore sufficient. The main risk is **recall on airborne, blurred jump-smash frames**, which Experiment E4 measures specifically.

## 5.3 Pose

| Candidate | HF / format | License | Type | Accuracy [R] | Speed [R] | Est. RTX 4000 Ada for 2 crops [E] | Verdict |
|---|---|---|---|---|---|---|---|
| **RTMPose-m** body7 256×192 | `Tau-J/RTMPose` rtmlib ONNX [V] | Apache-2.0 [V] | top-down | COCO 75.8 | 2.29 ms/crop on 1660 Ti TRT FP16 | 1.0–1.8 ms | **Fast profile primary** |
| **RTMPose-l/x 384×288, halpe26** | ONNX zips [V] | Apache-2.0 | top-down | COCO 77.0–77.3; halpe26 adds heels and toes | 3.7–6 ms/crop | 2–6 ms | **Quality profile**; heel/toe points help jump detection |
| ViTPose++ B/L | `usyd-community/vitpose-plus-*` (transformers) [V] | Apache-2.0 | top-down ViT | 77.0 / 78.6 | U | 2–10 ms | Most blur-robust family (PoseBench [R]); TensorRT export effort |
| RTMO s/m/l | rtmlib ONNX [V] | Apache-2.0 | bottom-up | 68.6–74.8 | 9–19 ms (V100) | 9–20 ms | **Reject for singles**: only wins with more than 4 people, and weaker on the small far player. *This corrects the earlier plan.* |
| DWPose / RTMW (133 keypoints) | `yzd-v/DWPose` [V] | Apache-2.0 | whole-body | Hand AP 0.62 (l-384) | — | 3–8 ms | Near player only; far player's hands are about 5 px |
| YOLO26-pose | Ultralytics | AGPL | one-stage | 57.2–71.6 | 1.8–12.2 ms | — | Licence; coarse keypoints on small persons |
| Sapiens2 | `facebook/sapiens2-pose-*` [V] | restricted (no biometrics/surveillance) [V] | ViT @1024 | — | 1.26 TFLOPs/crop | 25–60 ms | Offline teacher only |
| MotionBERT | `walterzhu/MotionBERT` [V] | Apache-2.0 | 2D→3D lifting | BST found 3D *worse* than 2D for strokes [R] | — | — | Not in the real-time path |

**PoseBench [R]:** motion blur is the most damaging corruption, roughly halving AP even for ViTPose (75.8 → 43.3). RTMPose was not tested. This makes **temporal smoothing (One-Euro) and event-triggered high-resolution re-crops** important rather than optional.

## 5.4 Racket

| Candidate | Source | License | Weights | Reported | Verdict |
|---|---|---|---|---|---|
| **RacketVision RacketPose** (RTMDet-M + RTMPose-M, 5 keypoints: top, bottom, handle, left, right) | `hf://models/linfeng302/RacketVision-Models` (`epoch_300.pth` 411 MB detector, `best_PCK_epoch_90.pth` 106 MB pose; mmdet/mmpose) [V]; github.com/OrcustD/RacketVision | MIT [V] (YouTube-sourced content [U]) | **Yes** | Badminton PCK@0.2 88.5, MPJPE 5.0 px; side keypoints weaker (65–80%) [R] | **Use, event-triggered only** (±4–8 frames around contact candidates) |
| RacketDB | `hf://datasets/muhabdulhaq/racketdb` (~130 GB, COCO export) [V] | CC-BY-4.0 [V] | No weights | YOLOv8 mAP50 0.78 [R]; drone back view (domain mismatch) | Extra training data only |
| COCO "tennis racket" class | any COCO detector | — | Yes | mAP50 0.63 on badminton rackets, zero-shot YOLOv5 [R] | Bootstrap labeller only |
| Wrist/forearm vector (pose) | from §5.3 | — | — | — | **Always-on racket proxy**: hitting side, swing timing, ROI for the racket model |

**Conclusion:** racket perception does **not** need to run continuously, and it does **not** need training to start. The order is: pose proxy (always on) → RacketVision model (event-triggered) → fine-tune only if Experiment E10 shows it fails on our footage.

## 5.5 Contact / hit detection

**No pretrained badminton hit detector exists on the Hugging Face Hub [V]** (searched: badminton, shuttle, shuttlecock, tracknet, stroke, racketvision).

| Method | Inputs | Reported | Weights |
|---|---|---|---|
| MonoTrack HitNet (CVPRW'22) | court + pose + 2D shuttle → 2-layer GRU, 12-frame window, ~16K params, classes none/near/far | F1 0.946 [R]; velocity-derivative baseline 53.8% acc [R] | **No** |
| Automated hit-frame detection (arthur900530, MIT) | rally trim + Keypoint-RCNN + Transformer | F1 0.64 @±5 frames, 0.80 @±15 [R] | Yes (heavy, coarse) |
| "Enhancing Badminton Game Analysis" (Sensors 2024) | TrackNet direction change + YOLOv7 swing + 5-case fusion | F1 0.905 on 69 matches [R] | No |
| SwingNet (2306.10293, HF paper) [V] | MobileNetV2 + BiLSTM on optical flow | U | Code claimed |
| E2E-Spot | RGB RegNetY + GRU | strong generic spotter [R] | no badminton checkpoint |

**Conclusion:** contact needs **a small, cheap custom model**. The labels already exist: ShuttleSet `frame_num` (~33k hits [V schema]) and **FineBadminton-20K** hit frames (20,757 hits, Apache-2.0 [V]). Until that model exists, a deterministic fusion heuristic is the baseline. Fusion literature reports ~0.9 F1 [R], which makes it a credible stopgap.

## 5.6 Stroke classification

| Candidate | Weights | Input | Window | Classes | Reported | Real-time fit |
|---|---|---|---|---|---|---|
| **BST-CG-AP** (Va6lue, MIT) [V] | **Yes** (Drive; ShuttleSet/BadmintonDB/TenniSet) [V README] | RTMPose 2D (joints + bones, box-normalised) + **TrackNetV3 *attention fork* (alenzenx)** shuttle + court position via homography [V] | fixed ±0.5 s (`seq_len=30`) or prev-opponent-hit → next-opponent-hit + ε (`seq_len=100`) [V] | 25 merged (12 types × top/bottom + unknown) or 35 raw [V] | Acc 0.832 / macro-F1 0.810 (25 classes) [R]; weakest: smash vs wrist smash, block vs defensive drive [R] | **Yes**, triggered per hit; classifier ≈1 ms [E]; latency = hit + 0.5 s (fixed) or + up to ~1.5 s (adaptive) |
| TemPose-TF | re-implementation inside the BST repo [V] | pose + shuttle | — | — | 0.82 / 0.80 [R] | Similar; no verified weights |
| TemPose-TF-ASF | none [R] | bidirectional stroke context | non-causal | 31 | +~2 points [R] | Offline re-scoring only |
| VideoMAE (HF `yexter/...Badminton_strokes...`) [V] | Yes | RGB 16×224² | 16 frames | 11 | inconsistent card (0.84 vs 0.76), unknown data, CC-BY-NC [V] | **Reject** (untrustworthy, non-commercial) |
| VideoBadminton SlowFast etc. | No [R] | RGB | clip | 18 | 82.8% top-1 [R] | Heavier; no weights |
| Skeleton-only (ST-GCN, SkateFormer) | NTU only | pose | — | — | ~5 points below shuttle-aware models [R] | Baselines |

**Important domain-shift risk [E]:** BST was trained on pose from *MMPose RTMPose* and shuttle tracks from a *different TrackNetV3 fork*. Feeding it our tracker's outputs is a distribution shift, and normalisation must match its scripts exactly. **Experiment E7 measures this on FineBadminton before any training decision.**

## 5.7 Temporal segmentation (rally / serve)

- **No badminton checkpoints exist** for MS-TCN++, ASFormer or OnlineTAS [U].
- DSTA (2605.23355): ShuttleSet mAP@0.5 75%, offline, no weights [R].
- HF `phubinhdang/videomae-base-finetuned-badminton-rally` (rally / not-rally, no metrics) [V] could gate replays and pauses, but it is unvalidated.
- HF `phubinhdang/badminton-video-trimmer` (ActionFormer, 170 MB) [V]: data and accuracy unknown.
- **Conclusion:** rally = first hit → last hit + landing/end evidence (BST's gap rule [V] + the branch FSM). Serve = the first hit of a rally (BST has short/long-serve classes). A learned temporal segmenter is **not justified** until the rule-based approach fails Experiment E8.

## 5.8 Court

- **No pretrained badminton court-keypoint model with metrics exists on HF [V].** Hits are tennis or basketball (`Coddieharsh/tennis-court-keypoints`, `koppolusameer/yolo11n-basketball-court-keypoints` (AGPL), …).
- TennisCourtDetector [R]: 14 keypoints, median error 1.83 px with refinement; licence [U]. Good **architecture template** for retraining.
- arthur900530 `court_kpRCNN.pth` (6 badminton court points, MIT) [R]: usable as a **pseudo-labeller**.
- PnLCalib (GPL-2.0) [V]: the method transfers (keypoints + line refinement); the code licence does not.
- **Broadcast cameras are effectively static within a shot.** So: detect cuts → calibrate once per shot (median of K frames, RANSAC homography, line refinement) → verify every 1–2 s by line reprojection → no valid homography means a replay or close-up. Court cost ≈ 0 per frame [E].

## 5.9 Datasets

| Dataset | URL | Size | Annotations | Res / FPS | Camera | License | Use |
|---|---|---|---|---|---|---|---|
| **FineBadminton-20K** | `hf://datasets/iLearn-Lab/Finebadminton-20K` [V] | **70 full-match videos** (~650–890 MB each [V]), 2,066 rallies, 20,757 hits [V] | Per rally: start/end frame, playerList server/receiver, point reason. Per hit: start/end frame, player, hit type, subtype, top/bottom hitter, ball area, forehand/backhand, comment, quality [V JSON] | 1280×720, `fps: 30.0` in JSON [V] (paper says 25 fps [R]; check per video) | BWF broadcast | **Apache-2.0** [V]; some labels machine-generated and noisy [V: a "serve" whose comment says "clear"] | **Primary evaluation set now**; fine-tuning for hits, strokes, rallies and server; jump-smash sub-type reported in the paper [R] (verify in data) |
| FineBadmintonBenchmark | `hf://datasets/iLearn-Lab/FineBadmintonBenchmark` [V] | built from 20 of the videos above [V] | MLLM QA benchmark | — | — | U | Test VLM/LLM layer; **exclude its 20 videos from training splits** |
| ShuttleSet / ShuttleSet22 | github.com/wywyWang/CoachAI-Projects | 44 matches, 3,685 rallies, 36,492 strokes [R] | per stroke: frame_num, player, server, type, hit/landing xy, area, roundscore, win/lose reason [V schema via BST mirror] | mostly 720p (36/42 videos) [V]; ~25 fps for match 1 [E] | broadcast | code MIT; videos BWF YouTube (self-download, rights [U]) | Hit/stroke fine-tuning; **score/server ground truth** |
| BFMD | `hf://datasets/OpenSportsLab/BFMD` (**gated, manual**) [V] | 19 matches, 20+ h, 1,687 rallies, 16,751 hits; singles + doubles [R] | match segments **incl. replays and Hawk-Eye**, rally events (hit, net hit, landing), shot types, shuttle trajectories, boxes, pose [R] | U | broadcast | U | **Replay/cut detection and landing evaluation**; request access |
| RacketVision | `hf://datasets/linfeng302/RacketVision` [V] | badminton: 461 clips, 114,753 frames [R] | ball xy + visibility; racket 5 keypoints (COCO JSON) [V README] | 1920×1080 | broadcast | MIT tag [V] | Shuttle/racket fine-tuning and evaluation |
| Shuttlecock Trajectory (TrackNetV2) | hackmd TUIK [R] | 26+3 matches, 78,200 frames [R] | Frame, Visibility, X, Y | 720p30 | broadcast + 3 amateur | **not stated** [R] | Shuttle evaluation (TrackNetV3 test split) |
| VideoBadminton | arXiv 2403.12385 [R] | 7,822 trimmed clips, 18 classes | stroke label per clip | 1280×960 @60 fps, fixed club camera | club/practice | CC BY-NC-SA [R] | Non-broadcast domain check only (non-commercial) |
| BadmintonDB | github.com/kwban/badminton-db [R] | 9 matches, one player pair | strokes, points (EAF) | broadcast | U | Low diversity |
| RacketDB | `hf://datasets/muhabdulhaq/racketdb` [V] | 22.7k images | racket boxes | 4K drone | CC-BY-4.0 [V] | Racket detector fine-tuning |
| Other HF "badminton" sets | inspected [V] | — | text/chat, robotics (LeRobot), ControlNet poses | — | — | — | **Not useful**; `howard9199/Badminton` is gated/"under construction" [U] |

---

# PART 6 — PLAN A: pretrained / off-the-shelf real-time system

| Capability | Candidate pretrained models | Best candidate | Why | Input | Frequency (hypothesis) | Expected cost on RTX 4000 Ada [E] | Confidence |
|---|---|---|---|---|---|---|---|
| Shuttle | TrackNetV3, RacketVision balltrack, TOTNet, WASB | **TrackNetV3** (VOD); **RacketVision balltrack or TOTNet** (live), decided by E3 | In-domain, MIT, best reported F1; the other two are causal | 8 frames + per-segment median @288×512 | every frame, computed in 8-frame (VOD) or causal (live) windows | ~0.6–1.3 ms/frame at step 8; ~5–10 ms/frame at step 1 | High (compute), Medium (our-footage accuracy) |
| Shuttle refinement | InpaintNet, WASB, spline/physics | **InpaintNet + branch spline gates**; WASB as a disagreement oracle | Already available; cheap | track windows | on gaps / low confidence only | negligible to ~1 ms amortised | Medium |
| Player detection | D-FINE-S, RF-DETR-N/S, RTMDet, YOLO26 (AGPL) | **D-FINE-S or RF-DETR-S** (E4 decides) | Apache, accurate on medium objects, TensorRT path | court-ROI crop → 640 | every 2nd frame in play; every 5th–10th out of play; forced on cuts/low confidence | ~1–1.5 ms/frame amortised | High |
| Tracking/identity | ByteTrack, OC-SORT, BoT-SORT, McByte | **ByteTrack + court-side identity + HSV signature** | 2 players, never cross the net; no ReID needed | boxes | every frame | <0.2 ms | High |
| Pose | RTMPose-m/l/x, ViTPose++, RTMO, YOLO-pose | **RTMPose-m body7** (fast) / **RTMPose-x halpe26 384** (quality) | Top-down beats bottom-up for 2 persons; heels/toes for jumps | full-resolution crops, batch 2 | every frame in play (impact phase is ~2–3 frames); off when idle | ~1–2 ms (m), 3–6 ms (x) | High (compute), Medium (blur accuracy) |
| Court | heuristic (branch), manual, TennisCourtDetector-style (needs retrain), court_kpRCNN | **Branch heuristic + manual confirmation**, per shot | No pretrained badminton model; camera static per shot | 1 frame per shot + verify | on cuts + every 1–2 s verify | ≈0 | Medium |
| Racket | RacketVision RacketPose, COCO racket class | **RacketVision RTMDet-M + RTMPose-M** | Only badminton broadcast racket keypoints with weights | full-resolution crop near hitter | event-triggered ±4–8 frames | ~5–10 ms per triggered frame (U) | Medium |
| Contact | none pretrained | **Deterministic fusion heuristic** (§9 of Part 13) | No weights exist | shuttle track + wrist kinematics + side alternation (+ racket if triggered) | per frame on the track, cheap | ≈0 | Medium-low until E6 |
| Stroke | BST, TemPose-TF, VideoMAE (reject) | **BST-CG-AP (ShuttleSet weights)** | Best reported, MIT, light, uses exactly our modalities | pose + shuttle + court, ±0.5 s | per contact | ~1 ms per call | Medium (domain shift, E7) |
| Smash | BST smash class | **BST p(smash) × shuttle-kinematics evidence** | Combination beats either alone (BST confuses smash and wrist smash [R]) | BST output + post-contact speed/angle | per contact | ≈0 | Medium |
| Jump smash | none | **Evidence fusion** (ankles/heels vs ground baseline, hip vertical velocity, airborne homography break) | No model or dataset with weights | pose window ±6 frames | per smash | ≈0 | **Low → research** |
| Rally/serve | branch FSM; VideoMAE rally (unvalidated) | **Hit-driven FSM + branch FSM fallback** | Cheap; BST gap rule [V] | events | per event | ≈0 | Medium-high |
| Rally outcome | branch rule engine + CNN (weights missing) | **Branch rule engine** | Best validated component | last 3 s of track + court | per rally end | ≈0 | Medium-high |
| Score | BWF rules + OCR | **Deterministic BWF state machine + scoreboard OCR** (RapidOCR/PaddleOCR, Apache) | Deterministic fact; OCR fixes winner errors on broadcasts | rally winners; score-bug region at 1–2 Hz | per rally / 1–2 Hz | ≈0–2 ms per OCR call | High on broadcast |
| Cut/replay | branch court-presence, court homography validity, VideoMAE rally | **Cut index at ingest (cheap histogram/SAD) + homography validity** | Cheap; replays show no valid main-camera homography | frames | ingest pass | ≈0 | Medium (BFMD can validate) |

**Known weaknesses of Plan A:** contact accuracy unknown; BST domain shift; jump-smash unvalidated; court needs a human on unseen venues; all perception is broadcast-trained.

---

# PART 7 — PLAN B: badminton-specific training (only where Plan A is insufficient)

Decision rule: **pretrained solves it → use it; partially → fine-tune; no → train a small specialist.**

| Capability | Pretrained adequate? | Decision | Trigger |
|---|---|---|---|
| Shuttle | Probably yes for broadcast | **Fine-tune only if E3 shows F1 < 0.90 on our footage** | E3 |
| Players / tracking | Yes | No training | — |
| Pose | Mostly yes | Fine-tune only if wrist/ankle PCK on far-player blur frames is < 0.7 (E5) | E5 |
| **Contact** | **No pretrained model** | **Train a small specialist** (definite) | — |
| Stroke | Partially | **Fine-tune BST** if E7 macro-F1 < 0.70 on FineBadminton | E7 |
| Smash | Via stroke + kinematics | Calibrate thresholds (no model) | E7 |
| Jump smash | No | **Threshold calibration first**; train a small classifier only if fusion AUC < 0.85 | E11 |
| Court keypoints | No | **Train** for automation (VOD can live with manual or semi-automatic first) | Phase 3 |
| Racket | Yes (RacketVision) | Fine-tune only if E10 fails | E10 |
| Rally segmentation | Rule-based | Train only if E8 F1 < 0.9 | E8 |
| ReID | Not needed | — | — |

### T1. Hit/contact detector (definite)
1. **Data:**
   - FineBadminton-20K: split 50/10/10 by match, excluding the 20 FineBadmintonBenchmark videos from test contamination.
   - Plus ShuttleSet (40 matches).
   - Hit frame = each hit's `start_frame` [V]. **Semantics must be verified** by visually inspecting 50 hits: is it contact or swing start?
2. **Cleaning:** drop rallies containing replays; spot-check 2% for machine-label noise.
3. **Inputs:** our own runtime pipeline's outputs (TrackNetV3 track, RTMPose wrists/elbows for both players, court-normalised positions), so train and deploy distributions match.
   - Cost [E]: ~70 matches × ~45 min ≈ 5.7M frames. At an estimated ≥150 fps perception throughput that is ≈10–11 GPU hours on the RTX 4000 Ada, cached as Parquet features.
4. **Model:** causal GRU/TCN over 12–20 frames, with ~16k–200k params (HitNet scale [R]).
5. **Output:** {none, top-player hit, bottom-player hit} per frame.
6. **Loss and augmentation:**
   - Loss: focal loss on Gaussian-smoothed targets (σ = 1 frame).
   - Augmentation: drop shuttle frames (occlusion simulation), jitter keypoints, mirror left/right, time-stretch ±10%.
7. **Metrics:** F1 at ±2 and ±5 frames; hitter accuracy; per-category breakdown (smash, net play, serve).
8. **Targets:** **F1 ≥ 0.90 @±3 frames**. The heuristic baseline must be beaten by ≥10 points.
9. **Export:** ONNX → TensorRT FP16 (tiny). Latency ≈ 0.1 ms [E].
10. **Minimum viable / good / ideal data:**
    - Minimum viable: 20 FineBadminton matches (~6k hits).
    - Good: 70 FineBadminton + 40 ShuttleSet (~50k).
    - Ideal: plus 5–8 matches from our own camera (~2k hits).

### T2. BST stroke fine-tune (conditional on E7)
1. **Data and labels:** map FineBadminton hit types and sub-types onto BST's 12 types (the mapping table must be written; ambiguous classes become "unknown"). Same match split as T1.
2. **Initialisation:** BST-CG-AP ShuttleSet weights.
3. **Inputs:** our pose, our shuttle and our court (fixes the domain shift).
4. **Loss:** cross-entropy with label smoothing; class-balanced sampling.
5. **Metrics:** macro-F1, a confusion matrix (watch smash/drop/clear and block/drive).
6. **Data volume and cost:** 25% of ShuttleSet already gave useful accuracy [R], so ~5k strokes is a reasonable minimum. Training takes minutes [E].
7. **Export:** TorchScript/ONNX.
8. **Target:** macro-F1 ≥ 0.75 on held-out FineBadminton matches.

### T3. Jump-smash calibration → optional classifier
1. **Data:**
   - Check whether FineBadminton sub-types contain "jump smash" ([R] in the paper).
   - Hand-label 200–300 smashes (jump vs standing) from FineBadminton plus our own footage, with Label Studio video-timeline labels.
2. **Calibration:** fit thresholds and logistic weights on the features: ankle/heel lift versus the pre-stroke baseline (box-normalised), hip vertical-velocity peak, airborne court-projection discontinuity, contact height versus the head keypoint.
3. **Metrics:** AUC, accuracy, ECE.
4. **Target:** accuracy ≥ 0.80 with ECE ≤ 0.10. Otherwise train a 1D-CNN on the same pose windows.

### T4. Court keypoints
1. **Data:**
   - Label 1 frame per camera shot across FineBadminton (70 venues/matches) and ShuttleSet (44): ~300–600 frames.
   - Pseudo-label further frames with court_kpRCNN (arthur900530) and homography propagation within each shot.
   - **Keypoints:** 4 doubles-court corners, 4 singles sidelines × back lines, 2 net posts, the service-line T-junctions (~16–22 points).
2. **Model:** TennisCourtDetector-style heatmap network, or RTMPose with court "keypoints" (Apache toolchain), followed by RANSAC homography and line refinement.
3. **Split:** **hold out venues**.
4. **Metrics:** keypoint pixel error, reprojection error, and the share of shots with a valid homography.
5. **Target:** reprojection ≤ 5 px @720p on held-out venues.

### T5. Shuttle fine-tune (conditional on E3)
- **Data:** RacketVision badminton (114k frames) + the TrackNetV2 dataset + pseudo-labels from TrackNetV3 at high confidence on FineBadminton.
- **Ablations:** TrackNetV4 motion-prompt layer (2 params); background `concat` vs none.
- **Metrics:** F1 at τ = 4 px, MDE.
- **Distillation:** only if a stronger teacher (TrackNetV3 + InpaintNet bidirectional) is clearly better than the live causal student. In that case distil into the TOTNet or RacketVision causal student for the live profile.

### Active-learning loop (applies to T1–T5)
1. The pretrained pipeline makes predictions.
2. Confidence and disagreement filtering (TrackNet vs WASB; hit heuristic vs model; BST top-2 margin < 0.15; OCR vs geometry score).
3. Uncertain windows go into the Label Studio queue, with the web app's review UI writing `human_verified` events.
4. Fine-tune.
5. Repeat.

Uncertainty sampling typically needs a fraction of random-sampling labels [R, Settles survey]. **Expected effect [E]: 3–5× fewer manual labels.**

### Hard-case evaluation taxonomy
Every evaluation set is reported per category:
- normal broadcast, fast rally, slow rally
- smash, jump smash, net play
- motion blur, occlusion, player overlap at net, shuttle occlusion
- poor lighting, low resolution (≤480p), compression
- camera movement / zoom, replay, slow motion, multiple angles, partial court

Sources: FineBadminton and ShuttleSet (broadcast); BFMD (replays, Hawk-Eye); VideoBadminton (club camera, evaluation only, non-commercial); our own footage (amateur/phone).

---

# PART 8 — Model comparison matrix

Accuracy and speed columns are **[R] unless marked**. "RTX 4000 Ada" column is **[E]**. Nothing is measured yet.

| Component | Model | Pretrained | Dataset | Accuracy [R] | Speed [R] | VRAM [E] | RTX 4000 Ada latency [E] | Badminton suitability | Fine-tune? | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|
| Shuttle | TrackNetV3 | Yes [V] | Shuttlecock Traj. | F1 98.56 | 25 fps e2e (HW?) | <1.5 GB at batch 8 | 5–10 ms/forward → 0.6–1.3 ms/frame at step 8 | High (broadcast) | If E3 fails | **Keep (VOD)** |
| Shuttle | RacketVision balltrack | Yes [V] | RacketVision 461 badminton clips | P .915 / R .865, MDE 1.54 px | U | <1.5 GB | U | High, diverse broadcasts | — | **Benchmark (live)** |
| Shuttle | TOTNet | Yes [V] | badminton split | acc .89 / .84 occluded | 28 fps | ~1 GB | U | High | — | **Benchmark (live)** |
| Shuttle | WASB | Yes [V] | badminton | F1 93.1 (strict) | 34–70 fps V100 | <0.5 GB | ~2–4 ms | High | — | **Second opinion** |
| Shuttle | TrackNetV4/V5 | **No** | — | F1 97.9 / 98.6 | — | — | — | — | Train | Research only |
| Player | D-FINE-S / RF-DETR-S | Yes [V] | COCO / Obj365 | AP 50.7 / 53.0 | 3.5 ms T4 | ~0.5 GB | 2–3 ms | Medium-high (far player) | No | **Primary** |
| Player | YOLO11x (current) | Yes | COCO | AP 54.7 | 11.3 ms T4 | ~1 GB | 7–9 ms | High | No | **Replace** (cost, AGPL) |
| Tracking | ByteTrack | n/a | — | SportsMOT HOTA 73.0 | negligible | 0 | <0.2 ms | High (2 players) | No | **Primary** |
| Pose | RTMPose-m | Yes [V] | body7 | COCO 75.8 | 2.3 ms/crop 1660 Ti | ~0.3 GB | 1–2 ms (2 crops) | High | If E5 fails | **Fast primary** |
| Pose | RTMPose-x halpe26 384 | Yes [V] | Halpe | U | U | ~0.6 GB | 3–6 ms | High (feet) | — | **Quality / jump** |
| Pose | ViTPose++-B | Yes [V] | multi | 77.0 | U | ~0.5 GB | 2–4 ms | High (blur-robust) | — | Benchmark |
| Pose | RTMO | Yes | body7 | 68.6–74.8 | 9–19 ms | ~1 GB | 9–20 ms | Low for 2 persons | — | **Reject** |
| Court | heuristic + manual | n/a | — | U | — | 0 | ≈0 | Medium | — | **Start** |
| Court | custom keypoint net | **No** | to label | — | — | ~0.3 GB | ~2 ms per shot | High once trained | **Train (T4)** | Phase 3 |
| Racket | RacketVision RacketPose | Yes [V] | RacketVision | PCK@0.2 88.5 | U | ~1.5 GB | 5–10 ms per triggered frame | High | If E10 fails | **Event-triggered** |
| Contact | heuristic fusion | n/a | — | U | — | 0 | ≈0 | Medium | — | **Baseline** |
| Contact | HitNet-style GRU (ours) | **No** | FineBadminton + ShuttleSet | target F1 ≥ .90 | — | ~0 | ~0.1 ms | High | **Train (T1)** | **Phase 2** |
| Stroke | BST-CG-AP | Yes [V] | ShuttleSet | macro-F1 .810 | — | ~0.1 GB | ~1 ms per hit | High (singles broadcast) | Conditional (T2) | **Primary** |
| Stroke | VideoMAE-B (HF) | Yes | unknown | inconsistent | — | ~1 GB | ~15–30 ms per clip | Unknown, NC licence | — | **Reject** |
| Score OCR | RapidOCR/PaddleOCR | Yes | — | U on score bugs | — | ~0.3 GB / CPU | 2–10 ms at 1–2 Hz | High (broadcast) | No | **Use** |

---

# PART 9 — Pipeline comparison

| Pipeline | Description | Accuracy | GPU ms/frame [E] | Latency | Complexity | Verdict |
|---|---|---|---|---|---|---|
| **A — Maximum accuracy** | TrackNetV3 step 1 (8-way ensemble) + InpaintNet + WASB on every frame; D-FINE-M every frame; RTMPose-x 384 + ViTPose++ every frame; racket model every frame; BST adaptive (`seq_len=100`) + ASF offline re-score | Highest | 25–45 | VOD only (non-causal, ~1.5–3 s look-ahead) | High | Offline "refine" pass for exports and research |
| **B — Maximum speed** | TrackNetV3 step 8 FP16; D-FINE-S every 3rd frame + ByteTrack; RTMPose-m every 2nd frame; no racket; heuristic contact; BST fixed window | Lowest of the set; loses impact-phase pose frames | 3–5 | Low | Low | CPU-lite / multi-session profile |
| **C — Hybrid cascade** | B, plus confidence-triggered escalation: low shuttle confidence → step 1 ensemble window, then WASB; tracker loss → detector; low pose confidence → RTMPose-x re-crop | Near A on hard windows | 5–9 average | Low | Medium | Part of the recommendation |
| **D — Event-triggered specialists** | Continuous shuttle + players + pose; on a contact candidate: racket model, high-res pose, BST, smash/jump fusion | Concentrates compute where information value is highest | +~2–4 average | +0.5 s semantic latency | Medium | Part of the recommendation |
| **E — Multi-rate** | Rates set by state: IN_PLAY vs IDLE/REPLAY (hypothesis table in Part 10) | Same as C+D in play; skips idle work | lowest average | — | Medium | Part of the recommendation |

**Recommended = C + D + E combined** ("multi-rate, confidence-cascaded, event-triggered"), with A available as an asynchronous refinement pass for VOD exports.

### Which combinations beat single models [R/E]
1. **TrackNetV3 + trajectory filter/gap fill + physics gate > TrackNetV3 alone.** The branch's filter and fill exist because raw TrackNet produces spikes and gaps.
2. **TrackNetV3 + WASB disagreement > either alone** on hard windows. Two architecturally different trackers fail differently [E]. The cost is paid only on disputed windows.
3. **Detector every k frames + ByteTrack > detector every frame**, both in cost (k×) and in identity stability.
4. **BST + shuttle kinematics > BST alone for smash.** BST's weakest confusion is smash vs wrist smash [R]; post-contact speed and angle disambiguate.
5. **Rule-engine outcome + scoreboard OCR > either alone.** Geometry gets the reason right 85.7% of the time but the winner only 68.9% [R]; OCR fixes the winner directly on broadcasts.
6. **Pose proxy + event-triggered racket model > a continuous racket model**, at roughly a quarter of the cost [E].
7. **Not worth it:** a VideoMAE stroke ensemble (≈20–30× BST's cost, untrustworthy weights); a deep ReID model for singles; a learned rally segmenter before the rules fail.

---

# PART 10 — Real-time compute model (30 fps source; all values are hypotheses until Phase 0)

| Component | IN_PLAY rate | IDLE / between rallies | REPLAY / cut / close-up | Trigger-based |
|---|---|---|---|---|
| Decode (NVDEC) | 30 | 30 (needed for rally-start detection) | 30 (or skip if the cut index marks a replay) | — |
| Shuttle (TrackNetV3, step 8 windows) | 30 (every frame inferred once) | 30 at step 8 (cheap), or 15 with a gate | 0 (suppressed) | step 1 ensemble on low-confidence windows |
| Player detector | 15 (every 2nd frame) | 3–6 | 0 | forced on cut / track loss |
| Tracker | 30 | 30 | reset | — |
| Pose (RTMPose-m, 2 crops) | 30 (the impact phase lasts ~2–3 frames) | 5 | 0 | high-res re-crop around contacts |
| Court | — | verify every 1–2 s | recalibrate on returning to the main camera | on cut |
| Scoreboard OCR | 1–2 Hz | 1–2 Hz | 0 | on rally end |
| Racket model | 0 | 0 | 0 | ±4–8 frames around each contact candidate |
| Contact detector | 30 (on track features) | 30 | 0 | — |
| BST stroke | — | — | — | once per contact, after +0.5 s |
| Smash / jump fusion | — | — | — | per smash candidate |
| Rally FSM, BWF state, analytics | per event | per event | frozen | — |
| LLM agents | — | — | — | asynchronous: rally end / game end / user question |

**Expected saving from state gating [E]:** in broadcast matches, live play is roughly 35–50% of the timeline; the rest is between rallies, replays and breaks. This needs measuring on FineBadminton, which has rally boundaries. Pose, detector and racket compute therefore drop by about 50–65% versus always-on. Escalations add an estimated ≤15% (budgeted).

**Frontier-lead principle for VOD:** source-to-visible latency is effectively **zero** whenever `analysis_frontier − playhead ≥ max_lookahead + processing_latency`.
- Lookahead per component: TrackNet window 0.27 s; filter/fill ≤3 s; BST adaptive ≤~1.5 s after the next opponent hit.
- So a **startup lead buffer of about 5 s** plus **sustained throughput ≥1.0×** makes every overlay and label appear *exactly at its moment in the video*, including non-causal ones. **The engineering target for VOD is therefore throughput and startup lead, not per-frame latency.**

---

# PART 11 — RTX 4000 Ada resource plan

**Specs:**
- 6,144 CUDA cores, 192 4th-generation Tensor Cores, 26.7 FP32 TFLOPS, 20 GB GDDR6 ECC, **360 GB/s**, 130 W [R, vendor].
- The quoted "327.6 TFLOPS" tensor figure is FP8 with sparsity; dense FP16 tensor throughput is about 82–107 TFLOPS [E].

**Scaling assumptions [E]:**
- Memory bandwidth limits the full-resolution U-Net layers.
- So: about 1.5–3× T4 throughput for TrackNet, and about 0.6–0.8× T4 latency for small batch-1 models.

| Resource | Fast profile (B+C+E) | Quality profile (recommended C+D+E) | Max-accuracy (A) |
|---|---|---|---|
| GPU ms/frame, in play [E] | 3–5 | 6–12 | 25–45 |
| Throughput vs real time @30 fps [E] | ~6–10× | **~2.5–5×** | ~0.7–1.3× |
| VRAM [E] | ~2–3 GB | ~4–6 GB (incl. racket model, OCR, TensorRT workspaces) | ~8–10 GB |
| Concurrent VOD sessions [E] | 3–5 | 1–2 at ≥1× | 1 (sub-real-time) |
| CPU | Low: decode on NVDEC; CPU runs the FSM, tracker, transport and FFmpeg HLS. ~4–6 cores [E] | Same | Same |
| Resolution | 720p analysis proxy (all published models are 720p-trained); shuttle 288×512; detector 640 court-ROI; pose crops from full 720p | Same, with pose 384×288 | Same |
| Unknowns | Real TensorRT gains for TrackNet; NVDEC + PyTorch zero-copy; thermal throttling at 130 W under sustained load; VRAM headroom if a local LLM shares the GPU (recommendation: **do not run the LLM on this GPU**; keep the cloud LLM) | | |

**Measured: none.** Every value above is an estimate.

---

# PART 12 — Benchmark plan (experiments before implementation)

### E0. Evaluation data and harness bootstrap (prerequisite)
- **Data:**
  - Download 5 FineBadminton-20K matches (~3.5 GB) plus annotations, chosen for diversity and **outside** the 20 benchmark videos.
  - Request BFMD access.
  - Fetch the TrackNetV3 weights (official Drive link; compare hashes with the `TanmaySarda` mirror).
  - Fetch the TrackNetV2 test videos (the branch already holds the corrected labels).
- **Visual verification:** check FineBadminton `start_frame` semantics (contact or swing start) and fps per video.
- **Harness (`research/bench/`), one reusable CLI:**
  - **Pipeline:** decode → model(s) → postprocess, with pluggable model adapters.
  - **Stage timings:** per-stage CUDA-event timings.
  - **Metrics:** p50/p95/p99, decode fps, model fps, pipeline fps, NVML GPU utilisation / VRAM / power / clocks, psutil CPU, queue depth, dropped frames, and analytics lag versus a simulated 1× playhead.
  - **Outputs:** JSON + CSV reports and a regression baseline.

### Experiment matrix

| # | Experiment | Input | Model(s) | HW | Res | Batch | Precision | Metric | Expected | Accept |
|---|---|---|---|---|---|---|---|---|---|---|
| **E1** | Decode & preprocessing ceiling | 3 FineBadminton matches | NVDEC vs cv2 + GPU resize | RTX 4000 Ada | 720p | — | uint8 → fp16 | decode fps, CPU % | NVDEC ≥ 300 fps [E] | ≥ 150 fps with ≤ 2 cores |
| **E2** | TrackNetV3 baseline vs optimized | TrackNetV2 test split (labels in branch) + 3 FineBadminton matches | TrackNetV3: branch code as-is → step {1,2,4,8} × FP32/FP16/TensorRT × batch {1,8,16}; per-segment median vs whole-video | RTX 4000 Ada | 288×512 | 1–16 | FP32/FP16/TRT | fps, p95, VRAM, F1@τ4, F1 loss vs step 1 | step 8 FP16 ≥ 300 frames/s [E]; F1 loss ≤ 0.5 pt [U] | ≥ 90 frames/s (3×) and F1 ≥ baseline − 1 pt |
| **E3** | Shuttle bake-off | same | TrackNetV3 (± InpaintNet), RacketVision balltrack, TOTNet, WASB | same | native | best | FP16 | F1@τ4, MDE, occluded-frame recall, fps, causal latency | V3 best offline; one causal model ≥ 0.92 F1 [U] | choose VOD and live models |
| **E4** | Player detection + tracking | 3 matches; 300 hand-boxed frames including 100 jump/blur frames | D-FINE-S/M, RF-DETR-N/S/M, RTMDet-m, (YOLO11x reference only) × {full frame, court ROI} × k = {1,2,3} + ByteTrack / OC-SORT / BoT-SORT | same | 640 | 1–2 | FP16 TRT | recall on far player, jump-frame recall, ID switches per match (incl. end changes), ms/frame | ROI + D-FINE-S ≈ YOLO11x recall at ~3× speed [E] | far-player recall ≥ 0.98; 0 ID switches in play |
| **E5** | Pose | 300–500 frames hand-labelled (wrist, elbow, ankle, heel) near/far, incl. blur subset | RTMPose-m, RTMPose-l/x-384 halpe26, ViTPose++-B/L | same | crops | 2 | FP16 | PCK@0.1 (wrist/ankle), jitter before and after One-Euro, ms | x-384 and ViTPose++ better on far + blur [R] | wrist PCK ≥ 0.75 far-player blur |
| **E6** | Contact heuristic | 5 FineBadminton matches (hit frames) | shuttle direction/speed change-point + wrist proximity + side alternation | CPU | — | — | — | F1@±2/±5, hitter accuracy | F1@±5 ≈ 0.75–0.85 [E] | baseline for T1 |
| **E7** | **BST zero-shot on our pipeline** | 5 FineBadminton matches, GT hit frames (isolates the stroke stage) | BST-CG-AP ShuttleSet weights, inputs from our TrackNetV3 + RTMPose + court | GPU | — | per hit | FP32 | macro-F1 on the 12 mapped types; confusion | 0.60–0.75 [E] (domain shift) | ≥ 0.70 → no fine-tune; else T2 |
| **E8** | Rally / serve / score | 5 matches (rally frames, server, point reason) | hit-driven FSM vs branch `detect_rallies` + BWF state + rule engine (+ OCR) | CPU | — | — | — | rally F1 @tIoU 0.5, server accuracy, point-winner accuracy with/without OCR | OCR lifts winner ≥ 95% [E] | rally F1 ≥ 0.9; score correct ≥ 95% (OCR) |
| **E9** | Full perception pipeline throughput | 2 full matches | shuttle + detector + tracker + pose (multi-rate, state-gated) | RTX 4000 Ada | — | — | FP16 TRT | sustained throughput ×RT, p95/p99 per stage, VRAM, GPU %, thermals over 30 min | 2.5–5× [E] | ≥ 2× sustained (Level 3) |
| **E10** | Event-triggered racket | 300 contacts | RacketVision RacketPose on ±4/±8 frames | same | crop | ≤ 16 | FP16 | racket-head PCK on 100 labelled frames, ms per contact, contact-F1 gain when fused | +2–5 F1 points [U] | keep only if gain ≥ 2 pt at ≤ 15% compute |
| **E11** | Smash and jump-smash fusion | 300 labelled smashes (jump/standing) + FineBadminton smash/kill labels | BST p(smash) + kinematics; jump features | CPU | — | — | — | smash F1; jump AUC / accuracy / ECE | smash F1 ≥ 0.85; jump AUC 0.75–0.9 [U] | jump acc ≥ 0.80 else T3 classifier |
| **E12** | **Playback synchronization prototype** | 1 match | HLS (FFmpeg fMP4) + hls.js + `requestVideoFrameCallback` + WebSocket replaying E9 tracks | browser + server | 720p | — | — | overlay frame error (test hook), WS lag p95, seek-recovery time, CPU in browser | ≤ 1 frame error [E] | ≤ 1 frame p95; seek ≤ 3 s p95 |
| **E13** | TensorRT / quantization | E2/E4/E5 models | FP32 vs FP16 vs INT8 (calibrated on FineBadminton frames) | same | — | — | — | accuracy delta, speed-up | FP16 ~lossless; INT8 risky for shuttle localization [E] | INT8 only if Δ ≤ 0.5 pt |
| **E14** | Live causal profile | RTSP replay of a match via MediaMTX | causal shuttle winner from E3 + same stack | same | — | — | — | glass-to-overlay latency p95, label latency | — | Level 4 thresholds (Part 16) |

### Highest-value first experiments
1. **E0** (data + harness) → **E2 + E9**: is the RTX 4000 comfortably real-time?
2. **E7**: does stroke need training?
3. **E6**: how good is contact without training?
4. **E3**: which shuttle model for VOD vs live?
5. **E12**: is the sync architecture sound?

These five remove the largest uncertainties: compute feasibility, the two semantic unknowns, the live-model choice, and frontend risk.

---

# PART 13 — Recommended architecture

## 13.1 Three options

| | **Option A — Simplicity** | **Option B — Best real-time quality (RECOMMENDED)** | **Option C — Research-grade** |
|---|---|---|---|
| Perception | TrackNetV3 step 8; D-FINE-S + ByteTrack; RTMPose-m | Option A + multi-rate state gating + confidence cascade (V3 step-1 window, WASB, high-res pose re-crop) + event-triggered RacketVision + scoreboard OCR | B + continuous racket model, ViTPose++-L, V4/V5 reimplementations, learned rally segmentation, 3D trajectory fitting, uncertainty calibration (conformal) |
| Semantics | heuristic contact; BST fixed window; rule engine; BWF state | trained causal contact model (T1); BST (fine-tuned if E7 requires); smash/jump fusion; rule engine + OCR; BWF state | + ASF bidirectional re-scoring, tactical GNN, forecasting (ShuttleNet/DyMF) |
| Accuracy | Medium | High | Highest (where research succeeds) |
| GPU ms/frame [E] | 3–5 | 6–12 | 20–45 |
| VRAM [E] | 2–3 GB | 4–6 GB | 8–12 GB |
| Complexity / effort | Low / ~4–6 weeks | Medium / ~10–14 weeks | High / 6+ months |
| Robustness | Medium | High (degradation paths, cross-checks) | High but fragile in integration |
| Training need | none | T1 (definite), T2/T3 (conditional), T4 (Phase 3) | many |
| Live compatibility | Good (swap the shuttle model) | **Good** (causal profile designed in) | Poor (non-causal research models) |

**Why B:**
- It spends GPU only where uncertainty or information value is high.
- Its single mandatory training job (contact) is small, cheap, and fully supported by an Apache-2.0 public dataset.
- Every other component starts pretrained.
- It keeps one architecture for VOD and live: only the shuttle model and look-ahead settings change.
- Option A is its first milestone, so nothing is wasted.

## 13.2 Architecture (event-driven; validated against the requirements)

```
SOURCE (file | YouTube→yt-dlp | later RTSP/SRT/WebRTC via MediaMTX)
  │ ingest: ffprobe → CFR 720p H.264 proxy + HLS fMP4 + cut index + per-shot bg median + court proposal + OCR ROI
  ▼
DECODE ONCE (NVDEC → GPU tensors, frame_idx/pts_us) ──► fan-out (CUDA streams)
  ├─ Shuttle: TrackNetV3 (VOD) | causal model (live) ─► filter/gap-fill ─► shuttle track
  ├─ Players: D-FINE-S/RF-DETR (k=2, court ROI) ─► ByteTrack ─► court-side identity
  ├─ Pose: RTMPose top-down (2 crops, every in-play frame) ─► One-Euro
  └─ Court: per-shot homography (+verify) ; OCR @1–2 Hz
  ▼  ordered by frame_idx
TEMPORAL ENGINE (single sequential consumer per session, CPU)
  contact detector ─► [trigger] racket model + high-res pose ─► BST stroke ─► smash/jump fusion
  rally FSM ─► rule-engine outcome ─► BWF match-state machine (◄ OCR cross-check)
  analytics accumulators (court-coord heatmaps, zones, speeds, momentum)
  escalation policy (budgeted) ─► refinement jobs ─► corrections
  ▼  append-only
EVENT STORE (SQLite events + Parquet tracks) ─► WebSocket deltas ─► React UI (hls.js + rVFC canvas)
                                              └► async LLM agents (rally/game/Q&A, cite event_ids) ─► exports/legacy
```

## 13.3 Canonical event representation
The earlier plan's schema is validated and kept. It is an ordered, append-only `Event` with:
- `event_id`, `session_id`, `schema_version`, `type`
- `frame_start`/`frame_end`, `pts_us`
- `actors{player_id, track_id}`, `payload`
- `confidence`, `band{confirmed, probable, uncertain, unknown}`, `status{provisional, confirmed, corrected, retracted, human_verified}`
- `evidence[]` (frame windows, track refs, pose refs)
- `provenance{model@version, params_hash, worker}`, `supersedes`, `parent_id`

Additions from this research:
- **Per-frame high-rate data stays out of events.** It lives in Parquet `TrackSample`s keyed by `frame_idx`; events reference them.
- **`evidence.contact` carries every component score** (trajectory, wrist, racket, side), so smash and jump decisions are auditable and calibratable.
- **`MatchState` snapshots** are written at every point plus a checkpoint every 10 s, so seeks can resume.
- **Ground truth lives in the same store** as `status=human_verified` / `source=dataset:<name>`. Evaluation is then a join, not a separate format.

## 13.4 VOD vs live: exactly what differs

| Component | VOD profile | Live profile |
|---|---|---|
| Shuttle | TrackNetV3 (8-frame windows) + InpaintNet + 90-frame gap fill | RacketVision balltrack or TOTNet (causal, E3); gap fill emits **async corrections** |
| Background | per-shot median from ingest | rolling median over a warm-up window, reset on cuts |
| Rally FSM | 15-frame look-ahead, 150-frame look-back | bounded 10-frame look-ahead; start corrected retroactively |
| Stroke | BST adaptive window (better) or fixed | BST fixed ±0.5 s (label at +0.5 s) |
| Outcome / score | same | same (+0.3–1 s after rally end) |
| Playback | HLS VOD/event; lead buffer ≥ 5 s | WebRTC/LL-HLS with the **video intentionally delayed** by the analytics latency (~0.5–1 s), so overlays stay frame-synced |
| Everything else | identical code | identical code |

## 13.5 Media layer decision

| Option | Upload | YouTube | RTSP/SRT/WebRTC | Browser playback | GPU decode | Ops complexity | Decision |
|---|---|---|---|---|---|---|---|
| **FFmpeg** (subprocess + PyAV/torchcodec) | ✔ | ✔ (after yt-dlp) | ✔ (pull) | via HLS output | ✔ NVDEC | Low | **Now: ingest, proxy, HLS, NVDEC** |
| **MediaMTX** (MIT, single binary) | — | — | ✔ ingest + protocol conversion | ✔ WebRTC/LL-HLS | — | Low | **Live phase** |
| GStreamer | ✔ | ✔ | ✔ | via plugins | ✔ | Medium-high | Not needed |
| NVIDIA DeepStream | ✔ | — | ✔ multi-stream | — | ✔ zero-copy | High; NVIDIA/Linux lock-in; custom TrackNet plugins | Reconsider only for many concurrent live cameras |
| HLS (fMP4) | ✔ playback | ✔ | LL-HLS 2–5 s | ✔ hls.js | — | Low | **VOD playback** |
| WebRTC | — | — | ✔ sub-second | ✔ | — | Medium | **Live playback** |

## 13.6 Frontend/backend synchronization (validated)
- Video goes over HLS (later WebRTC); metadata over a WebSocket, as msgpack deltas.
- The browser maps `requestVideoFrameCallback` `mediaTime` to `frame_idx` on the canonical CFR proxy timeline.
  - That callback has been Baseline since October 2024 [R]. It can be one vsync late, so overlays are keyed by frame index.
- Client → server messages: playhead, seek, rate.
- WebSocket is chosen over SSE because it is bidirectional.
- Stack: React 19 + Vite + TypeScript, Canvas2D overlay (earlier plan §F).
- E12 validates this before UI investment.

## 13.7 Canonical timeline
- The internal source of truth is `(session_id, frame_idx)` on the CFR analysis proxy, plus `pts_us` (int64 µs) and monotonic ingest time.
- `MM:SS` strings exist only at UI/export boundaries.
- **All five current parsers and the branch's truncated `Start_Time` strings are replaced** by one `timeline` module. Its round-trip property tests guarantee frame ↔ pts ↔ display consistency.
- Evaluation is scored on frame indices, never on truncated strings.

## 13.8 Agentic layer (bounded)
- A **deterministic, budgeted escalation policy** runs in the perception loop:
  - low shuttle confidence for ≥3 frames → step-1 ensemble window → WASB → physics fit
  - contact p ∈ [0.35, 0.7] → racket + high-res pose
  - BST margin < 0.15 → `probable`
  - OCR ≠ geometry → correction + review flag
  - cut → recalibrate
- **LLM agents** (LangGraph, the existing provider factory, cloud LLM, not on the GPU) run only on rally end, game end, a detected pattern, or a user question.
  - They use tools over the event store only (`query_events`, `get_rally`, `player_stats`, `score_timeline`, `retrieve_kb`, `make_clip`).
  - Every numeric claim must cite `event_id`s (enforced by a validator).
- Measured per agent: escalation rate, accuracy gain per escalation, latency added, LLM tokens/cost.

## 13.9 Security and robustness
These carry over from the earlier plan §Q.
1. **P0:** remove and rotate the Azure key (`llm_provider.py:46-47`, local commit `4e7895f`) and the Roboflow key (`rally_detector_complete.py:53`). Scrub local history **before any push**; this needs explicit owner confirmation.
2. **Uploads:** content-addressed storage; `ffprobe` with a timeout; size/duration caps; decoding in a resource-limited subprocess.
3. **YouTube:**
   - yt-dlp with no shell, allow-listed hosts only, SSRF guards, a max filesize, rate limits.
   - **YouTube's Terms of Service restrict downloading**, so the feature sits behind a flag with a rights acknowledgement.
4. **GPU:**
   - Out-of-memory → halve the batch → fall back to the CPU-lite profile.
   - Per-session VRAM budget.
   - Worker heartbeats and chunk leases.
5. **Graceful degradation:**
   - no shuttle → player/state-only mode
   - no pose → trajectory-only strokes (`uncertain`)
   - no court → image-space analytics only
   - LLM down → deterministic templates

---

# PART 14 — Implementation roadmap (runtime)

| Phase | Content | Exit |
|---|---|---|
| **P0 — Benchmark & validation (2–3 weeks; no product code)** | Secrets hygiene; branch merge (unrelated histories; already decided); E0 data + harness; E1, E2, E3, E6, E7, E9, E12 | Part 16 P0 criteria |
| **P1 — Option A vertical slice (3–4 weeks)** | Ingest (upload + YouTube) → proxy/HLS → NVDEC decode → TrackNetV3 (optimized) + D-FINE/ByteTrack + RTMPose-m → heuristic contact → BST → rally FSM + rule engine + BWF state + OCR → event store → WebSocket → React player with overlays and live panel | P1 criteria |
| **P2 — Option B cascade (3–4 weeks)** | Multi-rate state gating; escalation policy; event-triggered racket (if E10 passes); smash/jump fusion; trained contact model (from T1); corrections protocol and review UI | P2 criteria |
| **P3 — Spatial (3 weeks)** | Trained court keypoints (T4); court-coordinate analytics and heatmaps; replay detection validated on BFMD | P3 criteria |
| **P4 — Intelligence (3 weeks)** | Grounded agents; categorised highlights with MMR diversity; momentum/comeback; player-specific queries; exports including the legacy 8-column CSV | P4 criteria |
| **P5 — Live (3 weeks)** | MediaMTX + causal profile + WebRTC delayed-video sync (E14) | P5 criteria |

# PART 15 — Training roadmap (separate track; runtime consumes only registry artifacts)
1. **During P0:** E0 verification of FineBadminton semantics; feature-extraction job over FineBadminton + ShuttleSet with the E2/E4/E5-selected models (~10–11 GPU-hours [E]); label-mapping tables (FineBadminton/ShuttleSet → `ontology.yaml`).
2. **Overlapping P1:** **T1 contact model**. Also start Label Studio for 300 jump/standing smashes and 300–500 pose-validation frames.
3. **Conditional on E7:** T2 BST fine-tune. **Conditional on E11:** T3 jump classifier.
4. **P2–P3:** T4 court keypoints (label ~300–600 shot frames across ~100 venues; venue-held-out splits).
5. **Only if E3 fails on our footage:** T5 shuttle fine-tune (+ V4 motion layer ablation; distillation to a causal student for live).
6. **Continuous:** active-learning loop from production low-confidence windows; model registry with sha256, licence, metrics and benchmark report; promotion gated by the frozen evaluation set plus latency SLOs.

# PART 16 — Acceptance criteria

### Real-time levels (definitions recommended for this product)

| Level | Definition (VOD unless stated) | Threshold |
|---|---|---|
| **L1 Progressive** | Analysis keeps moving forward and stays bounded | Throughput ≥ 0.5× real time sustained; no frontier stall > 5 s; UI shows "analysed up to" |
| **L2 Real-time synchronized** | Analysis keeps pace with 1× playback | Sustained throughput ≥ 1.0× (5th percentile of 10 s windows); startup to first overlay ≤ 5 s after the first HLS segment; overlay alignment ≤ 1 frame p95; every label visible no later than its source moment + 0.5 s |
| **L3 Comfortable real-time** | Enough margin that non-causal stages are invisible and seeks are cheap | Throughput ≥ 2× sustained over a full match; lead ≥ 10 s after 15 s of playback; seek recovery ≤ 3 s p95; all labels appear exactly at their source moment (lead > look-ahead) |
| **L4 Live-camera capable** | Causal pipeline on a live stream | Glass-to-overlay ≤ 500 ms p95 with the video delayed to match; stroke label ≤ 1.0 s after contact; score ≤ 1.5 s after rally end; frame drops ≤ 0.5% |

These thresholds rest on three points:
- **One frame (33 ms)** is the visible-mismatch threshold for overlays on moving objects [E].
- **±0.5 s** is the inherent window of the fixed BST classifier [V].
- **1–2 s** is typical latency for broadcast score graphics [E].

### Phase gates
- **P0:**
  - Harness reports for E1, E2, E3, E6, E7, E9 and E12 exist, with measured numbers replacing every [E] in Parts 10–11.
  - The decisions they trigger are documented: shuttle model per profile; detector; pose; fine-tune yes/no for BST; contact baseline F1.
  - gitleaks reports clean.
- **P1 (= L2 on RTX 4000 Ada):**
  - A 30-minute FineBadminton match and a YouTube URL both play with live overlays.
  - Rally F1 ≥ the branch baseline.
  - Score correct ≥ 95% of points on 5 evaluation matches (with OCR).
  - BST macro-F1 reported per category.
- **P2 (= L3):**
  - Contact F1 ≥ 0.90 @±3 frames.
  - Smash F1 ≥ 0.85.
  - Jump-smash accuracy ≥ 0.80 with ECE ≤ 0.1, or explicitly shown as `probable`.
  - Escalation ≤ 15% of compute with a measured accuracy gain > 0.
  - ≥ 2× throughput sustained over 30 minutes without thermal throttling below 1.5×.
- **P3:**
  - Court reprojection ≤ 5 px on held-out venues.
  - Replays cause 0 score changes on BFMD.
  - Heatmaps lag ≤ 1 s.
- **P4:**
  - 100% of agent numeric claims cite valid `event_id`s.
  - The "An Se Young's highlights" query returns only her won rallies.
  - Clip boundaries exactly match event frames.
- **P5:** L4 on an RTSP replay.

# PART 17 — Risks

| Risk | Detail | Mitigation |
|---|---|---|
| Model availability | TrackNetV4/V5 have no weights. Some weights live on Google Drive (link rot). HF mirrors have unverified provenance | Mirror validated weights into our own registry with sha256; prefer official sources |
| **Licensing (models)** | Ultralytics (YOLO, trackers) and boxmot are AGPL. StrongSORT is GPL. DEIMv2 is non-commercial. RF-DETR XL/Atto is PML. Sapiens is restricted. PnLCalib is GPL-2.0. The TennisCourtDetector licence is unknown | Default stack is Apache/MIT only: TrackNetV3, WASB, TOTNet, RacketVision, D-FINE, RF-DETR N–L, RTMPose, ByteTrack (roboflow `trackers`), BST |
| **Licensing (data/content)** | FineBadminton-20K is Apache-2.0, but its videos are BWF broadcasts (underlying rights unclear). ShuttleSet and RacketVision use BWF YouTube video. VideoBadminton is non-commercial. The TrackNetV2 dataset licence is unstated. Obj365 / MSMT17 pre-training terms apply | Legal review before commercial use; research use now; keep a dataset-provenance manifest |
| Accuracy / domain shift | Every model is trained on 720p broadcast singles. Amateur, phone, side view, 60 fps, doubles and low light are out of distribution | Hard-case taxonomy, our-camera evaluation set, active learning, profile-specific fine-tunes |
| BST input shift | BST was trained on MMPose RTMPose and the alenzenx TrackNetV3 fork; our inputs differ | E7 first, then T2 |
| Contact | No pretrained model exists; label semantics (FineBadminton `start_frame`) are unverified | E0 verification, T1 training, heuristic fallback |
| Jump smash | Single-camera depth/height ambiguity; few labels | Report as `probable` with confidence; calibrate per court zone; T3 |
| Latency / VRAM | All estimates are unmeasured; 130 W card may throttle; TensorRT conversion of TrackNet/BST is unproven | P0 benchmark; profiles; keep the LLM off the GPU |
| Live causality | Causal shuttle accuracy unknown | E3 / E14; delayed-video live playback |
| YouTube ingestion | ToS restrictions; yt-dlp breakage (now needs a JS runtime [R]); IP-bound URLs | Feature flag, rights acknowledgement, server-side ingestion, pinned yt-dlp with a health check |
| Frontend sync | rVFC jitter; HLS segment boundaries; seek storms | E12 before UI investment; frame-index keyed overlays; server-side seek debouncing |
| Evaluation reproducibility | The branch's ground truth is missing | Rebuild on FineBadminton + BFMD with frozen, hash-registered splits |

---

# FINAL DECISION FRAMEWORK

1. **Can the current architecture achieve useful real-time performance on the RTX 4000?**
   - **No, as written:** a subprocess/CSV chain; TrackNet with step 1, batch 1, FP32; whole-video median; YOLO11x on every frame; physical segment re-decodes; polling.
   - **Yes, once its models are re-executed correctly** inside an event-driven, decode-once, multi-rate engine. That reaches an estimated 2.5–5× real time in the recommended profile [E].
2. **Which existing models should be replaced?**
   - YOLO11x → D-FINE-S or RF-DETR-S + ByteTrack.
   - Stage-1 HSV/Kalman/random-forest/pose heuristics → discard.
   - The `ball_types` placeholder → BST.
   - Hough-only court → per-shot calibration, then a trained keypoint model.
   - Physical segment extraction → logical frame ranges.
3. **Which existing models should remain?**
   - TrackNetV3 (VOD primary), with its execution fixed.
   - The branch trajectory filter/gap-fill logic (ported).
   - `detect_rallies` as the fallback FSM.
   - `rule_engine.py` (best validated).
   - `court_presence` logic.
   - The webapp's auth and review concepts.
4. **Which new pretrained models should be introduced?**
   - D-FINE-S/RF-DETR, ByteTrack (`trackers`), RTMPose-m / x-halpe26, BST-CG-AP.
   - RacketVision RacketPose (event-triggered).
   - RacketVision balltrack or TOTNet (live shuttle), WASB (second opinion), InpaintNet (official weights).
   - RapidOCR/PaddleOCR (scoreboard).
5. **Which combinations beat single models?**
   - TrackNet + filter/gap-fill + physics gate.
   - TrackNet + WASB disagreement on hard windows.
   - Detector every k frames + tracker.
   - BST + shuttle kinematics for smash.
   - Rule engine + OCR for the winner.
   - Pose proxy + event-triggered racket model.
6. **Which capabilities require fine-tuning?** Conditionally: BST (if E7 macro-F1 < 0.70), pose (if E5 fails on far-player blur), shuttle (if E3 F1 < 0.90 on our footage), racket (if E10 fails).
7. **Which genuinely require custom training?** **Contact/hit detection (definite)**, court keypoints (for full automation), and possibly a jump-smash classifier (only if fusion fails).
8. **What is the minimum dataset?**
   - Contact and strokes: 20 FineBadminton matches (~6k hits) to start; 70 FineBadminton + 40 ShuttleSet for a good model.
   - Validation: 5–8 matches from our own camera.
   - Jump smash: 200–300 hand-labelled smashes.
   - Pose validation: 300–500 frames.
   - Court: ~300–600 shot frames across venues.
9. **What is the most efficient real-time pipeline?** Option A/Pipeline B: TrackNetV3 step 8 FP16 + D-FINE-S k=3 + ByteTrack + RTMPose-m k=2, heuristic contact, BST fixed window; ~3–5 ms/frame [E].
10. **What is the most accurate pipeline?** Pipeline A: step-1 ensemble + InpaintNet + WASB, per-frame quality pose, continuous racket model, BST adaptive window + ASF re-scoring. Offline/VOD only, ~25–45 ms/frame [E].
11. **What is the best compromise?** **Option B**: multi-rate, confidence-cascaded, event-triggered, with an async max-accuracy refinement pass for exports.
12. **First 3–5 experiments:** **E0 → E2 + E9** (compute feasibility on the real card), **E7** (BST zero-shot), **E6** (contact baseline), **E3** (shuttle bake-off for VOD vs live), **E12** (sync prototype).
13. **What to implement first after the experiments:**
    - The **Option A vertical slice (P1)**: ingest → HLS → decode-once engine with the selected models → events → BWF state → WebSocket → synchronized player.
    - In parallel, the **T1 contact training** pipeline on FineBadminton.
14. **What must NOT be implemented yet:**
    - TrackNetV4/V5 reimplementation.
    - Continuous racket inference.
    - Learned rally segmentation.
    - 3D trajectory reconstruction.
    - Tactical GNNs and forecasting.
    - VLMs in any frame loop.
    - DeepStream/GStreamer.
    - Doubles.
    - Deep ReID.
    - INT8 for the shuttle model.
    - Large-scale custom annotation before active learning narrows it.
    - Any UI beyond the E12 prototype until P0 passes.

---

### Appendix — Hugging Face URIs inspected (selection)
- **Models:**
  - `TanmaySarda/tracknetv3-weights`, `rahulanantharama/TrackNetV3-badminton`, `linfeng302/RacketVision-Models`, `Huydinh1205/shuttle_yolo11s`, `bambezius/tracknetv5-*`
  - `ustc-community/dfine-*`, `Roboflow/rf-detr-*`, `PekingU/rtdetr_v2_*`, `Intellindust/DEIMv2_*`, `Ultralytics/YOLO26`
  - `Tau-J/RTMPose`, `usyd-community/vitpose-plus-*`, `yzd-v/DWPose`, `facebook/sapiens2-pose-*`, `walterzhu/MotionBERT`, `kaiyangzhou/osnet`
  - `yexter/videomae-base-Badminton_strokes-finetuned-stroke-classification`, `phubinhdang/videomae-base-finetuned-badminton-rally`, `phubinhdang/badminton-video-trimmer`, `Arup-ai/badminton-shot-detection`, `chathushik/forensicnet-badminton-pose`
  - `Coddieharsh/tennis-court-keypoints`, `koppolusameer/yolo11n-basketball-court-keypoints`, `Davidsv/CourtSide-Computer-Vision-v1`
- **Datasets:**
  - `iLearn-Lab/Finebadminton-20K` (README, file listings, `0005_updated.json`), `iLearn-Lab/FineBadmintonBenchmark`, `OpenSportsLab/BFMD` (gated), `OpenSportsLab/bfmd-captions`
  - `linfeng302/RacketVision`, `muhabdulhaq/racketdb`, `owen1233/tracknet_preprocessd_data`, `alekcode/tracknet`, `BilltheTsar/shuttle-detection-dataset`
  - `howard9199/Badminton` (gated), `YikaiZheng/BadmintonPoses*`, and other badminton search hits (robotics and text, not useful)
- **Papers:** 2502.21085 (BST), 2508.07554 (FineBadminton), 2603.25533 (BFMD), 2306.10293 (SwingNet), 2511.17045 (RacketVision), 2512.02789 (TrackNetV5), 2409.14543 (TrackNetV4), 2311.05237 (WASB), 2508.09650 (TOTNet).
- **Spaces:** `smolagents/ml-intern` (retired), `raizahida947/badminton-stroke-classifier`, `TanmaySarda/Shuttle_Det`.
