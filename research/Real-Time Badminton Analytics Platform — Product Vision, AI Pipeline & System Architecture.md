# Real-Time Badminton Analytics Platform
## Product Vision, AI Pipeline, Model Strategy, Real-Time Architecture & Research-to-Production Roadmap

**Document Status:** Architecture & Research Foundation  
**Primary Sport:** Badminton  
**Current Inputs:** Uploaded video, YouTube badminton video  
**Future Inputs:** Live camera, RTSP, SRT, WebRTC and other live streams  
**Primary Compute Target:** NVIDIA RTX 4000 Ada — 20 GB VRAM  
**Architecture Principle:** Pretrained-first, event-driven, multi-rate, confidence-aware, evidence-grounded

---

# 1. Executive Vision

The objective is to build a **real-time, low-latency, accurate badminton analytics platform** capable of transforming badminton video into structured, synchronized and progressively available intelligence.

The platform should initially support two practical video sources:

1. **Uploaded badminton video**
2. **YouTube badminton video**

The system should analyze the video while the video is being played in the application, progressively producing analytics rather than requiring the entire video to be processed before playback begins.

The longer-term objective is to evolve the same architecture into a **true live badminton intelligence platform**, where a camera or live stream can be analyzed with minimal latency and analytics can be synchronized with the live video.

The evolution is therefore:

```text
                         CURRENT
                            │
             ┌──────────────┴──────────────┐
             │                             │
        Uploaded Video               YouTube Video
             │                             │
             └──────────────┬──────────────┘
                            ↓
                  Progressive Analytics
                            ↓
                         VOD
                            │
                            ▼
                    FUTURE PLATFORM
                            │
             ┌──────────────┼──────────────┐
             │              │              │
          Camera          RTSP            SRT
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                     Live Analytics
                            ↓
                  Low-Latency Intelligence
```

The ultimate product is therefore **not simply a badminton video-processing application**.

It is a:

> **Real-Time Multimodal Badminton Event-Understanding and Intelligence Platform.**

The system should transform:

```text
Pixels
   ↓
Measurements
   ↓
Tracks
   ↓
Events
   ↓
State
   ↓
Evidence
   ↓
Analytics
   ↓
Reasoning
   ↓
Intelligence
```

The research indicates that this architecture is technically achievable in principle on a single RTX 4000 Ada 20 GB, but the actual performance must be established through a target-GPU benchmark rather than assumed from published or estimated numbers.

---

# 2. Product Objective

The platform should eventually answer questions such as:

### Perception

- Where is the shuttle?
- Where are the players?
- Which player is which?
- Where are the players' joints?
- Where is the racket?
- Where is the court?
- Where is the shuttle relative to the court?

### Event understanding

- When did a player hit the shuttle?
- Which player hit it?
- What stroke was played?
- Was it a smash?
- Was it a jump smash?
- Where did the shuttle travel?
- Where did it land?
- When did the rally begin?
- When did the rally end?

### Match understanding

- Who won the rally?
- What is the current score?
- What game is being played?
- Who is serving?
- Is this game point or match point?
- Has the side changed?
- Is the game at deuce?

### Analytics

- Rally duration
- Number of strokes
- Stroke distribution
- Smash frequency
- Player movement
- Court coverage
- Heatmaps
- Shuttle landing distribution
- Attack/defence patterns
- Player positioning
- Rally tempo
- Winning/losing patterns
- Tactical tendencies

### Intelligence

- Why did a player win a rally?
- What tactical pattern is emerging?
- What are the player's weaknesses?
- What shots are most effective?
- Where does the opponent repeatedly attack?
- Which rallies are strategically important?
- What are the most important highlights?

The key principle is that these layers should **not all be solved by the same model**.

---

# 3. Complete Pipeline Capability Map

Before selecting individual models, the complete system should be understood as the following set of capabilities.

