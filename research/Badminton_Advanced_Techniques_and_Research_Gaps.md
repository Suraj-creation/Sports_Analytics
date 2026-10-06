# **Advanced Techniques & Open Research Directions** 

Badminton Computer Vision & Sports Intelligence — Companion to the Contribution Map _What Already Exists in the Research Literature, and What Genuinely Does Not_ 

Prepared for: 6-Month Internship Application — Badminton Analytics Project 

Prepared by: Shuva 

September 2026 

_This document is grounded in real, sourced literature (papers, benchmarks, and systems, each linked). Part II surveys advanced techniques already published and usable at every level of the pipeline. Part III lists research directions that the same literature shows are genuinely still open — not yet solved by any published method._ 

**Table of Contents** 

**Part I — How to Read This Document** 

This is a companion to the Contribution Map document. That document laid out where you could contribute; this one answers two follow-up questions with citations, not opinions. 

Part II works through eleven layers of the system — from raw shuttlecock detection up to world-model reasoning — and lists the specific, named, sourced techniques that represent the current state of the art at each layer, so you know exactly what exists to build on and cite. Each section closes with a short, literaturegrounded note on what that technique family still does not solve. 

Part III turns those same "not yet solved" notes into twenty-one concrete research directions, grouped into six clusters that map back onto the Contribution Map’s extended areas. Each one names why it is still open (with the specific paper that shows the limitation) and poses it as a research question you could actually pursue — these are gaps in the published literature itself, not just gaps in this project. 

_Every technique and every gap below was verified by live literature search while preparing this document; sources are given as clickable links so each claim can be checked directly._ 

## **Part II — Existing Research-Backed Advanced Techniques** 

Organized by pipeline layer, from perception through to reasoning and system design. 

### **A. Advanced Shuttlecock / Ball Tracking & Detection** 

_Beyond TrackNetV2/V3, the tiny-fast-occluded-object tracking problem is an active, fast-moving research area across racket and ball sports._ 

- **TrackNetV3 (baseline)** —  Visibility-aware augmentation plus InpaintNet, a trajectory-rectification module that inpaints occluded/invisible-ball frames from surrounding trajectory context. _Source:_ <u>htps://dl.acm.org/doi/10.1145/3595916.3626370t</u> 

- **TrackNetV4** —  Fuses heatmap features with a learnable "motion attention map" derived from frame differences instead of relying on appearance alone; a lightweight plug-in on top of V2/V3. _Source:_ <u>htps://arxiv.org/abs/2409.14543t</u> 

- **WASB (Widely Applicable Strong Baseline)** —  High-resolution heatmap regression, position-aware training, and temporal-consistency inference in one architecture that beats six prior SOTA methods across five re-annotated datasets (tennis, badminton, soccer, basketball, volleyball). _Source:_ <u>htps://arxiv.org/abs/2311.05237t</u> 

- **TOTNet** —  Occlusion-aware 3D-conv temporal network with a visibility-weighted loss and synthetic occlusion augmentation; cuts RMSE from 37.3 to 7.2 and raises fully-occluded-frame accuracy from 0.63 to 0.80 across tennis/badminton/table-tennis (offline analytics; real-time untested). 

   - _Source:_ <u>htps://arxiv.org/abs/2508.09650t</u> 

- **BlurBall** —  Treats motion blur as signal, not noise: labels the blur midpoint rather than the leading edge and uses PCA on heatmaps to extract blur angle/length as a velocity cue (table tennis). _Source:_ <u>htps://arxiv.org/html/2509.18387t</u> 

- **"Tracking the Blur"** —  Broadcast-video ball trajectory detection that explicitly models motion blur rather than treating it as a nuisance. _Source:_ <u>htps://dl.acm.org/doi/10.1145/3689061.3689075t</u> 

- **Event-Based High-Speed Ball Detection** —  Uses event-camera streams (microsecond temporal resolution, no motion blur) instead of frame-based video for high-speed ball detection. _Source:_ <u>htps://dl.acm.org/doi/10.1145/3606038.3616164t</u> 

- **Egocentric Event-Based Ping-Pong Trajectory Prediction** —  Event camera plus gaze data achieves 4.5ms end-to-end latency versus roughly 66ms for 30fps frame-based perception, via gaze-foveated compute. _Source:_ <u>htps://arxiv.org/html/2506.07860v1t</u> 

- **Motion-Blur-Robust ViT for UAV Tracking** —  Transformer tracker with an explicit blur-robustness objective and dynamic early-exit, built for small/fast/blurry aerial targets — an analogous domain not yet applied to shuttlecocks. 

_Source:_ <u>htps://arxiv.org/abs/2407.05383t</u> 

- **Video Tiny-Object Detection via Spatial-Temporal Motion** —  Flow/motion-guided tiny-object detector (anti-UAV domain) fusing optical-flow cues with appearance to recover objects invisible in any single frame. 

_Source:_ <u>htps://openaccess.thecvf.com/content/CVPR2023W/Antt</u> i-UAV/papers/Yang_Video_Tiny- <u>Object_Detecton_Guided_by_the_Spati ali</u> -Temporal_Moton_Informati <u>on_CVPRW_2023_paper.pdfi</u> 

- **GNN-Based Table-Tennis Ball Tracking** —  Uses a graph neural network over per-frame candidate detections to model trajectory consistency, instead of pure heatmap regression. _Source:_ <u>htps://www.nature.com/artt cles/s41598i</u> -024-80056-3 

**What is NOT yet solved:** _Occlusion/low-visibility recovery is repeatedly named unsolved even by the papers proposing improvements; blur-exploiting methods assume linear blur and degrade on curved/spinaffected shuttle trajectories; event cameras need non-standard hardware incompatible with existing broadcast pipelines. No method claims a general solution across "tiny + fast + frequently invisible" simultaneously._ 

### **B. Advanced Multi-Player Tracking & Re-Identification** 

_General-purpose multi-object tracking has matured quickly; sports-specific variants expose problems generic trackers do not face._ 

- **ByteTrack** —  Associates every detection box, including low-confidence ones usually discarded, recovering occluded or blurred players other trackers drop. _Source:_ <u>htps://arxiv.org/abs/2110.06864t</u> 

- **StrongSORT** —  Upgrades DeepSORT with stronger ReID features, camera-motion compensation (ECC), and NSA Kalman filtering rather than a new architecture. _Source:_ <u>htps://arxiv.org/abs/2202.13514t</u> 

- **OC-SORT** —  An "observation-centric" reformulation of Kalman-filter SORT, robust to occlusion and nonlinear motion without needing appearance features at all. _Source:_ <u>htps://arxiv.org/abs/2203.14360t</u> 

- **BoT-SORT** —  Combines motion prediction, camera-motion compensation, and ReID for robust associations; a widely used strong sports baseline. _Source:_ <u>htps://arxiv.org/abs/2206.14651t</u> 

- **MOTRv2** —  End-to-end transformer tracker that bootstraps query-based tracking with a pretrained detector’s proposals, fixing MOTR’s weak detection performance. _Source:_ <u>htps://arxiv.org/abs/2211.09791t</u> 

- **SportsMOT** —  First large sports-specific MOT benchmark (basketball/volleyball/football); shows association, not detection, is the bottleneck because players share appearance and move erratically, motivating their motion+appearance MixSort tracker. 

_Source:_ <u>htps://arxiv.org/abs/2304.05170t</u> 

- **TeamTrack** —  Multi-sport, full-pitch MOT dataset with both fixed and moving cameras, designed to stress-test trackers under camera motion. _Source:_ <u>htps://arxiv.org/abs/2404.13868t</u> 

- **SoccerNet Game State Reconstruction** —  Full pipeline (detector + StrongSORT + ReID + jersey OCR + calibration) mapping broadcast footage to pitch-coordinate athlete identities with team/role/jersey; jersey-number recognition is flagged as the weakest module. 

_Source:_ 

<u>htps://openaccess.thecvf.com/content/CVPR2024W/CVsports/papers/Somers_SoccerNet_Game_State_Reconstructt on_Endi</u> - <u>to-End_Athlete_Tracking_and_Identfi cati on_on_CVPRW_2024_paper.pdfi</u> 

- **General Framework for Jersey Number Recognition** —  Scene-text recognition plus pose-guided torso cropping plus ReID-based outlier filtering; generalizes to unseen numbers but accuracy drops sharply (65.8%) cross-domain. 

_Source:_ 

<u>htps://openaccess.thecvf.com/content/CVPR2024W/CVsports/papers/Koshkina_A_General_Framework_for_Jersey_Number_Rt ecogniton_in_Sports_Video_CVPRW_2024_paper.pdfi</u> 

- **Jersey Number Recognition via Keyframe Identification** —  Selects the best-legibility keyframes from lowresolution broadcast video before OCR — aimed at exactly the low-res broadcast setting a badminton system would face. 

_Source:_ <u>htps://arxiv.org/abs/2309.06285t</u> 

- **Basketball-SORT** —  Replaces IoU association with homography-projected court-position association plus an ID-reacquisition module for long occlusions; explicitly limited to fixed-camera footage. _Source:_ <u>htps://arxiv.org/pdf/2406.19655t</u> 

- **Towards Real-Time Analysis of Broadcast Badminton Videos** —  The closest badminton-specific playertracking work: tracks both players and generates court-coverage heatmaps from broadcast-only visual input, validated live on Premier Badminton League 2019 broadcasts. 

_Source:_ <u>htps://arxiv.org/abs/2308.12199t</u> 

**What is NOT yet solved:** _No badminton-specific player re-ID/MOT paper solves occlusion- or camera-cut re-identification; jersey-number recognition (the standard broadcast re-ID cue) is the weakest link and does not generalize across sports; homography/court-plane methods explicitly break under jumping/aerial poses and fixed-camera-only assumptions — both problematic for badminton’s jumpsmash motion and single-panning-camera broadcasts._ 

### **C. Advanced Human & Racket Pose Estimation** 

_Body-pose estimation is mature; fusing it with racket/equipment pose for fast, contact-sport-like motion is not._ 

- **HRNet** —  Maintains high-resolution representations through the whole network instead of downsampling/upsampling; still the standard backbone many later methods build on. 

- **ViTPose** —  Shows plain, non-hierarchical ViT backbones (no pose-specific design) scale and transfer better across datasets/resolutions than CNN pipelines. _Source:_ <u>htps://arxiv.org/abs/2204.12484t</u> 

- **RTMPose** —  Real-time top-down pipeline co-optimizing architecture, training, and post-processing; reports 90%+ AP on COCO at 430+ FPS. _Source:_ <u>htps://arxiv.org/html/2303.07399v2t</u> 

- **DWPose** —  Whole-body (body+hand+face) pose via two-stage distillation from a large teacher into a lightweight student — relevant for grip/racket-hand tracking. _Source:_ <u>htps://github.com/ideat</u> -research/dwpose 

- **PoseBench** —  A robustness benchmark (not a new method) finding motion blur is the single most damaging corruption to pose models, and that regression-based methods resist occlusion better than heatmap-based ones despite lower clean-data accuracy. 

_Source:_ <u>htps://arxiv.org/abs/2406.14367t</u> 

- **MotionBERT** —  Unified pretraining using a Dual-stream Spatio-temporal Transformer on a large mixed 2D/3D/mocap corpus, fine-tunable for 3D lifting, mesh recovery, or action recognition. _Source:_ <u>htps://arxiv.org/abs/2210.06551t</u> 

- **MotionAGFormer** —  Hybrid Transformer–GCNFormer improves on PoseFormerV2 for monocular 3D lifting, better handling local joint dependencies during fast, non-rigid motion. 

_Source:_ 

<u>htps://openaccess.thecvf.com/content/WACV2024/papers/Mehraban_Mott onAGFormer_Enhancing_3D_Human_Pose_Esti mai ton_With_a_Transformeri</u> -GCNFormer_Network_WACV_2024_paper.pdf 

- **Explicit Occlusion Reasoning for Multi-Person 3D Pose** —  Explicitly models inter-person occlusion in multi-view/multi-person 3D pose estimation rather than treating occluded joints as generic noise — relevant to doubles play and net collisions. 

_Source:_ <u>htps://arxiv.org/abs/2208.00090t</u> 

- **RacketVision** —  First large-scale benchmark unifying articulated racket-pose estimation with ball tracking and trajectory forecasting across tennis, table tennis, and badminton; naively concatenating racket-pose features with other modalities hurts trajectory prediction — cross-attention fusion is required. _Source:_ <u>htps://arxiv.org/abs/2511.17045t</u> 

- **Real-Time 6D Racket Pose Estimation (Table Tennis Robots)** —  Keypoint-based 6-DoF estimation of racket head/shaft orientation for a robot table-tennis system — the closest existing precedent for tracking a badminton racket’s head/shaft pose. 

_Source:_ <u>htps://www.researchgate.net/publicatt on/336469630_Reali</u> - <u>tme_6D_Racket_Pose_Esti mati on_and_Classifi cati on_for_Table_Tennis_Robotsi</u> 