| # | Pipeline Component | Primary Purpose | Initial Strategy |
|---|---|---|---|
| 1 | Video Ingestion | Accept uploaded/YouTube/live sources | FFmpeg + source abstraction |
| 2 | Video Decode | Efficient frame extraction | NVDEC / GPU-aware decode |
| 3 | Video Normalization | CFR, resolution, timestamps | 720p proxy + canonical timeline |
| 4 | Playback | Synchronized user experience | HLS initially; WebRTC later |
| 5 | Shuttle Detection/Tracking | Locate shuttle continuously | TrackNetV3 for VOD |
| 6 | Shuttle Confidence | Determine tracking reliability | Confidence + temporal checks |
| 7 | Shuttle Recovery | Recover difficult shuttle cases | WASB conditional inference |
| 8 | Player Detection | Detect players | D-FINE-S / RF-DETR-S benchmark |
| 9 | Player Tracking | Maintain identity | ByteTrack |
| 10 | Player Identity | Maintain P1/P2 identity | Court side + continuity + rules |
| 11 | Pose Estimation | Track body keypoints | RTMPose-m / RTMPose-x |
| 12 | Court Detection | Locate court geometry | Existing heuristic initially |
| 13 | Homography | Convert pixels to court coordinates | Court calibration |
| 14 | Racket Detection | Locate racket around impact | Event-triggered specialist |
| 15 | Contact Detection | Detect exact hit/contact moment | Custom GRU/TCN |
| 16 | Stroke Classification | Classify badminton strokes | BST-CG-AP |
| 17 | Smash Detection | Identify smash | BST + shuttle kinematics |
| 18 | Jump-Smash Detection | Identify jumping smash | Pose + kinematics + contact + smash |
| 19 | Rally Detection | Segment rallies | Hit events + FSM |
| 20 | Rally Winner | Determine point winner | Event/rally logic |
| 21 | Score Engine | Maintain match score | Deterministic BWF state machine |
| 22 | Score OCR | Cross-check scoreboard | Low-rate OCR |
| 23 | Match State | Track game/match context | Deterministic state |
| 24 | Movement Analytics | Distance/velocity/position | Court coordinates |
| 25 | Heatmaps | Spatial analysis | Court-normalized aggregation |
| 26 | Highlight Detection | Find important moments | Event/rule/AI scoring |
| 27 | Event Store | Canonical runtime representation | SQLite/event model |
| 28 | Track Store | High-frequency trajectories | Parquet |
| 29 | Confidence/Uncertainty | Quantify reliability | Every inference layer |
| 30 | Evidence/Provenance | Explain where a result came from | Event IDs + model metadata |
| 31 | Analytics Engine | Compute badminton statistics | Deterministic analytics |
| 32 | AI Analyst | Interpret structured evidence | LLM/agentic layer |
| 33 | RAG | Rules/background knowledge | External knowledge layer |
| 34 | Real-Time Transport | Deliver analytics to frontend | WebSocket |
| 35 | Video/Analytics Sync | Synchronize overlays | Canonical PTS/frame timeline |
| 36 | Live Media Layer | Future true-live support | WebRTC/RTSP/SRT |
| 37 | Observability | Measure system health | Latency/FPS/VRAM/queues |
| 38 | Evaluation Harness | Benchmark models/pipelines | Standardized benchmark suite |

This decomposition is fundamental because it prevents the architecture from becoming one large monolithic inference pipeline.

---

# 4. Foundational Architecture Principle

The platform should follow:

> **Fast perception → persistent tracks → temporal event understanding → deterministic state → analytics → evidence → intelligence**

Rather than:

```text
Frame
 ↓
Model
 ↓
Model
 ↓
Model
 ↓
Model
 ↓
Model
```

the target architecture is:

```text
Frame
 ↓
FAST PERCEPTION
 ↓
TRACKING
 ↓
EVENT CANDIDATE
 ↓
STATE CHANGE
 ↓
SPECIALIST MODEL
 ↓
CONFIRMED EVENT
 ↓
ANALYTICS
 ↓
INTELLIGENCE
```

This is the most important architectural transformation identified by the research.

The system should be **event-driven rather than model-driven**.

---

# 5. Video Input and Media Architecture

## 5.1 Current Sources

The first production target should support:

```text
Uploaded MP4/video
        +
YouTube badminton video
```

The source layer should be abstracted so that downstream analytics do not care where the video originated.

Conceptually:

```text
VideoSource
 ├── FileSource
 ├── YouTubeSource
 ├── CameraSource
 ├── RTSPSource
 ├── SRTSource
 └── WebRTCSource
```

This avoids redesigning the analytics pipeline when live streaming is introduced.

---

# 6. Video Preprocessing

The video should be normalized into a canonical representation.

Initial processing:

```text
Input Video
     ↓
FFmpeg
     ↓
Constant Frame Rate
     ↓
720p Analysis Proxy
     ↓
Canonical Timestamp / PTS
     ↓
Playback + Analytics
```

The system should avoid repeatedly decoding the same video independently for each model.

The current architecture's repeated decoding and CPU preprocessing are identified as important performance bottlenecks.

The future target is:

```text
Decode once
     ↓
Shared frame pipeline
     ↓
GPU tensors
     ├── Shuttle
     ├── Player
     ├── Pose
     └── Event specialists
```

---

# 7. Shuttle Detection and Tracking

## Objective

Continuously determine:

```text
shuttle_x
shuttle_y
confidence
velocity
trajectory
visibility
```

The shuttle is one of the most difficult objects because it is:

- extremely small,
- fast,
- frequently blurred,
- occasionally occluded,
- sometimes hidden behind players/racket/net.

---

## 7.1 VOD Strategy — TrackNetV3

For prerecorded video, the current preferred baseline is:

### TrackNetV3

It has strong published shuttle-tracking performance and existing pretrained weights.

The report cites approximately:

- F1 ≈ 98.56
- Accuracy ≈ 97.51

but these are **published evaluation numbers, not measurements on our target footage**.

Therefore:

> TrackNetV3 should be treated as a strong baseline, not an assumed ground truth.

---

# 8. TrackNetV3 Execution Optimization

The current bottleneck is:

```text
sliding_step = 1
```

For an 8-frame temporal window:

```text
Frames 1–8
Frames 2–9
Frames 3–10
Frames 4–11
...
```

This causes significant overlap.

The report estimates approximately **8× redundant computation**.

For VOD, we can instead process:

```text
Frames 1–8
Frames 9–16
Frames 17–24
Frames 25–32
...
```

using:

```text
step = 8
```

or another benchmark-selected stride.

This should dramatically reduce unnecessary inference.

---

# 9. Analysis Lead Buffer

Because uploaded and YouTube videos already exist in full, the analyzer can work ahead of playback.

Example:

```text
Playback position = 10 seconds
Analysis frontier = 15 seconds

Lead = +5 seconds
```

Architecture:

```text
                    ANALYSIS FRONTIER
                           ↓
0──1──2──3──4──5──6──7──8──9──10──11──12──13──14──15
                         ↑
                     PLAYBACK
```

This is extremely important because it allows a VOD system to use models that require future context without necessarily creating visible playback latency.

The user sees approximately:

```text
video at 10 sec
analytics at 10 sec
```

even though the backend may already have analyzed through 15 seconds.

---

# 10. True Live Shuttle Tracking

Live video has no future frames.

Therefore:

```text
Current frame = t
```

cannot depend on:

```text
t + 1
t + 2
t + 3
```

For the future live architecture, causal shuttle approaches should be evaluated.

Candidates include:

- RacketVision balltrack
- TOTNet
- other causal shuttle trackers identified through benchmarking

The research specifically distinguishes the VOD TrackNetV3 strategy from causal live tracking.

Therefore the final platform may have:

```text
VOD profile:
TrackNetV3

LIVE profile:
Causal shuttle tracker
```

rather than forcing one model to serve both use cases.

---

# 11. Conditional Shuttle Recovery

TrackNetV3 should not necessarily be followed by another expensive model on every frame.

Instead:

```text
TrackNetV3
      ↓
Confidence / trajectory consistency
      ↓
 ┌────┴────┐
 │         │
HIGH      LOW
 │         │
accept     WASB
           ↓
       recovery
```

This is:

> **Confidence-driven conditional inference.**

WASB therefore becomes a specialist/recovery model rather than necessarily the primary tracker.

This follows the broader principle:

> Spend compute where uncertainty exists.

---

# 12. Player Detection

## Objective

Detect:

```text
Player bounding boxes
```

for each frame or selected frame rate.

The existing system uses YOLO11x, but running a large YOLO model on every frame is a major compute cost.

The research therefore recommends evaluating smaller detectors such as:

### D-FINE-S

or

### RF-DETR-S

The decision must ultimately be based on:

```text
accuracy
FPS
latency
VRAM
robustness
```

on the project's actual footage.

---

# 13. Player Tracking

Detection does not establish identity.

Therefore:

```text
Player Detector
      ↓
Bounding Boxes
      ↓
ByteTrack
      ↓
Persistent Track IDs
```

Example:

```text
P1 = track_03
P2 = track_07
```

These IDs persist through frames.

This means we don't need to run a detector and rediscover player identity from scratch every frame.

---

# 14. Singles Player Identity

For singles, an expensive ReID system may not be necessary.

Use:

```text
Court side
+
Track continuity
+
End-change rules
+
Appearance/shirt signature
```

because players generally remain on their respective court sides during a rally.

This is an example of replacing expensive learned inference with a combination of:

> tracking + domain knowledge + deterministic rules.

The research specifically identifies this as a way to avoid unnecessary ReID complexity in singles.

---

# 15. Doubles

Doubles should be treated as a later capability.

The architecture should nevertheless be designed so that:

```text
PlayerTrack[]
```

is not hard-coded to exactly two players.

Future representation:

```text
P1
P2
P3
P4
```

with:

```text
team_id
player_id
court_side
track_id
confidence
```

But doubles should not block the initial singles system.

---

# 16. Pose Estimation

Pose provides the body geometry needed for:

- contact detection,
- stroke classification,
- smash detection,
- jump-smash detection,
- movement analytics,
- biomechanics,
- positioning.

The preferred initial architecture is **top-down pose estimation**:

```text
Player Detector
      ↓
Player Crop
      ↓
RTMPose
      ↓
Keypoints
```

---

# 17. Pose Models

## Fast mode

### RTMPose-m

Use when:

- low latency is prioritized,
- enough accuracy is available,
- running on many player crops.

## Quality mode

### RTMPose-x / HALPE26

Use when:

- higher-quality keypoints are needed,
- event-triggered refinement is occurring,
- contact/stroke analysis requires additional precision.

The research favors RTMPose for the two-player badminton scenario rather than using a bottom-up multi-person pose model such as RTMO, whose major advantage is more relevant when many people must be located simultaneously.

---

# 18. Multi-Rate Pose

Pose does not necessarily need maximum-quality inference at every frame.

Possible architecture:

```text
Normal operation
     ↓
RTMPose-m
     ↓
15–30 FPS

Contact candidate
     ↓
High-quality pose
     ↓
RTMPose-x
```

Thus high-quality computation is concentrated around important events.

---

# 19. Court Detection

Court understanding provides the geometric foundation for spatial analytics.

We need:

```text
court lines
court corners
net/court geometry
homography
```

The initial strategy should use the existing court heuristic plus manual confirmation if necessary.

A dedicated court model can be trained later.

The key insight is:

> Court detection does not need to run continuously.

For a mostly static broadcast shot:

```text
Shot begins
    ↓
Detect court
    ↓
Calculate homography
    ↓
Reuse calibration
```

The research specifically recommends exploiting the static-camera property instead of repeatedly running court detection.

---

# 20. Homography

Pixel coordinates are insufficient for meaningful badminton analytics.

We need:

```text
Image coordinates
        ↓
Homography
        ↓
Court coordinates
```

Then:

```text
pixel (x,y)
      ↓
court (x,y)
```

This allows:

- real movement distance,
- player heatmaps,
- court coverage,
- shuttle landing zones,
- shot locations,
- positional analysis,
- tactical spatial analysis.

---

# 21. Racket Detection