**What is NOT yet solved:** _Motion blur remains the top corruption failure mode for SOTA 2D/3D pose models; racket-pose fusion is non-trivial (naive fusion degrades results); multi-person occlusion is still an active research area; whole-body/hand models still lag under fast motion because hand keypoints are smaller and blur first._ 

### **D. Advanced Camera Calibration & Court Registration** 

_Recovering a metric court coordinate system from an uncalibrated broadcast camera is its own research field._ 

- **PnLCalib** —  A non-linear refinement module using detected field lines (not just point keypoints) to correct initial pose estimates. _Source:_ <u>htps://arxiv.org/abs/2404.08401t</u> 

- **"No Bells, Just Whistles"** —  Leverages geometric field properties (line/conic structure) rather than pure black-box keypoint regression for field registration. _Source:_ <u>htps://arxiv.org/abs/2404.08401v1t</u> 

- **KaliCalib** —  Encoder-decoder network regressing basketball court keypoints under perspective-aware sampling constraints plus basket-position regression; won the MMSports 2022 challenge. 

_Source:_ <u>htps://arxiv.org/abs/2209.07795t</u> 

- **A Deep-Learning Framework for Racket Sports Court Registration** —  Directly targets racket-sport court layouts (tennis/badminton-style lines) — the most directly transferable prior work for a badminton courtregistration model. 

_Source:_ <u>htps://link.springer.com/chapter/10.1007/978t</u> -3-031-63219-8_2 

- **TennisCourtDetector** —  Deep keypoint-detection network for tennis court corner/line-intersection localization, widely reused as a base for racket-sport court registration. _Source:_ <u>htps://github.com/yastrebksv/TennisCourtDetectort</u> 

- **Sports Camera Calibration via Synthetic Data** —  Reduces calibration to three free parameters (focal length, pan, tilt) using a synthetic camera-pose engine plus siamese metric learning; accuracy drops from ~92% to ~70% IoU as camera displacement from the training viewpoint grows. 

_Source:_ <u>htps://ar5iv.labs.arxiv.org/html/1810.10658t</u> 

- **A Two-Point Method for PTZ Camera Calibration** —  Calibrates pan-tilt-zoom broadcast cameras from just two point correspondences per frame using a known base pose — built explicitly for the zoom/pan drift problem broadcast cameras exhibit. 

_Source:_ <u>htps://ar5iv.labs.arxiv.org/html/1801.09005t</u> 

- **Video-Based Sequential Bayesian Homography Estimation** —  Adds temporal Bayesian filtering across frames instead of independent per-frame registration, targeting the instability/jitter deep per-frame calibration models exhibit on broadcast video. 

_Source:_ <u>htps://arxiv.org/abs/2311.10361t</u> 

- **Enhancing Soccer Camera Calibration Through Keypoint Exploitation** —  Derives 57 geometric keypoints via an HRNetV2-W48 backbone plus an "Iterative Voter" consensus algorithm; the authors note adding extra low-confidence points can decrease accuracy and that real-time performance was out of scope. _Source:_ <u>htps://arxiv.org/html/2410.07401v1t</u> 

- **SoccerNet-Depth / Foundation Monocular Depth Adaptation** —  Dataset and foundation-modeladaptation work using synthetic supervision to get match-level-reliable monocular depth in sports video — the closest existing template for recovering court-relative height from a single broadcast camera. _Source:_ <u>htps://pmc.ncbi.nlm.nih.gov/artt cles/PMC13364479/i</u> 

**What is NOT yet solved:** _Every recent registration paper cites partial occlusion of court lines and unconstrained/variable focal length (zoom) as unresolved error sources; accuracy documents a concrete cliff with camera displacement/weather; PTZ drift breaks static-homography assumptions; monocular sports-depth work is still "adapting general foundation models" rather than a mature sport-native solution._ 

### **E. Advanced 3D Trajectory Reconstruction & Physics-Informed Modeling** 

_Recovering true 3D position, angle, and spin of a shuttlecock from limited camera views combines sportsscience physics with modern trajectory learning._ 

- **Cohen, Berry & Cohen, "The Physics of Badminton" (New J. Phys., 2015)** —  Models flight as pure quadratic drag with an "aerodynamic length" Λ ≈ 4.6m; shows the cork/skirt mass-pressure offset causes range to saturate logarithmically rather than follow a parabola, plus a post-impact 15–40ms "flip" and 

damped oscillation absent in ball flight. Assumes constant drag coefficient and does not model racketimpact dynamics. 

_Source:_ <u>htps://iopscience.iop.org/artt</u> icle/10.1088/1367-2630/17/6/063001 

- **Hasegawa, Kitta, Murakami & Obayashi (Sports Engineering, 2013)** —  Wind-tunnel study showing spin reduces skirt deformation and drag differently than non-spinning shuttles; quantifies air leaking through skirt gaps as a major separate drag source. 

_Source:_ <u>htps://link.springer.com/artt</u> icle/10.1007/s12283-013-0112-4 

- **Zhou, Acta of Bioengineering and Biomechanics (2024/25)** —  Wind-tunnel-derived empirical drag/lift regressions; simulated trajectories matched experiment within about 5% deviation. _Source:_ <u>htps://pubmed.ncbi.nlm.nih.gov/40100993/t</u> 

- **Lin, Chua & Yeo (Proc. IMechE Part P, 2015)** —  Identifies drag parameters directly from video rather than a wind tunnel, usable as a simulation/CV prior. _Source:_ <u>htps://journals.sagepub.com/doi/10.1177/1754337114568825t</u> 

- **MonoTrack (CVPR workshop, 2022)** —  Recovers a 3D shuttle trajectory by fitting a particle-under-drag ODE to 2D detections; requires known court corners and net-pole 3D coordinates as a metric scale/depth anchor, and states this reconstruction is "ill-defined" without stereo cues. 

_Source:_ <u>htps://ar5iv.labs.arxiv.org/html/2204.01899t</u> 

- **TT3D (Table Tennis 3D Reconstruction)** —  Applies the same physics-based reprojection-minimization idea to table tennis, notably inferring spin without racket/pose tracking by using bounce-state physics instead. 

_Source:_ <u>htps://arxiv.org/abs/2504.10035t</u> 

- **"A Universal Model Combining Differential Equations and Neural Networks for Ball Trajectory Prediction"** —  An MLP predicts effective drag/spin parameters feeding per-axis ODEs; tested on badminton, table tennis, tennis, and pickleball; beats both a pure aerodynamic model and a learned baseline over long horizons, needing only a few dozen samples per ball type. 

_Source:_ <u>htps://arxiv.org/html/2503.18584v1t</u> 

- **Hybrid PINN for Ballistic Prediction (Engineering Applications of AI, 2025)** —  A general ballistictrajectory physics-informed neural network combining flight-mechanics equations with learned residuals — the methodological template racket-sports work above borrows from, not itself sports-specific. _Source:_ <u>htps://www.sciencedirect.com/science/artt cle/abs/pii/S0952197625029963i</u> 

- **Hawk-Eye Tennis System** —  8–10 high-speed cameras plus trajectory-model fitting; the vendor claims 3.6mm mean accuracy, though Cardiff University’s Harry Collins has publicly noted the error-computation methodology has never been made transparent or independently peer-reviewed. 

_Source:_ <u>htps://spectrum.ieee.org/hawkeyet</u> -in-the-crosshairs-at-wimbledon-again 

- **Badminton Trajectory Tracking via Binocular Stereo Vision + YOLOv8 (2026)** —  A badminton-specific stereo rig (50–100cm baseline, 120fps) reaching 1.26% depth MAE and 98.44% tracking success on VideoBadminton, but reported as suboptimal on embedded devices. 

_Source:_ <u>htps://link.springer.com/artt</u> icle/10.1007/s42452-026-08354-1 

- **Deep Ensembles (Lakshminarayanan et al., NeurIPS 2017)** —  The foundational non-Bayesian ensemble method for calibrated predictive uncertainty — the standard baseline any trajectory uncertaintyquantification system would build on. 

_Source:_ <u>htps://arxiv.org/abs/1612.01474t</u> 

- **CUQDS (AAAI 2025)** —  Combines Gaussian-process error modeling with online conformal calibration for vehicle trajectory prediction under distribution shift. _Source:_ <u>htps://arxiv.org/html/2406.12100v4t</u> 

- **CP-Traj (2025)** —  Adaptive conformal prediction intervals over trajectory ensembles for autonomous driving, cyclone tracks, and flu forecasting — not yet applied to sports objects. _Source:_ <u>htps://arxiv.org/abs/2508.13362t</u> 

**What is NOT yet solved:** _No monocular method recovers true 3D position without a known court/scale geometry prior (MonoTrack calls this fundamentally ill-posed otherwise); no PINN targets shuttlecock spin/angle recovery from vision directly; Hawk-Eye’s widely cited accuracy figure is an unvalidated vendor claim; and no published uncertainty-quantification method (Bayesian, ensemble, or conformal) has been applied to ball/shuttlecock trajectory tracking at all._ 

### **F. Advanced Action/Stroke Recognition & Temporal Segmentation** 

_General video and skeleton-based action recognition is mature; applying it to continuous rally structure is less so._ 

- **ST-GCN (AAAI 2018)** —  The foundational spatio-temporal graph convolutional network treating joints/frames as a graph; baseline for nearly all successors. 

- **2s-AGCN / MS-G3D** —  Added adaptive, learnable graph topology and multi-scale spatio-temporal aggregation on top of ST-GCN. 

- **CTR-GCN (ICCV 2021)** —  Learns a distinct topology per channel rather than one shared graph — a widely used strong skeleton-action baseline. _Source:_ <u>htps://arxiv.org/abs/2107.12213t</u> 

- **PoseConv3D (CVPR 2022)** —  Argues GCNs are not necessary; treats pose-heatmap volumes with 3DCNNs, outperforming GCN methods and generalizing better to fine-grained/multi-person interaction actions. 

_Source:_ <u>htps://arxiv.org/abs/2104.13586t</u> 

- **SkateFormer (ECCV 2024)** —  A transformer that partitions joints/frames by skeletal- and temporalrelation type before self-attention, claiming SOTA over recent GCN and transformer methods with better efficiency. 

_Source:_ <u>htps://arxiv.org/abs/2403.09508t</u> 

- **SlowFast Networks (ICCV 2019)** —  Two-pathway CNN (slow/high-res + fast/low-res) for video recognition; a standard benchmark baseline. 

- **TimeSformer (ICML 2021)** —  Pure-transformer "divided space-time attention" for video, convolutionfree. 

- **Video Swin Transformer** —  Hierarchical shifted-window transformer for video with strong actionrecognition results. 

_Source:_ <u>htps://arxiv.org/abs/2106.13230t</u> 

- **VideoMAE / VideoMAE V2** —  Self-supervised masked-autoencoder pretraining for video transformers, scaling label-efficient action recognition beyond labeled data. 

- **MS-TCN / MS-TCN++ (TPAMI 2020)** —  Multi-stage temporal convolutional networks, long the standard for frame-wise action segmentation of continuous untrimmed video. 

- **ASFormer (BMVC 2021)** —  A transformer replacing TCN stages for action segmentation, improving boundary accuracy. _Source:_ <u>htps://arxiv.org/abs/2110.08568t</u> 

- **ActionFormer (ECCV 2022)** —  A single-stage transformer for temporal action detection (not just segmentation), widely cited SOTA on THUMOS14/ActivityNet. 

- **FACT / OnlineTAS / DiffAct / Difformer (2024–2025)** —  Frame-action cross-attention, online/streaming segmentation, and diffusion-based segmentation formulations — the field moving toward streaming methods directly relevant to live rally/stroke boundary detection. 

**What is NOT yet solved:** _3D pose underperforms 2D pose in fine-grained sports because general-purpose pose datasets don’t cover sport-specific occlusion/fast-motion cases; and general-purpose segmentation methods are validated on cooking/assembly datasets (Breakfast, 50Salads, GTEA), not on racket-sport rally/serve segmentation — an unvalidated but very feasible transfer._ 

### **G. Existing Badminton-Specific Systems (Closest Prior Art)** 

_This is the most directly relevant section: real, published, badminton-specific datasets and models already exist and define the current frontier._ 

- **ShuttleSet (KDD 2023)** —  The largest public badminton singles dataset: 104 sets, 3,685 rallies, 36,492 strokes, 44 matches, 27 top-ranked players, each stroke labeled with one of 18 shot types, hit location, and both players’ court positions. Supports stroke-influence analysis, stroke forecasting, and movement forecasting benchmarks. 

_Source:_ <u>htps://arxiv.org/abs/2306.04948t</u> 

- **ShuttleSet22** —  Extends ShuttleSet with 2022 matches for the IJCAI 2023 stroke-forecasting challenge (30,172/1,400/2,040 strokes across train/val/test). 

_Source:_ <u>htps://arxiv.org/abs/2306.15664t</u> 

- **ShuttleNet (AAAI 2022)** —  Predicts the next stroke’s shot type and landing coordinates using a Transformer Rally Extractor, a Transformer Player Extractor, and a Position-aware Gated Fusion Network weighing rally-context versus player-style at each turn. 