Racket detection is useful but expensive.

Therefore it should **not** be continuously executed at maximum resolution.

Instead:

```text
Fast perception
      ↓
Possible contact
      ↓
Racket specialist
      ↓
Racket keypoints / position
```

For example:

```text
contact - 8 frames
       ↓
contact
       ↓
contact + 8 frames
```

Only this temporal window receives high-cost racket analysis.

This converts racket detection from a continuous compute problem into an event-localized problem.

---

# 22. Contact Detection — The Major Custom Model

Contact detection is currently one of the largest gaps in the pretrained ecosystem.

The question is:

> Exactly when did the racket/player contact the shuttle?

This is fundamentally a temporal event-detection problem.

Possible input sequence:

```text
12–20 frames
```

Features:

```text
Shuttle position
Shuttle velocity
Player position
Wrist trajectory
Elbow trajectory
Shoulder movement
Court-normalized coordinates
Optional racket evidence
```

Model:

```text
Small GRU
or
Small TCN
```

Output:

```text
NO CONTACT
PLAYER A CONTACT
PLAYER B CONTACT
```

The proposed model size is only approximately:

```text
16k–200k parameters
```

This is intentionally small.

The report identifies contact detection as a capability where custom training is justified rather than attempting to solve everything with a giant pretrained model.

---

# 23. Why Contact Should Be a Small Model

The task is highly structured.

Consider:

```text
t-2    shuttle approaching
t-1    shuttle approaching
t      wrist accelerates
t+1    shuttle direction changes
t+2    shuttle departs
```

The system is detecting a temporal change point.

Therefore a small temporal model can be highly effective.

There is no need for a massive vision-language model.

---

# 24. Contact Training Data

Primary candidates:

### FineBadminton-20K

The research identifies:

- 70 full-match videos
- 2,066 rallies
- 20,757 hit annotations
- player identity
- hit type
- hit subtype
- forehand/backhand
- ball area
- rally information
- server/receiver
- point reason.

This is highly valuable because it provides badminton-specific supervision.

Additional data can come from:

### ShuttleSet

which provides badminton stroke/rally-related information.

The intended philosophy is:

```text
Public data
     ↓
Train baseline
     ↓
Evaluate on target footage
     ↓
Find failure cases
     ↓
Active learning
     ↓
Small proprietary dataset
     ↓
Fine-tune
```

---

# 25. Stroke Classification

The first choice should be:

### BST-CG-AP

rather than immediately developing a custom stroke transformer.

It is particularly attractive because it uses:

```text
Pose
+
Shuttle trajectory
+
Court position
```

which are already outputs of our perception pipeline.

The report cites approximately:

```text
Accuracy ≈ 83.2%
Macro-F1 ≈ 81.0%
```

on its evaluation setup. These should be treated as published reference results, not expected production accuracy.

---

# 26. Stroke Model Decision Gate

The development policy should be:

```text
BST-CG-AP
     ↓
Zero-shot evaluation
     ↓
 ┌───┴────┐
 │        │
Good     Poor
 │        │
Keep    Fine-tune
          ↓
       Evaluate
          ↓
      Still poor?
          ↓
    Train specialist
```

This establishes the project's central ML strategy:

> **Pretrained → Evaluate → Fine-tune → Train from scratch only when justified.**

The report suggests a zero-shot performance gate around Macro-F1 ≥ 0.70 as a decision criterion for whether fine-tuning is necessary.

---

# 27. Domain Shift

A pretrained model may fail even when the underlying architecture is excellent.

For example:

```text
Training pose distribution
        ≠
Our pose distribution
```

or:

```text
Training shuttle trajectory
        ≠
Our TrackNet trajectory
```

Therefore model compatibility matters.

We must test the complete combination:

```text
Our Shuttle Model
+
Our Pose Model
+
Our Court Model
+
BST
```

rather than evaluating BST in isolation.

---

# 28. Smash Detection

Smash detection should initially be an **evidence-fusion problem**, not another giant neural network.

Use:

```text
BST stroke probability
+
Shuttle kinematics
+
Contact evidence
+
Court position
```

For example:

```text
BST:
smash = 0.82

Shuttle:
high downward velocity

Trajectory:
steep downward angle

Contact:
high-confidence overhead contact
```

Together:

```text
SMASH
confidence = high
```

This is more interpretable and more robust than relying on one classifier.

---

# 29. Jump-Smash Detection

Jump smash is significantly harder.

A normal 2D video does not directly provide true 3D body height.

Therefore the initial system should estimate jump-smash probability using multiple signals:

```text
Ankle/heel movement
+
Hip vertical velocity
+
Body elevation
+
Court projection
+
Contact height
+
BST smash probability
```

Output should initially be:

```text
Jump Smash
confidence = 0.84
```

rather than an absolute claim that the player definitely jumped.

The system should explicitly support:

```text
CONFIRMED
PROBABLE
UNCERTAIN
```

states.

---

# 30. Rally Detection

The first implementation should remain deterministic.

The basic structure:

```text
First confirmed hit
       ↓
RALLY ACTIVE
       ↓
subsequent hits
       ↓
shuttle/player continuity
       ↓
last confirmed hit
       ↓
RALLY END
```

Existing rally FSM logic can therefore be retained and improved.

A learned temporal rally segmentation model should only be introduced if the deterministic approach fails evaluation.

This avoids unnecessary model complexity.

---