_Source:_ <u>htps://arxiv.org/abs/2112.01044t</u> 

- **DyMF — "Where Will Players Move Next?" (AAAI 2023)** —  Builds a dynamic player-movement graph plus hierarchical fusion to jointly forecast return-shot type and player movement location; the first work to model strategic relations jointly across shot type and movement rather than separately. _Source:_ <u>htps://arxiv.org/abs/2211.12217t</u> 

- **TemPose (CVPR 2023 workshop)** —  A skeleton-based transformer with temporal and interaction layers, plus auxiliary shuttlecock-position input, classifying fine-grained badminton strokes from pose sequences. 

_Source:_ <u>htps://openaccess.thecvf.com/content/CVPR2023W/CVSports/html/Ibh_TemPose_A_New_Skeletont</u> - <u>Based_Transformer_Model_Designed_for_Fine-Grained_Motion_CVPRW_2023_paper.html</u> 

- **BST — Badminton Stroke-Type Transformer** —  Direct successor to TemPose adding shuttlecock trajectory and court position; reaches 82.54% accuracy / 0.798 macro-F1 on ShuttleSet-merged, 65.17% on BadmintonDB, 99.23% on TenniSet. Depends on accurate upstream hit-frame detection and shuttle tracking, and is validated on singles only. 

_Source:_ <u>htps://arxiv.org/pdf/2502.21085t</u> 

- **VideoBadminton** —  An RGB-video (not skeleton) dataset: 7,822 clips, 18 BWF-aligned stroke classes, benchmarking seven SOTA video/skeleton models head-to-head. States that distinguishing subtle action differences within continuous activity remains hard, and background/context entanglement is a persistent challenge. 

_Source:_ <u>htps://arxiv.org/html/2403.12385v2t</u> 

- **"A Stroke of Genius: Predicting the Next Move in Badminton" (CVPR 2024 workshop)** —  Same research group as TemPose, extending to next-move/shot prediction. 

_Source:_ 

<u>htps://openaccess.thecvf.com/content/CVPR2024W/CVsports/html/Ibh_A_Stroke_of_Genius_Predictt ng_the_Next_Move_in_Bi adminton_CVPRW_2024_paper.html</u> 

- **"Enhancing Badminton Game Analysis" (Sensors/MDPI 2024)** —  Addresses the upstream problem of shuttlecock tracking and hit detection from a monocular camera, which BST and TemPose assume as a clean input. 

_Source:_ <u>htps://www.mdpi.com/1424t</u> -8220/24/13/4372 

- **TemPose-TF-ASF (2026)** —  A further TemPose refinement using two-stage bidirectional stroke-context fusion. 

_Source:_ <u>htps://arxiv.org/pdf/2605.02558t</u> 

- **CoachAI Badminton Environment (AAAI 2024)** —  An RL environment modeling badminton as an MDP (shot types, positions, rally rewards) using ShuttleNet/DyMF as real-match-trained opponent models, specifically to close the "simple rule-based opponent" sim-to-real gap that plagues prior sport-RL work. _Source:_ <u>htps://ojs.aaai.org/index.php/AAAI/artt cle/download/30523/32673i</u> 

**What is NOT yet solved:** _No source reports end-to-end raw-video → rally segmentation → stroke classification → tactical forecasting as one validated pipeline; each paper solves one stage assuming clean upstream inputs. Doubles play is essentially unaddressed across all of the above — every dataset and model listed here is singles-only._ 

### **H. Tactical Graph-Neural-Network Modeling** 

_Football has a landmark, expert-validated precedent for GNN-driven tactical AI; badminton does not yet have an equivalent._ 

- **TacticAI (Nature Communications, 2024; DeepMind + Liverpool FC)** —  Models each corner-kick as a graph using a geometric deep-learning graph-attention network with D₂-symmetry group convolutions to exploit pitch reflection symmetry under limited training data. Receiver-prediction top-3 accuracy 0.782; conditional shot-prediction F1 0.71; generated tactics indistinguishable from real ones by a classifier (F1 

0.60); Liverpool FC coaches preferred its suggestions over the alternative in 90% of 50 evaluated scenarios. 

_Source:_ <u>htps://www.nature.com/artt cles/s41467i</u> -024-45965-x 

- **TacticExpert** —  Combines GNNs with an LLM interface for basketball tactic representation and query — a 2025 example of GNN-plus-language-model fusion for team-sport tactics. _Source:_ <u>htps://arxiv.org/abs/2503.10722t</u> 

- **Other GNN-for-Sports Work (less rigorously validated)** —  Graph convolutional networks applied to player/ball interaction graphs for formation or event analysis in football and basketball, generally at lower validation rigor than TacticAI. 

- **ShuttleNet & DyMF (badminton analog)** —  Effectively the badminton equivalent of tactic-modeling graph/sequence work — DyMF explicitly builds a dynamic player-movement graph — but neither matches TacticAI’s scale of expert (professional-club) evaluation or its generative tactic-recommendation capability. 

**What is NOT yet solved:** _No badminton paper matches TacticAI’s scale of expert validation or generative tactic recommendation — a clear, citable maturity gap between football and badminton tactical AI._ 

### **I. Vision-Language Models & Multimodal Sports Reasoning** 

_General-purpose video-language models are increasingly being benchmarked on sports, with informative failure results._ 

- **Sports-QA** —  A large-scale VideoQA benchmark for complex/professional sports (gymnastics, diving, etc.) requiring multi-step reasoning over actions. _Source:_ <u>htps://arxiv.org/abs/2401.01505t</u> 

- **SportR** —  A multimodal-LLM benchmark across basketball/soccer/table-tennis/badminton/football with a visual-grounding task (bounding boxes for rule violations) plus 7,118 human chain-of-thought rationales; evaluates GPT-5, Claude 4 Sonnet, Gemini 2.5 Pro, and Qwen-VL. 

_Source:_ <u>htps://arxiv.org/html/2511.06499v2t</u> 

- **"Sports Intelligence"** —  Evaluates GPT-4o, Gemini 1.5, Claude 3 Opus, Video-LLaVA, and PLLaVA on sports knowledge, tactical-scenario analysis, and video recognition. _Source:_ <u>htps://arxiv.org/html/2406.14877v1t</u> 

- **GOAL (CIKM 2023)** —  A knowledge-grounded video captioning benchmark for real-time soccer commentary, grounding captions in a soccer knowledge graph. _Source:_ <u>htps://dl.acm.org/doi/10.1145/3583780.3615120t</u> 