# 31. Rally State Machine

The rally engine should maintain states such as:

```text
IDLE
   ↓
RALLY_STARTING
   ↓
RALLY_ACTIVE
   ↓
RALLY_ENDING
   ↓
RALLY_CONFIRMED
   ↓
POINT_RESOLUTION
```

Each rally should receive a stable:

```text
rally_id
```

and every event should reference it.

---

# 32. Score Engine

Score should be deterministic.

Never ask an LLM:

> "What is the score?"

Instead:

```text
Rally Winner
      ↓
BWF Rules
      ↓
Score State Machine
```

The state engine should handle:

- points,
- games,
- matches,
- deuce,
- game point,
- match point,
- 30-point cap,
- game transition,
- court-side changes,
- server/receiver state,
- intervals.

The research also recommends OCR as an independent scoreboard cross-check.

---

# 33. Scoreboard OCR

OCR should run at a very low frequency:

```text
1–2 Hz
```

rather than 30 FPS.

It can provide:

```text
Observed scoreboard = 19–20
Internal score = 19–20
```

→ high confidence.

But:

```text
Observed scoreboard = 20–20
Internal score = 19–20
```

→ discrepancy event.

This becomes a useful independent validation mechanism.

---

# 34. Match State

The system should maintain a formal match state:

```text
Match
 ├── Game
 │    ├── Score
 │    ├── Server
 │    ├── Receiver
 │    ├── Rally
 │    └── Interval
 │
 └── Match Status
```

This state should be deterministic and auditable.

---

# 35. Movement Analytics

Once player tracks and homography exist, movement analytics become straightforward.

Possible metrics:

- total distance covered,
- average velocity,
- peak velocity,
- acceleration,
- court coverage,
- time spent in zones,
- recovery position,
- forward/backward movement,
- lateral movement.

These should be calculated from tracked court coordinates rather than raw pixels.

---

# 36. Heatmaps

Heatmaps can be generated for:

### Player position

```text
Where does Player A stand?
```

### Player movement

```text
Where does Player A move?
```

### Shuttle landing

```text
Where does the shuttle land?
```

### Shot origin

```text
Where does Player A hit from?
```

### Shot destination

```text
Where does Player A target?
```

These become particularly powerful when combined with stroke classification.

---

# 37. Highlight Detection

Highlights should be event-based.

Potential signals:

```text
Smash
+
long rally
+
close score
+
game point
+
match point
+
unusual stroke
+
high shuttle speed
+
rally winner
```

A highlight engine can assign:

```text
highlight_score
```

and retain the evidence behind it.

The system should generate clips from event windows rather than scanning the entire video again.

---

# 38. Event Store

The event store should become the **central runtime contract**.

Instead of:

```text
CSV → CSV → CSV
```

the architecture should be:

```text
Perception
     ↓
Event Store
     ↓
State
     ↓
Analytics
     ↓
Agents
     ↓
UI
```

Example:

```json
{
  "event_id": "evt_004231",
  "event_type": "stroke",
  "rally_id": "rally_032",
  "player_id": "P1",
  "frame_start": 18234,
  "frame_end": 18238,
  "timestamp": 607.80,
  "stroke": "smash",
  "confidence": 0.91,
  "status": "confirmed",
  "model": "BST-CG-AP",
  "model_version": "v1"
}
```

This creates a traceable evidence chain.

---

# 39. Canonical Timeline

Every component must use a canonical timeline.

Primary identifiers should be:

```text
frame_index
PTS
timestamp
```

rather than loosely formatted human-readable timestamps.

For example:

```text
frame = 18234
PTS = 607.80 sec
```

All components refer to the same timeline.

This is essential for synchronized overlays.

---

# 40. Provenance

Every important analytical claim should be traceable.

For example:

> Player A won 7 of the last 10 rallies.

should be backed by:

```text
rally_021
rally_023
rally_024
rally_026
...
```

Similarly:

> Player A hit 14 smashes.

should reference the underlying stroke events.

This makes the AI analyst evidence-grounded rather than generative guesswork.

---

# 41. Confidence and Uncertainty

Every probabilistic component should produce:

```text
prediction
+
confidence
+
status
```

For example:

```json
{
  "stroke": "smash",
  "confidence": 0.82,
  "status": "probable"
}
```

Possible status values:

```text
UNCERTAIN
CANDIDATE
PROBABLE
CONFIRMED
REJECTED
```

This allows the system to avoid pretending that every visual inference is certain.

---

# 42. Multi-Rate Architecture

The system should not run every model at the same frequency.

A target architecture is:

```text
                    FRAME RATE
                        │
          ┌─────────────┼─────────────┐
          │             │             │
       ~30 FPS       ~10–15 FPS      1–2 Hz
          │             │             │
       Shuttle        Players        OCR
       Tracking        Pose        Scoreboard
```

while event-triggered specialists run only when needed:

```text
                 EVENT-TRIGGERED
                       │
          ┌────────────┼────────────┐
          │            │            │
        Racket      High-res      BST
                     Pose
          │            │            │
          └────────────┼────────────┘
                       │
                  Smash analysis
```

The exact frequencies must be benchmark-selected rather than hard-coded prematurely.

---

# 43. Compute Where Information Matters

This is the central compute principle.

Imagine:

```text
30,000 frames
```

but only:

```text
~2,000 frames
```

contain high-value contact/event windows.

Instead of:

```text
30,000 × expensive model
```

use:

```text
30,000
   ↓
cheap continuous perception
   ↓
2,000 event windows
   ↓
expensive specialist models
```

This is the fundamental reason the system can potentially achieve real-time performance on a single GPU.

---

# 44. Event-Driven Conditional Compute

The complete flow becomes:

```text
Frames
   ↓
Shuttle + Player + Pose
   ↓
Possible Contact
   ↓
Racket Specialist
   ↓
Contact Confirmation
   ↓
BST
   ↓
Stroke
   ↓
Smash Evidence Fusion
   ↓
Rally State
   ↓
Point Winner
   ↓
Score Update
   ↓
Analytics
   ↓
AI Analyst
```

Notice that expensive computation occurs **because an event occurred**, not merely because another frame arrived.

---

# 45. Three Main Runtime Profiles

## Profile A — Maximum Accuracy

```text
TrackNet step 1
+
InpaintNet / recovery
+
WASB
+
larger player detector
+
high-quality pose
+
racket specialist
+
BST
+
rich event analysis
```

Purpose:

> Offline research, benchmarking, ground-truth refinement.

Not intended as the primary live product profile.

---

## Profile B — Maximum Speed

```text
TrackNet step 8
+
small detector
+
ByteTrack
+
RTMPose-m
+
lightweight contact logic
+
BST
```

Purpose:

> Fast progressive analysis.

---

## Profile C — Recommended Hybrid

```text
Fast continuous perception
            ↓
Confidence / event detector
            ↓
       ┌────┴────┐
       │         │
    reliable   uncertain
       │         │
    continue   specialist
                  ↓
          high-quality analysis
```

Purpose:

> Production-oriented balance between latency, accuracy and GPU utilization.

This is the preferred architecture.

---

# 46. VOD Architecture

For uploaded/YouTube video:

```text
Video Source
     ↓
FFmpeg
     ↓
Normalized Proxy
     ↓
Playback
     │
     ├───────────────┐
     │               │
     ↓               ↓
Analysis Engine   Frontend
     │               │
     ↓               │
Event Store          │
     │               │
     └── WebSocket ──┘
```

The analysis engine should maintain:

```text
analysis_frontier
```

ahead of:

```text
playback_position
```

Whenever possible.

---

# 47. Real-Time Definition

Real-time should not be defined simply as:

> "The model runs at 30 FPS."

Instead:

```text
Analytics Timestamp
        -
Playback Timestamp
```

is the key quantity.

For VOD:

```text
analysis = 307 sec
playback = 300 sec

lead = +7 sec
```

Excellent.

For:

```text
analysis = 298 sec
playback = 300 sec

lag = -2 sec
```

the system is falling behind.

Therefore the platform must continuously measure:

```text
analysis frontier
-
playhead
```

---

# 48. True Live Architecture

For future camera input:

```text
Camera
  ↓
RTSP / SRT / WebRTC
  ↓
Media Gateway
  ↓
Low-latency Decoder
  ↓
Causal Perception
  ↓
Tracking
  ↓
Events
  ↓
Analytics
  ↓
WebSocket
  ↓
Frontend
```

Video delivery:

```text
Camera → WebRTC → Browser
```

Analytics:

```text
Inference → WebSocket → Browser
```

These should remain separate streams but share the same canonical timeline.

---

# 49. Live Synchronization

The objective is not necessarily zero latency.

The objective is:

> **minimum practical latency while keeping video and analytics synchronized.**

A small intentional video buffer may be better than showing:

```text
video = 10.7 sec
analytics = 10.2 sec
```

because the overlay would visibly lag behind the action.

Instead:

```text
camera timestamp = 10.000
display timestamp = 10.700
analytics timestamp = 10.700
```

This produces a much better user experience.

---

# 50. LLM and Agentic Architecture

The LLM should not operate inside the frame loop.

Wrong:

```text
30 FPS
 ↓
LLM
 ↓
LLM
 ↓
LLM
```

Correct:

```text
30 FPS perception
       ↓
events
       ↓
rally complete
       ↓
analytics
       ↓
AI agent
```

The AI agent receives structured evidence such as:

```text
Rally duration: 18.2 s
Strokes: 14
Smashes: 3
Net shots: 2
Winner: P1
Distance: 14.3 m
Final stroke: smash
```

and can then answer:

> Why did Player 1 win the rally?

This is much more reliable than asking a VLM/LLM to interpret the entire video continuously.

---

# 51. Agent Tools

The future AI analyst should operate through tools such as:

```text
get_rally()
get_player_stats()
get_score_timeline()
get_stroke_sequence()
get_heatmap()
get_shuttle_trajectory()
get_event()
compare_players()
get_highlight()
retrieve_rules()
make_clip()
```

This makes the agent an **analyst over structured evidence**, not a frame-by-frame video observer.

---

# 52. RAG

RAG should provide:

- badminton rules,
- terminology,
- tactical concepts,
- player background,
- competition context,
- methodology/reference information.

But RAG should not be the source of match truth.

Match truth should come from:

```text
video
+
events
+
state
+
analytics
```

The AI should therefore distinguish:

```text
World knowledge
vs.
Observed match evidence
```

---

# 53. RTX 4000 Ada Target

The research estimates approximately:

| Runtime profile | Estimated GPU time |
|---|---:|
| Fast | 3–5 ms/frame |
| Recommended | 6–12 ms/frame |
| Maximum accuracy | 25–45 ms/frame |

These are **estimates, not benchmark results**.

At 30 FPS, the nominal frame budget is approximately:

```text
33.3 ms/frame
```

Therefore the recommended hybrid architecture is theoretically compatible with the GPU budget.

However, actual system throughput depends on:

- preprocessing,
- decoding,
- memory transfers,
- model scheduling,
- CPU/GPU synchronization,
- batching,
- queueing,
- postprocessing,
- video encoding,
- WebSocket delivery.

Therefore no production throughput claim should be made until the benchmark is complete.

---

# 54. Optimization Techniques

The runtime should investigate:

### Model optimization

- FP16
- ONNX
- TensorRT
- INT8 where accuracy permits
- CUDA graphs where beneficial

### Pipeline optimization

- GPU decode
- zero-copy / reduced-copy paths
- asynchronous inference
- batching where appropriate
- frame skipping
- temporal reuse
- ROI inference
- event-triggered inference
- multi-rate scheduling

### Architectural optimization

- shared decoding
- shared tensors
- persistent tracks
- cached court calibration
- asynchronous specialists
- analysis lead buffer

The system should optimize the **whole pipeline**, not just individual model FPS.

---

# 55. Benchmarking Framework

Before making architecture commitments, build a standard benchmark harness.

Measure:

```text
End-to-end FPS
Inference FPS
p50 latency
p95 latency
p99 latency
GPU utilization
GPU memory
CPU utilization
decode time
preprocessing time
postprocessing time
queue depth
dropped frames
analysis frontier
playback lag
thermal behavior
```

And accuracy:

```text
Shuttle detection
Player detection
Tracking
Pose
Contact
Stroke
Smash
Rally
Score
Synchronization
```

---

# 56. Key Research Gates

The most important experiments are:

## E0 — Benchmark Infrastructure

Create the evaluation dataset and measurement framework.

## E2 — Shuttle Benchmark

Compare:

```text
TrackNetV3
+
candidate causal trackers
+
recovery approaches
```

## E7 — Stroke Zero-Shot

Evaluate BST-CG-AP using our own:

```text
shuttle
+
pose
+
court
```

## E6 — Contact

Determine whether a pretrained solution is sufficient. If not, train the small GRU/TCN.

## E9 — Full Pipeline

Measure the complete stack on the RTX 4000.

## E12 — Synchronization

Verify that browser video and analytics remain synchronized.

---

# 57. Training Philosophy

The project should follow a strict hierarchy:

```text
                PRETRAINED
                    │
                    ▼
                 EVALUATE
                    │
           ┌────────┴────────┐
           │                 │
        GOOD              INSUFFICIENT
           │                 │
         KEEP             FINE-TUNE
                             │
                         EVALUATE
                             │
                      Still insufficient?
                             │
                             ▼
                     TRAIN SPECIALIST
```

This avoids unnecessary custom training.

---

# 58. Models Expected to Require Training

### High-confidence candidate

**Contact detector**

Small:

```text
GRU / TCN
```

### Conditional

**BST fine-tuning**

Only if zero-shot performance is insufficient.

### Later

**Court keypoint model**

If the heuristic/general solution does not meet robustness requirements.

### Research candidate

**Jump-smash classifier**

Only after enough reliable contact/stroke/pose evidence exists.

---

# 59. Active Learning

Instead of manually labeling everything:

```text
Model
 ↓
Predictions
 ↓
Uncertainty
 ↓
Select difficult examples
 ↓
Human annotation
 ↓
Training set
 ↓
Fine-tune
 ↓
New model
```

Example:

```text
confidence = 0.51
→ human review
```

while:

```text
confidence = 0.99
→ automatically accepted
```

This should become the long-term data strategy.

---

# 60. What Should Not Be Implemented Prematurely

The following should remain deferred until the core system is validated:

- continuous high-cost racket inference,
- learned rally segmentation,
- 3D trajectory reconstruction,
- tactical GNN,
- advanced forecasting,
- VLM in the frame loop,
- large-scale ReID,
- doubles support,
- large custom annotation projects,
- aggressive INT8 optimization before baseline accuracy is understood,
- complex streaming infrastructure before the local VOD pipeline is proven,
- replacing TrackNetV3 solely because a newer model exists.

The research explicitly recommends resisting this kind of premature expansion.

---

# 61. Recommended Development Phases

## Phase 0 — Benchmark & Ground Truth

Goal:

> Prove what is actually possible on the target hardware.

Deliver:

- benchmark harness,
- evaluation clips,
- model comparison,
- RTX 4000 measurements,
- latency profile.

---

## Phase 1 — Fast Perception

Build:

```text
Video
 ↓
Decode
 ↓
Shuttle
 ↓
Players
 ↓
Tracking
 ↓
Pose
 ↓
Court
```

Goal:

> Reliable perception.

---

## Phase 2 — Event Engine

Build:

```text
Contact
 ↓
Stroke
 ↓
Rally
 ↓
Winner
 ↓
Score
```

Goal:

> Reliable badminton events.

---

## Phase 3 — Synchronized Progressive UI

Build:

```text
Video Playback
+
WebSocket
+
Live analytics panel
+
overlays
```

Goal:

> Analytics appear while video is playing.

---

## Phase 4 — Advanced Badminton Intelligence

Add:

```text
Racket
Smash
Jump Smash
Movement
Heatmaps
Shot locations
Tactical patterns
```