- **SoccerNet-Caption** —  A dense video-captioning benchmark localizing and describing soccer events endto-end. _Source:_ <u>htps://ar5iv.labs.arxiv.org/html/2304.04565t</u> 

- **Knowledge-Guided Entity-Aware Video Captioning (basketball)** —  Entity-aware captioning grounded in player/team knowledge, with a new basketball dataset. _Source:_ <u>htps://arxiv.org/html/2401.13888v2t</u> 

- **PG-Video-LLaVA** —  A general video-LLM adding pixel-level spatial grounding of language to video regions plus audio — representative of the grounded video-LLM architecture family applicable to sports event grounding. 

_Source:_ <u>htps://www.crcv.ucf.edu/cvpr2025t</u> -vidllms-workshop/data/accepted_papers/ 

<u>CVPR25_VidLLMs_Workshop_PG_Video_LLaVA.pdf</u> 

- **Video-Bench** —  A toolkit/benchmark for evaluating general video-LLMs, useful as a baseline evaluation methodology. 

_Source:_ <u>htps://arxiv.org/html/2311.16103v2t</u> 

**What is NOT yet solved:** _SportR reports that even GPT-5 scores under 7% IoU on grounding rule violations to pixels (a fine-tuned Qwen-2.5VL-7B reaches only 9.94%); "Sports Intelligence" reports multi-hop tactical-reasoning accuracy of only 22–31% versus 96%+ for humans. Reliable, evidence-grounded tactical explanation generation for real match video remains an open research frontier, not a solved capability._ 

### **J. World Models & Reinforcement Learning for Tactics** 

_Model-based RL and world models have landmark precedents in games and simulated sport, but not yet in real racket-sport strategy._ 

- **TacticAI** —  (See Section H.) A real-data-driven, expert-validated tactical AI — but static and single-setpiece, not a sequential world model, and explicitly does not model reactive opponent counteradjustment. 

_Source:_ <u>htps://www.nature.com/artt cles/s41467i</u> -024-45965-x 

- **Google Research Football** —  An open-source, physics-based football RL environment, the standard testbed for multi-agent tactical RL research. 

_Source:_ <u>htps://arxiv.org/abs/1907.11180t</u> 

- **TiZero (AAMAS 2023)** —  Curriculum learning plus self-play achieving champion-level 11v11 play in Google Research Football — a concrete, but fully simulated, self-play tactical-optimization precedent. _Source:_ <u>htps://arxiv.org/abs/2302.07515t</u> 

- **CoachAI Badminton Environment** —  (See Section G.) The closest direct precedent for badminton: an RL environment using real-match-trained opponent models to close the sim-to-real gap for a rule-based opponent. 

- **MuZero (Nature, 2020)** —  The foundational model-based RL/world-model architecture that plans with a learned model and no given rules; never applied to a real sport. _Source:_ <u>htps://www.nature.com/artt cles/s41586i</u> -020-03051-4 

- **DreamerV3** —  A general-purpose latent world model working across diverse domains without perdomain tuning; no sports-tactics application found in the literature. _Source:_ <u>htps://arxiv.org/pdf/2301.04104t</u> 

- **DeepMind Table-Tennis Robot (Nature, 2026)** —  Real (non-simulated) RL deployed on an actual racket sport, but for physical stroke/motor control against humans, not strategic/tactical rally reasoning. _Source:_ <u>htps://www.nature.com/artt cles/s41586i</u> -026-10338-5 

**What is NOT yet solved:** _No published work applies a MuZero/Dreamer-style world model, or any modelbased RL system, to real (non-simulated) racket-sport tactical decision-making. Every existing sports-RL_ 

_system is validated only in simulation against modeled opponents, and TacticAI itself does not handle reactive, in-play opponent adjustment._ 

### **K. Uncertainty-Aware / Conditional-Compute Inference Patterns** 

_The proposed "only escalate to expensive analysis when confidence is low" design is a well-established general ML pattern, though not yet validated for sports-tactics pipelines specifically._ 

- **BranchyNet (ICPR 2016)** —  The founding early-exit architecture: exits inference early via entropy-based confidence, reporting large speedups with minimal accuracy loss. _Source:_ <u>htps://arxiv.org/abs/1709.01686t</u> 

- **Early-Exit DNN: A Comprehensive Survey (ACM Computing Surveys, 2024)** —  Surveys early-exit as an established, validated adaptive-inference pattern across vision and NLP. _Source:_ <u>htps://dl.acm.org/doi/full/10.1145/3698767t</u> 

- **Sparsely-Gated Mixture-of-Experts (ICLR 2017)** —  The foundational conditional-computation/gatedrouting paper. _Source:_ <u>htps://arxiv.org/abs/1701.06538t</u> 

- **Mixture-of-Experts with Expert Choice Routing (NeurIPS 2022)** —  An improved routing algorithm balancing expert load and compute cost. _Source:_ <u>htps://research.google/blog/mixturet</u> -of-experts-with-expert-choice-routng/i 

- **Conformal Prediction: A Gentle Introduction** —  The authoritative reference for distribution-free uncertainty quantification with finite-sample coverage guarantees — the standard basis for confidencetriggered gating. 

_Source:_ <u>htps://arxiv.org/abs/2107.07511t</u> 

- **Active Learning Literature Survey (Settles)** —  The canonical reference establishing uncertainty sampling as the trigger for invoking expensive labeling/computation only when needed. _Source:_ <u>htps://burrsett les.com/pub/sett</u> tles.actvelearning.pdfi 

- **Gatekeeper / Speculative Cascades (2025)** —  Recent cascade designs invoking a large/expensive model only when a cheap model’s confidence is low, with reported cost/accuracy tradeoffs. _Source:_ <u>htps://arxiv.org/html/2502.19335t</u> 

- **Viola–Jones Cascade Classifier (2001/2004)** —  The historical origin of the cascade-of-classifiers pattern for real-time detection — escalate only on ambiguous input. 

**What is NOT yet solved:** _Conformal prediction gives only marginal (average-case), not per-instance, coverage — a low-uncertainty flag can still be wrong on a specific case. Cascade/early-exit literature notes miscalibrated confidence causes wrong early exits, and almost all validation is on classification or LLM question-answering, not on structured, temporally extended tactical inference like sports analytics._ 

**Part III — Genuine Open Research Directions (No Existing Solution)** 

Twenty-one research gaps, each verified against the literature surveyed in Part II — grouped into six clusters that map back onto the Contribution Map’s extended areas (A–Q). 

### **Cluster 1 — Perception Limits That Remain Unsolved Even in 2025–2026 Papers** 