---

## Phase 5 — AI Analyst

Add:

```text
Event Store
+
Analytics
+
RAG
+
Agents
+
LLM
```

Capabilities:

- Q&A,
- rally explanations,
- player comparison,
- tactical analysis,
- automated reports,
- highlights.

---

## Phase 6 — True Live

Add:

```text
Camera
+
RTSP/SRT/WebRTC
+
Causal models
+
Low-latency transport
```

The same event/analytics architecture should remain underneath.

---

# 62. Target Final Architecture

```text
                              VIDEO SOURCES
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
             Upload            YouTube           Camera
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  ↓
                         SOURCE ABSTRACTION
                                  ↓
                       FFmpeg / Media Layer
                                  ↓
                         Canonical Timeline
                                  ↓
                    Efficient Decode / GPU Frames
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
        SHUTTLE              PLAYERS                POSE
       TrackNetV3          D-FINE/RF-DETR         RTMPose
             │                    │                    │
             │                ByteTrack                │
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ↓
                          TRACK / STATE LAYER
                                  ↓
                         COURT + HOMOGRAPHY
                                  ↓
                         TEMPORAL EVENT ENGINE
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                CONTACT        RACKET         STROKE
                    │             │             │
                    └─────────────┼─────────────┘
                                  ↓
                         EVIDENCE FUSION
                                  ↓
                           SMASH / JUMP
                                  ↓
                            RALLY ENGINE
                                  ↓
                          RALLY WINNER
                                  ↓
                         SCORE STATE MACHINE
                                  ↓
                           MATCH STATE
                                  ↓
                            ANALYTICS
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
             Heatmaps         Movement          Highlights
                │                 │                 │
                └─────────────────┼─────────────────┘
                                  ↓
                            EVENT STORE
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
               WebSocket                  AI ANALYST
                    │                           │
                    ▼                           ▼
                FRONTEND                 RAG / AGENTS
                    │                           │
                    └─────────────┬─────────────┘
                                  ↓
                         BADMINTON INTELLIGENCE
```

---

# 63. Final Architectural Principles

The entire project should follow these principles.

### Principle 1 — Pretrained first

Do not train a model merely because training one is possible.

---

### Principle 2 — Benchmark before replacing

A model should be replaced because measured evidence shows that another model is better for our workload.

---

### Principle 3 — Fine-tune before training from scratch

Use domain adaptation whenever possible.

---

### Principle 4 — Train small specialists

When a missing capability is highly structured, prefer a small task-specific model over a massive general model.

---

### Principle 5 — Multi-rate everything

Different capabilities have different temporal requirements.

---

### Principle 6 — Conditional inference

Run expensive models when:

- confidence is low,
- an event occurs,
- models disagree,
- a high-value event is detected.

---

### Principle 7 — Separate perception from intelligence

Computer vision determines:

> What happened?

Analytics determines:

> What does the data show?

Agents determine:

> What does it mean?

---

### Principle 8 — Deterministic systems should remain deterministic

Score, geometry, timestamps, distances, aggregations and numerical statistics should not depend on an LLM.

---

### Principle 9 — Evidence before explanation

Every important AI claim should have underlying event/analytics evidence.

---

### Principle 10 — VOD and LIVE are different runtime profiles

VOD can use lookahead.

Live requires causal inference.

---

### Principle 11 — Optimize the system, not isolated models

End-to-end latency matters more than individual model FPS.

---

### Principle 12 — Real-time means synchronized intelligence

The true objective is:

```text
Video timestamp
        ≈
Analytics timestamp
```

not merely:

```text
Inference FPS ≥ video FPS
```

---

# 64. Final Strategic Position

The project should **not** be approached as:

> "Find the best badminton AI model."

It should be approached as:

> **Build the most efficient composition of specialized perception, tracking, temporal understanding, deterministic state machines, analytics and agentic reasoning that can continuously transform badminton video into reliable structured intelligence.**

The strongest current strategy is therefore:

```text
                  PRETRAINED MODELS
                         ↓
                    BENCHMARK
                         ↓
                SELECT BEST STACK
                         ↓
               OPTIMIZE EXECUTION
                         ↓
             MULTI-RATE ARCHITECTURE
                         ↓
             CONFIDENCE CASCADING
                         ↓
             EVENT-DRIVEN SPECIALISTS
                         ↓
             SMALL CUSTOM TRAINING
               where genuinely needed
                         ↓
                 EVENT STORE
                         ↓
                 ANALYTICS
                         ↓
                AGENTIC INTELLIGENCE
                         ↓
              SYNCHRONIZED FRONTEND
                         ↓
                 VOD REAL-TIME
                         ↓
                  TRUE LIVE
```

The current research strongly supports this direction: shuttle/player/pose perception can largely begin from pretrained components; stroke recognition has a promising pretrained candidate; contact detection is the clearest candidate for custom training; smash and jump-smash should initially be solved through multimodal evidence fusion; rally and score should remain deterministic; and expensive specialists should be invoked conditionally rather than continuously.

The **single most important next step** is therefore not to start implementing the entire platform. It is to execute **Phase 0** and experimentally establish the best complete pipeline on the RTX 4000 Ada: shuttle + player detector + ByteTrack + RTMPose + court + event scheduling, followed by the first contact/BST experiments. The research report itself explicitly identifies this benchmark-before-commitment approach as the next stage.