_These gaps sit directly beneath Contribution Areas A and C (shuttlecock tracking research, player/pose tracking) in the Contribution Map._ 

#### **<mark>RG1  —  A single tracker robust to t</mark> i** **<mark>ny scale, extreme blur, AND mult</mark> i** **<mark>-frame invisibility at once</mark>** 

**Why this is still open:** TrackNetV4 solves motion-attention fusion, TOTNet solves occlusion recovery, and BlurBall solves blur-as-signal — each addresses one axis of the problem, and BlurBall’s linear-blur assumption may directly conflict with a curving, spinning shuttle. 

**_Research question:_** _Can motion-attention heatmaps, occlusion-aware temporal memory, and blur-as-signal cues be combined into one architecture, and do their underlying assumptions compound or conflict?_ 

#### **RG2  —  Player re-identification without jersey numbers** 

**Why this is still open:** Every broadcast re-ID pipeline found (SoccerNet GSR, jersey-recognition papers) relies on jersey-number OCR as the primary re-ID cue — but badminton kits rarely carry large jersey numbers the way football/basketball do. 

**_Research question:_** _Can gait, body-shape, grip style, or racket-handling signatures serve as a re-ID cue for badminton players when the standard jersey-OCR cue is unavailable?_ 

#### **RG3  —  Tracking through the jump-smash (non-ground-plane pose)** 

**Why this is still open:** Every homography/court-plane multi-object tracker found (SoccerNet GSR, Basketball-SORT) explicitly assumes players stay on the ground plane — which breaks for badminton’s defining aerial smash motion. **_Research question:_** _What association method keeps a player’s identity and position stable through an airborne, non-ground-plane pose, without the ground-plane assumption every existing sports MOT method relies on?_ 

### **Cluster 2 — Multimodal Fusion of Body, Racket, and Shuttle** 

_These gaps sit beneath Contribution Areas C and E (player/pose tracking, physics-informed modeling)._ 

#### **<mark>RG4  —  Principled racket–shut</mark> t** **<mark>le–pose fusion for badminton specif</mark> i** **<mark>cally</mark>** 

**Why this is still open:** RacketVision found that naively concatenating racket-pose features hurts trajectory prediction and that cross-attention fusion is required — but this has only been demonstrated cross-sport in one benchmark, not built as a badminton-native architecture. 

**_Research question:_** _What fusion architecture (contact-event-conditioned cross-attention, or otherwise) correctly combines racket pose, body pose, and shuttle trajectory for badminton without the naive-fusion penalty RacketVision documents?_ 

#### **RG5  —  A badminton-native 3D pose training set** 

**Why this is still open:** BST’s own paper states 3D pose underperforms 2D pose because general pose-estimation training data doesn’t cover badminton-specific fast/occluded motion. **_Research question:_** _Would a badminton-specific 3D pose benchmark (built from multi-view badminton footage) close the 3D-vs-2D accuracy gap BST reports?_ 

#### **RG6  —  Doubles-play modeling** 

**Why this is still open:** Every badminton CV paper found (ShuttleSet, ShuttleNet, DyMF, TemPose, BST, VideoBadminton) is singles-only. 

**_Research question:_** _How do four-body occlusion, partner-coordination signals, and doubles-specific tactics change tracking, stroke recognition, and tactical modeling compared to the singles case every existing method assumes?_ 

### **Cluster 3 — Geometry, 3D, and Physics** 

_These gaps sit beneath Contribution Areas D and E (court geometry, physics-informed trajectory intelligence) — and are arguably the deepest, most defensible research territory in this whole map._ 

#### **<mark>RG7  —  Real-t</mark> i** **<mark>me, zoom/pan-robust court calibrat</mark> i** **<mark>on from one panning broadcast camera</mark>** 

**Why this is still open:** Recent calibration papers either explicitly place real-time performance out of scope, or degrade under PTZ drift/zoom — no system handles both simultaneously for a single panning camera, badminton’s typical broadcast setup. 

**_Research question:_** _Can a calibration network be both real-time and robust to continuous zoom/pan drift, rather than trading off one for the other as current methods do?_ 

#### **RG8  —  Monocular 3D shuttle-trajectory recovery without a known-geometry scale anchor** 

**Why this is still open:** MonoTrack explicitly calls monocular 3D reconstruction "ill-defined" without stereo cues, and every monocular method found anchors scale via known court/net geometry. 

**_Research question:_** _Could a learned scale prior — from the shuttlecock’s known physical dimensions and apparent size, analogous to monocular depth foundation models — replace the geometric anchor current methods require?_ 

#### **RG9  —  Orientation-dependent, in-flight drag modeling from vision alone** 

**Why this is still open:** Published physics models (Cohen et al., Zhou) still assume a constant drag coefficient per shot, despite acknowledging drag varies with the shuttle’s orientation and tumble state. 

**_Research question:_** _Can a vision-estimated shuttle orientation/tumble state be fused into the physics model in real time to replace the constant-drag-coefficient assumption?_ 

#### **RG10  —  Racket-impact (contact) dynamics** 

**Why this is still open:** Every aerodynamic model found explicitly excludes racket-impact dynamics, modeling only the resulting post-impact trajectory. 

**_Research question:_** _Can the actual racket–shuttle collision — restitution, string-bed deformation, contact angle — be modeled from video, rather than only inferred from what happens after?_ 

#### **RG11  —  Calibrated uncertainty for ball/shuttle trajectories** 

**Why this is still open:** Zero papers found apply Bayesian ensembles or conformal prediction to ball/shuttlecock tracking specifically — the entire conformal-trajectory literature clusters around autonomous vehicles, storms, epidemics, and surgical tools. 

**_Research question:_** _What does a properly calibrated confidence interval look like for a shuttlecock’s estimated 3D position, and can existing conformal-trajectory methods be transplanted directly, or does the shuttle’s aerodynamic instability require a new formulation?_ 

#### **RG12  —  An open, reproducible accuracy-validation protocol for vision-based trajectory systems** 

**Why this is still open:** Hawk-Eye’s widely cited "3.6mm" accuracy figure has never been made methodologically transparent or independently peer-reviewed, per Cardiff University’s public challenge. 

**_Research question:_** _What would a fully transparent, reproducible ground-truth protocol for validating vision-based trajectory accuracy look like, and could it be applied to a badminton system from day one — turning a methodological weakness in the field into a point of rigor for this project?_ 

### **Cluster 4 — Temporal Understanding and Tactics** 

_These gaps sit beneath Contribution Areas B, F, G, and N/O (video understanding, sports analytics, dataset engineering, evaluation) in the Contribution Map._ 

#### **<mark>RG13  —  One validated end-to-end pipeline from raw video to tact</mark> i** **<mark>cal forecast</mark>** 

**Why this is still open:** Every stage (tracking, stroke classification, forecasting) has been solved separately, each assuming clean, often ground-truth, upstream input — ShuttleNet/DyMF assume annotated strokes; BST/TemPose assume known hit frames. 

**_Research question:_** _Does a system built by chaining these existing components together survive the compounding of real (non-ground-truth) upstream errors, and if not, where does it break first?_ 

#### **RG14  —  Domain-transfer of temporal action segmentation to rally/serve boundaries** 

**Why this is still open:** MS-TCN, ASFormer, ActionFormer, and diffusion-based segmenters are validated on cooking/assembly benchmarks (Breakfast, 50Salads, GTEA), never on racket-sport rally or serve boundary detection. 

**_Research question:_** _Do these general-purpose segmentation architectures transfer cleanly to rally/serve/stroke boundary detection in badminton video, or does the sport’s different temporal structure (discrete rallies, no fixed action vocabulary length) require adaptation?_ 

#### **RG15  —  A badminton-native tactical GNN evaluated at TacticAI’s rigor** 

**Why this is still open:** Nothing in badminton matches football’s TacticAI in either modeling sophistication (generative tactic recommendation) or validation rigor (expert-panel evaluation, real-vs-generated indistinguishability testing). **_Research question:_** _Can a badminton-specific tactical GNN be built and validated with the same rigor — real coaches judging generated versus real tactical recommendations — as TacticAI, closing a direct, citable maturity gap between the two sports?_ 

### **Cluster 5 — Language-Grounded and World-Model Reasoning** 

_These gaps sit beneath Contribution Areas H, I, and J (VLMs, long-horizon memory, world models) in the Contribution Map — and directly beneath Part VI’s agentic architecture proposal._ 

#### **<mark>RG16  —  Grounding tactcal language explanat</mark> i i** **<mark>ons in pixel-level evidence</mark>** 

**Why this is still open:** SportR shows even GPT-5 achieves under 7% IoU grounding rule violations to video regions — current VLMs cannot reliably connect a tactical claim to the specific pixels that justify it. 

**_Research question:_** _Can a badminton-specific structured-evidence-to-language grounding approach (evidence objects in, grounded language out, as sketched in the agentic architecture proposal) directly address this documented VLM failure mode?_ 

#### **RG17  —  Multi-hop sports tactical reasoning specific to badminton** 

**Why this is still open:** General sports-intelligence benchmarks put VLMs at 22–31% accuracy versus 96%+ for humans on multi-step tactical questions. 

**_Research question:_** _Does grounding a VLM in badminton-specific structured evidence (shot type, contact geometry, rally history) close this gap, or is the failure more fundamental than a missing-domain-knowledge problem?_ 

#### **RG18  —  A model-based RL / world model for real (non-simulated) racket-sport tactics** 

**Why this is still open:** Every existing sports-RL system (TiZero, Google Research Football agents, the CoachAI badminton environment) is validated only in simulation against modeled opponents. DeepMind’s real-world tabletennis RL solved motor control, not strategy. 

**_Research question:_** _What would it take to close the sim-to-real gap for tactical — not motor-control — decisionmaking in a real rally, and is a badminton rally (discrete, turn-based, bounded court) a more tractable first target than continuous team sports?_ 

#### **<mark>RG19  —  React</mark> i** **<mark>ve, dynamic tactcal modeling beyond Tact</mark> i i** **<mark>cAI’s statc scope</mark> i** 

**Why this is still open:** TacticAI is a single-set-piece (corner kick) recommender that does not model a reactive opponent adjusting in real time, does not quantify uncertainty, and ignores vertical/aerial movement. **_Research question:_** _Can a sequential, rally-length, opponent-adaptive tactical model be built for a sport defined by continuous back-and-forth exchange — structurally harder than TacticAI’s one-shot corner-kick setting?_ 

### **Cluster 6 — Systems and Inference-Orchestration Research** 

_These gaps sit beneath Contribution Areas K, L, and M (RL/adaptive decision-making, research infrastructure, real-time engineering) and directly test the agentic architecture proposed in Part VI of the Contribution Map._ 

**<mark>RG20  —  Validat</mark> i** **<mark>ng uncertainty-triggered orchestraton for a chain of specialized agents</mark> i** 

**Why this is still open:** Early-exit networks, mixture-of-experts routing, and cascades are well-established for classification and LLM question-answering, but none of the sources found validate this pattern for a pipeline of interacting perception/geometry/tactics agents over a continuous rally. 

**_Research question:_** _Does confidence calibration remain reliable when errors can compound across a chain of specialized agents rather than a single model — and if not, what does a calibration method for multi-agent pipelines look like?_ 

#### **RG21  —  Per-instance, not just marginal, uncertainty guarantees for a live sports pipeline** 

**Why this is still open:** Standard conformal prediction guarantees only average-case coverage — a specific rally’s trajectory estimate can still be confidently wrong even when the method is well-calibrated on average. **_Research question:_** _Can per-instance or conditional conformal methods be adapted to a live tracking-plus-tactics pipeline where wrong-but-confident estimates on a single rally matter more than average-case guarantees?_ 

**Part IV — How This Connects Back to the Contribution Map** 

The six clusters above map directly onto the seventeen extended contribution areas as follows, so the two documents read as one continuous argument rather than two separate lists: 

- Clusters 1–2 (perception & fusion limits) deepen Areas A, B, and C — shuttlecock tracking, video understanding, and player/pose tracking. 

- Cluster 3 (geometry & physics) deepens Areas D and E — court geometry and physics-informed trajectory intelligence — and is the single richest, most self-contained research vein in this entire map. 

- Cluster 4 (temporal understanding & tactics) deepens Areas F, G, N, and O — sports analytics, tactical intelligence, dataset engineering, and evaluation/validation. 

- Cluster 5 (language & world-model reasoning) deepens Areas H, I, and J — vision-language models, longhorizon memory, and world models — and directly stress-tests the agentic architecture proposed in Part VI of the Contribution Map. 

- Cluster 6 (systems & orchestration) deepens Areas K, L, and M — reinforcement learning, research infrastructure, and real-time engineering — and is the empirical validation this project’s uncertaintytriggered agentic design would need before it could be called a research contribution rather than an engineering pattern. 

Read together, the two documents give a defensible three-part pitch: (1) here is exactly what I understand about the existing system and the literature around it, with sources; (2) here is exactly what remains unsolved in that same literature, also with sources; (3) here is where my specific background points at closing one or more of those gaps rather than re-implementing what already exists. 

