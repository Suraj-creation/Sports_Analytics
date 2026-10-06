# **Contribution Map** 

Computer Vision & Vision-Language Models for Sports Analytics — Badminton _From TrackNetV3 to an Uncertainty-Aware, Agentic Sports Intelligence System_ 

Prepared for: 6-Month Internship Application — Badminton Analytics Project 

Prepared by: Shuva 

September 2026 

_This document consolidates the three original contribution areas from the internship letter with an expanded map of seventeen additional contribution areas, an experience-to-project mapping, and a proposed uncertainty-aware agentic architecture for evolving the project beyond shuttlecock tracking into a full sports-intelligence system._ 

**Table of Contents** 

**Part I — Foundational Contribution Areas (From the Application Letter)** 

These are the three contribution areas already articulated in the internship letter. They remain the foundation on which every additional area below is built. 

### **1. Research-Oriented Computer Vision & Multimodal Intelligence** 

- Temporal understanding of badminton videos. 

- Shuttle trajectory and player/action tracking. 

- Shot recognition and pose understanding. 

- Vision-language reasoning. 

- Long-horizon memory and world-model-like representations. 

- Connecting vision to richer intelligent systems. 

### **2. Real-Time Intelligent Product & Analytics** 

- Turn vision outputs into structured sports data. 

- Build analytical and intelligence layers around the pipeline. 

- Generate actionable coaching intelligence. 

- Analyze positioning, footwork, reaction time, shot selection and rally patterns. 

- Build real-time and post-match experiences. 

**3. Deep Experimentation, Automated Research & Reinforcement Learning** 

- Experiment with architectures, representations and objectives. 

- Build research harnesses and automated evaluation. 

- Explore AutoML and hyperparameter optimization. 

- Investigate temporal modeling, multimodal architectures and RL. 

- Explore simulated badminton environments and reward-driven tactical optimization. 

**Part II — Extended Contribution Areas (A–Q)** 

These seventeen areas expand the three foundational themes into the complete research-and-engineering stack around TrackNetV3 and a full badminton analytics system. Together with Part I they cover 182 distinct, numbered contribution items. 

### **A. Specialized Shuttlecock Tracking Research** 

_Directly related to TrackNetV3_ 

This is the most direct way to contribute to the existing project. TrackNetV3 is designed for shuttlecock trajectory prediction and rectification. You could work on improving its reliability and extending its capabilities. 

#### **_What you can contribute_** 

- 1. Improve shuttlecock detection accuracy. 

- 2. Improve trajectory prediction across consecutive frames. 

- 3. Handle shuttlecock occlusion and missing detections. 

- 4. Improve performance under motion blur. 

- 5. Experiment with different CNN architectures. 

- 6. Compare TrackNetV3 against modern detection and tracking baselines. 

- 7. Improve trajectory rectification and missing-segment recovery. 

- 8. Explore better data augmentation. 

- 9. Improve robustness across different courts and camera angles. 

- 10. Build error analysis tools for tracking failures. 

#### **_Research questions_** 

- Can temporal information improve shuttle localization? 

- Can a better architecture handle tiny shuttlecock appearances? 

- Can background modeling improve performance? 

- Can we reconstruct missing trajectory segments more reliably? 

- Can we make the model work better in real-world match videos? 

Why this fits you: You already have ML and AI research experience. This would be an opportunity to apply those skills to a specialized computer vision problem. 

### **B. Advanced Video Understanding** 

This is broader than simply tracking the shuttle. 

#### **_What you can contribute_** 

- 11. Temporal action recognition. 

- 12. Shot boundary detection. 

- 13. Rally segmentation. 

- 14. Recognition of badminton strokes. 

- 15. Player-action understanding. 

- 16. Understanding the relationship between player movement and shuttle movement. 

- 17. Learning temporal representations of a rally. 

- 18. Exploring CNN + LSTM, temporal convolutional networks and video transformers. 

- 19. Investigating multimodal video understanding. 

- 20. Developing models that understand an entire rally rather than individual frames. 

#### **_Example_** 

Instead of: "Frame 1: shuttle at position A." You want: "Player A performed a clear. The shuttle traveled to the backcourt. Player B moved backward and returned with a drop shot." This is a much richer form of temporal understanding. 

### **C. Player Tracking and Pose Estimation** 

TrackNetV3 primarily solves the shuttle tracking problem. A complete badminton analytics system also needs to understand the players. 

#### **_What you can contribute_** 

- 21. Player detection. 

- 22. Multi-player tracking. 

- 23. Player identity association across frames. 

- 24. Human pose estimation. 

- 25. Racket and body-part tracking. 

- 26. Footwork analysis. 

- 27. Court positioning analysis. 

- 28. Recovery movement analysis. 

- 29. Reaction and movement timing. 

- 30. Player-shuttle interaction modeling. 

#### **_Research opportunity_** 

Can we combine shuttle trajectory, player pose, player position, racket movement, and temporal context to improve shot recognition and player performance analysis? This would be an important multimodal computer vision contribution. 

### **D. Court Geometry and Spatial Intelligence** 

This is an entirely separate but important contribution area. A camera sees a 2D image. The actual badminton court is a 3D physical environment. 

#### **_What you can contribute_** 

- 31. Court line detection. 

- 32. Court corner detection. 

- 33. Camera calibration. 

- 34. Homography estimation. 

- 35. Mapping image coordinates to court coordinates. 

- 36. Real-world player distance estimation. 

- 37. Shuttle landing position estimation. 

- 38. Court coverage analysis. 

- 39. Shot placement and court zone analysis. 

- 40. Spatial representations of the court. 

#### **_Example_** 

Instead of: "Player moved 120 pixels." You want: "Player moved approximately 2 meters toward the backhand corner." This makes the output much more useful for sports analytics. 

### **E. Physics-Informed Modeling and Trajectory Intelligence** 

This is an exciting research direction that combines computer vision, mathematics and physical reasoning. 

#### **_What you can contribute_** 

- 41. Shuttle velocity estimation. 

- 42. Acceleration and direction-change analysis. 

- 43. Shuttle flight-time estimation. 

- 44. Trajectory prediction. 

- 45. Physics-inspired trajectory correction. 

- 46. Modeling shuttle aerodynamic effects. 

- 47. Studying racket impact and shuttle response. 

- 48. Combining learned models with physical constraints. 

- 49. Estimating uncertainty in trajectory predictions. 

- 50. Exploring learned dynamics models. 

#### **_Research question_** 

Can a model that combines visual observations with physical constraints produce a more accurate shuttle trajectory? This could become a meaningful research contribution, especially if you design rigorous experiments. 

### **F. Sports Analytics and Statistical Intelligence** 

This is where your Data Science background can contribute significantly. 

#### **_What you can contribute_** 

- 51. Rally-level analytics. 

- 52. Shot distribution analysis. 

- 53. Shot placement statistics. 

- 54. Winning and losing pattern analysis. 

- 55. Player movement statistics. 

- 56. Court coverage metrics. 

- 57. Rally duration analysis. 

- 58. Shot success and error analysis. 

- 59. Opponent response analysis. 

- 60. Performance trends across matches. 

- 61. Statistical comparison between players. 

- 62. Data-driven tactical insights. 

#### **_Example_** 

You could analyze: "How often does a player lose points after being pushed into the backhand corner?" Or: "Does a particular shot combination correlate with winning rallies?" These are analytics questions, not just computer vision questions. 

### **G. Tactical Intelligence and Decision Support** 

This is where the system begins to move from analytics toward intelligence. 

#### **_What you can contribute_** 

- 63. Tactical pattern recognition. 

- 64. Shot selection analysis. 

- 65. Opponent response modeling. 

- 66. Identifying weaknesses in positioning. 

- 67. Analyzing recovery after shots. 

- 68. Identifying repeated rally patterns. 

- 69. Evaluating whether a shot created a tactical advantage. 

- 70. Generating evidence-based recommendations. 

- 71. Personalized coaching feedback. 

- 72. Tactical scenario analysis. 

#### **_Example_** 

Instead of: "You played 5 backhand shots." You want: "When the opponent played a deep clear to your backhand corner, your recovery position was consistently late. This limited your options for the next shot." The system would need reliable evidence from perception and analytics before making that recommendation. 

### **H. Vision-Language Models and Multimodal Reasoning** 

This is directly connected to your broader AI interests. 

#### **_What you can contribute_** 

- 73. Explore video-language models for badminton understanding. 

- 74. Connect structured sports data with language models. 

- 75. Build natural-language explanations of rally events. 

- 76. Generate match summaries. 

- 77. Create question-answering over badminton videos. 

- 78. Build a vision-language coaching assistant. 

- 79. Ground language-model insights in actual detected events. 

- 80. Explore multimodal representations of player performance. 

- 81. Compare direct VLM reasoning with structured analytics pipelines. 

#### **_Example_** 

User asks: "Why did I lose this rally?" The system should combine video, shuttle trajectory, player movement, shot events, court position, and rally outcome, then generate a grounded explanation. This is much more interesting than asking an LLM to guess from a video. 

### **I. Long-Horizon Memory and Player State Modeling** 

This is one of your strongest distinctive research interests. A normal analytics system might analyze one match. A richer system could remember the player’s history. 

#### **_What you can contribute_** 

- 82. Persistent player profiles. 

- 83. Long-term performance memory. 

- 84. Match-to-match comparison. 

- 85. Tracking recurring weaknesses. 

- 86. Tracking improvements over time. 

- 87. Memory of opponent tendencies. 

- 88. Retrieval of similar past rallies. 

- 89. Uncertainty-aware player state estimation. 

#### • 90. Longitudinal coaching intelligence. 

#### **_Example_** 

After analyzing 20 matches, the system might identify: "Your recovery after attacking shots has improved over the last month, but your performance against deep backhand clears remains inconsistent." This would require reliable data, consistent player identity and careful statistical validation. 

#### **_Connection to your research_** 

This is closer to your interest in cognitive systems that build knowledge over time. But it is important to start with a well-defined sports analytics memory system rather than immediately calling it a world model. 

### **J. World Models and Learned Game Dynamics** 

This is a more advanced research direction. 

#### **_What you can contribute_** 

- 91. Learn representations of badminton court state. 

- 92. Model player and shuttle dynamics. 

- 93. Predict possible future rally states. 

- 94. Study opponent-response patterns. 

- 95. Explore learned action-state representations. 

- 96. Build a simulated badminton environment. 

- 97. Investigate predictive world models. 

- 98. Explore counterfactual rally analysis. 

- 99. Predict the consequences of alternative shots. 

- 100. Connect learned dynamics to decision-making. 

#### **_Example_** 

"If the player had returned cross-court instead of straight, what might have happened?" This is a counterfactual question. It cannot be answered reliably by merely looking at the current trajectory — you need a model of the game dynamics, player capabilities and uncertainty. 

### **K. Reinforcement Learning and Adaptive Decision-Making** 

You already mentioned reinforcement learning, but it deserves a separate contribution area because it connects to a different research problem. 

#### **_What you can contribute_** 

- 101. RL for tactical recommendation. 

- 102. RL for shot selection in simulation. 

- 103. Reward design for badminton strategy. 

- 104. Opponent modeling. 

- 105. Self-play environments. 

- 106. Learning policies for court positioning. 

- 107. Simulated rally optimization. 

- 108. Evaluating action sequences. 

- 109. Adaptive inference policies. 

- 110. Decision-making under uncertainty. 

#### **_Two possible directions_** 

- 1. RL for analytics infrastructure — an agent learns when to process frames, increase resolution, or select a more expensive model. 

- 2. RL for badminton strategy — an agent learns which shot or movement to choose in a simulated game environment. 

The second is much closer to your long-term ambition, but it requires a reliable simulator or environment and a sufficiently accurate state representation. 

### **L. Research Infrastructure and Automated Experimentation** 

This is another strong contribution given your engineering experience. 

#### **_What you can contribute_** 

- 111. Automated training pipelines. 

- 112. Dataset versioning. 

- 113. Experiment tracking. 

- 114. Hyperparameter sweeps. 

- 115. Model comparison. 

- 116. Evaluation automation. 

- 117. Error analysis dashboards. 

- 118. Checkpoint management. 

- 119. Reproducible experiments. 

- 120. Research documentation. 

- 121. Automated visualization of trajectory predictions. 

- 122. Benchmark creation. 

- 123. AI-assisted research workflows. 

#### **_Example_** 

You could build a system where the team changes model architecture, sequence length, augmentation strategy, background mode, or learning rate — and the system automatically trains, evaluates, compares and reports the results. That would make you useful not only as a model developer but as someone who improves the research process itself. 

### **M. Real-Time AI Systems and Production Engineering** 

This is directly connected to your work at DSeT Consultancy and your previous AI engineering experience. 

#### **_What you can contribute_** 

- 124. Real-time video ingestion. 

- 125. GPU inference optimization. 

- 126. Frame buffering and pipeline design. 

- 127. Model serving. 

- 128. Backend APIs. 

- 129. WebSocket-based live updates. 

- 130. Structured event generation. 

- 131. Data serialization. 

- 132. Monitoring and observability. 

- 133. Latency optimization. 

- 134. Memory and compute optimization. 

- 135. Deployment and reproducibility. 

- 136. Reliability testing. 

**_Example — a live pipeline_** 

Camera ↓ Video ingestion ↓ TrackNetV3 ↓ Player tracking ↓ Pose estimation ↓ Temporal events ↓ Analytics ↓ Live dashboard 

The engineering challenge is to make this work consistently, not just in a notebook. 

### **N. Dataset Engineering and Annotation** 

This is often overlooked, but it is essential for computer vision research. 

#### **_What you can contribute_** 

- 137. Dataset preparation. 

- 138. Video preprocessing. 

- 139. Frame extraction. 

- 140. Shuttle annotation. 

- 141. Player annotation. 

- 142. Shot-event annotation. 

- 143. Rally segmentation labels. 

- 144. Dataset quality checks. 

- 145. Train/validation/test split design. 

- 146. Dataset balancing. 

- 147. Synthetic data generation. 

- 148. Hard-example mining. 

- 149. Data augmentation. 

- 150. Benchmark dataset construction. 

#### **_Why this matters_** 

A better model is not always the solution. Sometimes the problem is bad labels, missing frames, incorrect annotations, data leakage, too little variation, or poor evaluation design. Your Data Science and research experience can help here. 

### **O. Model Evaluation, Reliability and Scientific Validation** 

This is particularly important if you want to contribute as a researcher rather than only as an implementer. 

#### **_What you can contribute_** 

- 151. Define evaluation metrics. 

- 152. Build reproducible benchmarks. 

- 153. Analyze failure cases. 

- 154. Evaluate across different camera setups. 

- 155. Measure robustness to blur and occlusion. 

- 156. Perform ablation studies. 

- 157. Compare model components. 

- 158. Quantify uncertainty. 

- 159. Test generalization to unseen matches. 

- 160. Validate whether analytics are actually useful. 

- 161. Compare automated insights with human expert judgment. 

- 162. Study the reliability of coaching recommendations. 

#### **_Example_** 

If a model claims a player was late to recover, you need to establish: how was recovery time calculated? Is the player identity correct? Is the court calibrated? Was the relevant shot detected? Is the conclusion supported by the data? This is how you avoid building a system that generates impressive but unreliable insights. 

### **P. Badminton Simulation and Synthetic Environments** 

This is a longer-term research contribution. 

#### **_What you can contribute_** 

- 163. Design a badminton simulation environment. 

- 164. Generate synthetic shuttle trajectories. 

- 165. Simulate player movement. 

- 166. Create synthetic training examples. 

- 167. Test trajectory prediction models. 

- 168. Study physics-informed learning. 

- 169. Build RL training environments. 

- 170. Explore self-play. 

- 171. Evaluate tactical decisions in simulation. 

- 172. Investigate sim-to-real transfer. 

This would be a strong direction if the project wants to explore reinforcement learning or world models. 

### **Q. Product Design and User Experience** 

Your product-development experience can also be valuable. 

#### **_What you can contribute_** 

- 173. Design a badminton analytics dashboard. 

- 174. Build trajectory visualization. 

- 175. Build replay and event timelines. 

- 176. Create player performance reports. 

- 177. Design coach-facing interfaces. 

- 178. Build natural-language analytics interaction. 

- 179. Make model uncertainty visible. 

- 180. Design actionable feedback rather than overwhelming statistics. 

- 181. Improve real-time user experience. 

- 182. Create a useful bridge between research outputs and players. 

#### **_Example_** 

A player should be able to watch a rally, see the shuttle path, inspect their movement, and understand what to improve — not just look at a screen full of numbers. 

**Part III — Experience Mapped to These Contributions** 

How existing background connects to the project: 

|**Experience**|**How It Can Help**|
|---|---|
|**AI Systems & Platform**<br>**Engineering**|Build reliable inference and analytics infrastructure.|
|**Pharma Intelligence Platform**|Structured data, deterministic analytics, retrieval and reasoning.|
|**SevenHills Mining Platform**|End-to-end systems, data flows and automation.|
|**ZenArk AI Engineer**|Behavioral signals, longitudinal state, memory and structured<br>insights.|
|**Hybrid RAG and agentic**<br>**orchestration**|Grounded multimodal analytics and insight generation.|
|**NLP research**|Temporal event descriptions, language-grounded reasoning and<br>VLM research.|
|**Data Science**|Evaluation, statistical analysis and experiment design.|
|**Reinforcement Learning**<br>**coursework**|Future tactical decision-making and simulation.|
|**Cortex Lab / The Inevitable**|Research thinking around memory, cognitive architectures and<br>intelligent systems.|
|**Python, FastAPI, AI**<br>**infrastructure**|Build the surrounding engineering system.|



The important point is that these are transferable skills. They do not mean every sports computer vision problem has already been mastered — they mean the underlying engineering and research habits carry over directly. 

## **Part IV — The Complete Contribution Map** 

Combining Parts I–III, the overall contribution space organizes into six layers: 

Badminton Analytics Research — Overall Contribution Perception        → Shuttle, players, pose, court Temporal          → Shots, rallies, movement Analytics         → Metrics, tactics, performance Intelligence      → Memory, reasoning, recommendations Research          → Experiments, evaluation, novel models Engineering → Real-time, deployment, infrastructure 

**Part V — What to Actually Present as the Contribution** 

A broad vision is good for research, but an internship application should communicate focus. Rather than listing all 182 possibilities, the contribution is organized into six major themes: 

|**Theme**|**Description**|
|---|---|
|**1. Computer Vision & Shuttle**<br>**Tracking**|Improve TrackNetV3, explore temporal models, trajectory<br>prediction, occlusion handling and vision perception.|
|**2. Multimodal Video**<br>**Understanding**|Combine shuttle trajectory, player tracking, pose, court geometry<br>and video-language reasoning.|
|**3. Sports Analytics & Tactical**<br>**Intelligence**|Transform observations into rally analysis, performance metrics,<br>tactical patterns and actionable coaching insights.|
|**4. Research & Experimentation**|Automated research harnesses, benchmarking, evaluation, model<br>optimization, ablations and novel architecture experiments.|
|**5. Intelligent Systems &**<br>**Longitudinal Learning**|Persistent player state, memory, world-model-like representations,<br>prediction and decision-making.|
|**6. Real-Time AI Product**<br>**Engineering**|Inference pipelines, structured data, APIs, visualization,<br>deployment and reliable production systems.|



### **Recommendation** 

The strongest differentiator is not simply knowing AI, Python, or RAG — it is wanting to connect perception, temporal understanding, structured knowledge, reasoning, decision-making, and learning over time into a single coherent system. That is the deeper contribution story. 

For a six-month internship, the priority order should be: 

- 1. TrackNetV3 and computer vision fundamentals. 

- 2. Player tracking, pose, and temporal event understanding. 

- 3. Reliable sports analytics and evaluation. 

- 4. Research experimentation and real-time engineering. 

- 5. Advanced memory, VLMs, world models, and RL — as research directions once the foundation is solid. 

## **Part VI — Proposed Architecture: An Uncertainty-Aware, Agentic Sports Intelligence System** 

The project can evolve from a shuttlecock tracking pipeline into an agentic, multi-layer sports intelligence system. This section lays out how — and, just as importantly, where agents should and should not be used. 

The project can evolve from a shuttlecock tracking pipeline into an agentic, multi-layer sports intelligence system — but the key is to place agents correctly. Agents should not replace deterministic computer vision. They should orchestrate, validate, refine, and interpret the outputs of computer vision models. An LLM agent should not be responsible for estimating every pixel-level coordinate or angle directly — that would be slow, expensive, and less reliable than geometric vision models. Instead, use a layered architecture where fast perception models produce measurements, and specialized agents decide what to inspect, refine, calculate, or explain. 

### **1. The Central Idea** 

Raw Match Video ↓ Fast Perception Layer ↓ Geometric Reconstruction Layer ↓ Temporal Understanding Layer ↓ Agentic Verification and Refinement Layer ↓ Badminton Intelligence Layer ↓ Prediction and Coaching Layer 

The important distinction is: 

- Computer Vision = measure what happened. 

- Geometry / Physics = estimate how it happened. 

- Agents = decide what needs deeper analysis. 

- Intelligence = understand why it happened. 

- Prediction = estimate what happens next. 

### **2. Where the Agentic Layer Should Exist** 

Do not put one giant agent around the entire TrackNetV3 pipeline. Instead, create a hierarchical orchestration system with multiple specialized agents: 

Orchestrator Agent (task planning + routing) ├─ Perception Refinement Agent  → Shuttle / Racket Validation ├─ Geometry Agent               → Angle / Speed / Trajectory └─ Temporal Understanding Agent → Stroke / Rally / Event Analysis ↓ Sports Intelligence Agent 

↓ Prediction + Coaching 

The orchestrator does not continuously ask an LLM what to do for every video frame — it operates at eventlevel or uncertainty-level, not necessarily at 30–60 FPS. 

### **3. Real-Time Loop vs. Agentic Loop** 

The system should be separated into two loops. 

#### **_A. Real-time perception loop_** 

This must be extremely fast and deterministic: 

Frame → Shuttle detection → Player detection → Racket/keypoint detection → Court calibration → Tracking → State estimation → Short-horizon prediction 

This loop may run at 25–60 FPS depending on hardware and model complexity. It should use: TrackNetV3 or an improved successor, a player detector, a racket detector or pose model, a court-line detector, a Kalman or particle filter, optical flow where useful, temporal smoothing, geometric calculations, and lightweight predictive models. 

#### **_B. Agentic intelligence loop_** 

This runs only when useful: 

Uncertainty detected → Agent selects additional analysis → Specialist model is invoked → Evidence is cross-checked → State is corrected → Insight is generated 

It may run after every stroke, at rally boundaries, when the shuttle disappears, when the trajectory is physically inconsistent, when two models disagree, when a tactical pattern emerges, or when the user asks a question. This separation is essential for both speed and accuracy. 

### **4. The Exact Angle-Estimation Idea** 

Estimating the angle relative to the ground, the racket point, the shuttlecock point, and the motion direction is a combination of camera calibration, court geometry, 3D (or pseudo-3D) reconstruction, racket and shuttle localization, trajectory estimation, impact-point estimation, and physics-informed inference. 

Instead of simply saying "the player hit a smash," the system should estimate: 

- Where the player was standing. 

- Where the racket was at contact. 

- Where the shuttle was at contact. 

- What the racket-head direction was. 

- What the shuttle’s incoming direction was. 

- What the outgoing direction was. 

- What the elevation angle was. 

- What the horizontal angle was. 

- What the estimated speed was. 

- How far above the floor contact occurred. 

- Whether the contact point was in front of or behind the player. 

- Whether the player was balanced. 

- Whether the shot was cross-court or straight. 

- Whether the shot was likely attacking, defensive, deceptive, or forced. 

That is much deeper than ordinary object tracking. 

### **5. Geometry Agent: The Core of This Idea** 

The Geometry Agent is responsible for constructing a consistent spatial coordinate system. 

#### **_Inputs_** 

- Court-line detections and court corners. 

- Camera parameters. 

- Player foot positions. 

- Shuttle coordinates. 

- Racket keypoints. 

- Net position. 

- Camera viewpoint. 

- Known badminton court dimensions. 

#### **_Outputs (illustrative schema)_** 

{ "court_coordinate": [x, y], "player_position": [x, y], "shuttle_position": [x, y, z_estimated], "racket_contact_point": [x, y, z_estimated], "shuttle_direction": [dx, dy, dz], "racket_direction": [rx, ry, rz], "elevation_angle": 38.4, "horizontal_angle": 17.8, "contact_height": 2.41, "confidence": 0.81 <u>}</u> 

These numbers would be estimates, not absolute truth, unless the system has enough camera information for reliable 3D reconstruction. 

### **6. Important Limitation: A Single Camera Cannot Fully Recover True 3D** 

If the input is a single broadcast video, the system usually observes only 2D image coordinates (u, v), but the goal is (x, y, z). The missing depth dimension creates ambiguity — a shuttle appearing at a given pixel location might be near the camera and high, far from the camera and lower, or at a different physical position with a similar image projection. Therefore a "true angle" cannot always be recovered from one camera without additional assumptions. Five possible solutions, in increasing order of practicality for a single-camera broadcast setup: 

- Option 1 — Court homography: map image coordinates to the court plane. Useful for player position, footwork, court coverage, landing zones, and horizontal shot direction, but does not fully recover shuttle height on its own. 

- Option 2 — Multi-view cameras: use two or more synchronized cameras and triangulate a Camera-A observation with a Camera-B observation to recover a true 3D shuttle position. This is the strongest route for accurate angle and trajectory estimation, but it requires multi-camera infrastructure. 

- Option 3 — Monocular depth estimation: use a depth model to estimate relative depth. Useful in principle, but potentially unreliable for a tiny, fast shuttlecock. 

- Option 4 — Physics-informed estimation: combine the 2D shuttle trajectory, court geometry, known shuttle flight constraints, gravity, drag approximation, the player/racket contact point, and temporal motion to infer the most plausible trajectory. 

- Option 5 — Hybrid camera-plus-physics model: 2D observations + court calibration + player/racket geometry + physical constraints + temporal filtering = an estimated 3D trajectory. This is likely the most practical research direction, and could be a substantial contribution beyond simply integrating an agent framework. 

### **7. Racket–Shuttle Interaction Analysis** 

A particularly valuable module would be a Contact Event Agent, whose job is to detect and analyze the moment of impact by combining the shuttle trajectory, racket-head location, wrist/elbow/shoulder pose, player movement, frame-to-frame velocity, an audio spike if available, direction change, and temporal proximity. 

#### **_Contact detection logic_** 

A likely hit event occurs when the shuttle approaches the racket, the racket and shuttle become spatially close, the shuttle changes direction or velocity, and the player’s pose indicates a stroke. The agent could then calculate the estimated contact frame, contact point, contact height, racket orientation, incoming shuttle direction, outgoing shuttle direction, estimated launch angle, estimated shot type, and a confidence score. 

This would allow analysis such as: "The player contacted the shuttle slightly behind the optimal body position, producing a lower and more defensive trajectory." That is a much more meaningful coaching insight than a bare shot label. 

### **8. Agents as Evidence Evaluators** 

Instead of allowing an agent to freely hallucinate coordinates, every agent should operate on a structured evidence object. For example, an input evidence record: 

{ "event_id": "rally_12_stroke_07", "frame_range": [1240, 1268], 

"shuttle_track": { "points": [], "visibility": [], "confidence": 0.74 }, 

"racket_track": { "points": [], "confidence": 0.68 }, 

"player_pose": { "keypoints": [], "confidence": 0.91 }, 

"court_geometry": { "homography": {}, "confidence": 0.96 }, 

"candidate_contact_frames": [1256, 1257, 1258] <u>}</u> 

The agent then returns a structured verdict: 

{ "selected_contact_frame": 1257, "estimated_shot_type": "overhead_attack", "estimated_launch_angle": 36.2, "estimated_direction": "cross_court", "confidence": 0.79, "uncertainties": [ "shuttle depth is underdetermined", "racket head partially occluded" ], "recommended_next_action": "run_high_resolution_racket_refinement" <u>}</u> 

This is the correct pattern: models produce evidence, and agents evaluate evidence and choose the next computation. 

### **9. Potential Specialized Agents** 

#### **_1. Shuttle Tracking Agent_** 

Responsibilities: validate TrackNetV3 output, detect missed shuttle frames, identify false positives, request high-resolution reprocessing, compare multiple tracking models, apply temporal consistency, and estimate uncertainty. Possible models: TrackNetV3, a YOLO-based detector, a small transformer detector, an opticalflow-assisted tracker, and a Kalman filter. 

#### **_2. Racket Detection Agent_** 

Responsibilities: detect the racket, track the racket head, estimate shaft direction, identify racket orientation, and refine the contact frame. The racket is often difficult because of motion blur, small size, occlusion, similarity to court lines, and fast movement. 

#### **_3. Player Pose Agent_** 

Responsibilities: estimate body keypoints, detect foot placement, analyze trunk rotation, estimate arm extension, measure preparation and recovery, and identify balance and posture. 

#### **_4. Court Geometry Agent_** 

Responsibilities: detect court lines, estimate homography, determine player side, map image coordinates to court coordinates, estimate shuttle landing zone, and correct camera perspective. 

#### **_5. Contact Event Agent_** 

Responsibilities: detect likely racket–shuttle contact, resolve the exact contact frame, estimate contact height, calculate direction changes, and classify stroke candidates. 

#### **_6. Trajectory Physics Agent_** 

Responsibilities: fit a physically plausible trajectory, estimate velocity and acceleration, detect impossible tracking points, estimate launch and landing, infer hidden shuttle positions, and produce uncertainty bounds. This agent could combine neural prediction with physics constraints. 

#### **_7. Temporal Rally Agent_** 

Responsibilities: segment rallies, detect serves, identify strokes, detect transitions, recognize rally phases, and track attack/defense changes. 

#### **_8. Tactical Intelligence Agent_** 

Responsibilities: analyze shot selection, detect repeated patterns, identify weaknesses, compare player positioning, evaluate recovery time, and generate tactical hypotheses. 

#### **_9. Prediction Agent_** 

Responsibilities: predict shuttle landing region, predict next shot type, predict opponent response, estimate rally continuation, predict player movement, and estimate likely winning zones. 

#### **_10. Research Agent_** 

Responsibilities: identify uncertain cases, select difficult clips, create experiment batches, compare model variants, generate ablation plans, analyze errors, and suggest new hypotheses. This is where agentic orchestration becomes especially powerful for the research contribution. 

### **10. The "Uncertainty-Triggered Computation" Idea** 

This may be the most precise and defensible agentic angle: instead of running every expensive module all the time, if confidence is high the system continues with the fast pipeline; if confidence is low, it invokes specialist agents. 

For example, with TrackNet confidence 0.96, court confidence 0.98, and racket confidence 0.92, the system accepts the result. But with TrackNet confidence 0.51, racket confidence 0.42, and a physically inconsistent trajectory, it triggers a refinement workflow that can: 

- 1. Reprocess frames at higher resolution. 

- 2. Run another shuttle detector. 

- 3. Run optical flow. 

- 4. Inspect neighboring frames. 

- 5. Use court geometry. 

- 6. Fit a trajectory. 

- 7. Compare candidate results. 

- 8. Select the most consistent estimate. 

- 9. Store the corrected track. 

This gives better accuracy, lower average compute, better real-time performance, explainable refinement, and a measurable research problem. A good name for this direction could be "Uncertainty-Aware Agentic Perception and Trajectory Refinement." 

### **11. Context-Based Orchestration** 

The orchestrator could maintain a structured Rally Context State, for example: 

{ "match_id": "match_001", "rally_id": 12, "current_player": "player_A", "opponent": "player_B", "last_shot": "clear", "current_phase": "defensive_transition", "shuttle_visibility": 0.62, "racket_visibility": 0.48, "player_balance": 0.71, "court_position": "rear_right", "uncertainty": "high", "recent_pattern": "repeated_cross_court_clear", "available_agents": [ "trajectory_refinement", "racket_contact", "tactical_analysis" ] <u>}</u> 

The orchestrator uses this context to choose what to do next — for example, if shuttle confidence is low, a stroke may have occurred, and racket confidence is low, then it invokes the Contact Event Agent, the Racket Refinement Agent, and the Trajectory Physics Agent. This is better than blindly invoking every agent on every frame. 

### **12. Agentic Orchestration Should Be Hierarchical** 

A strong design has three levels. 

#### **_Level 1 — Frame-level perception_** 

Fast models only: a shuttle detector, a player detector, a pose estimator, a racket detector, and a court detector. No LLM required. 

#### **_Level 2 — Event-level specialist agents_** 

Triggered by events: contact detection, stroke classification, trajectory refinement, occlusion recovery, geometry correction, and rally segmentation. These can use learned models, algorithms, and small decision policies. 

#### **_Level 3 — Match-level intelligence agent_** 

Runs over longer context: tactical patterns, player weaknesses, strategy, match momentum, longitudinal player development, coaching recommendations, and natural-language explanations. An LLM or VLM is most useful at this level, grounded in structured evidence. 

### **13. Where VLMs Fit** 

A VLM can help with describing a rally, interpreting player posture, explaining tactical sequences, answering natural-language questions, comparing two rallies, generating coaching reports, and identifying visually 

meaningful events. But a VLM should not be the sole authority for exact shuttle coordinates, exact launch angles, precise velocity, pixel-level tracking, or reliable contact timing — for those, use specialized CV and geometry models. 

The VLM should receive structured evidence, for example: 

{ "shot_type": "smash", "contact_height": 2.35, "launch_angle": 28.4, "speed_estimate": 62.1, "landing_zone": "deep_backhand_corner", "player_recovery_time": 0.84, "confidence": 0.78 <u>}</u> 

and then produce: "The player used a steep attacking shot toward the opponent’s backhand corner, but recovery was delayed, leaving the center exposed." That is grounded multimodal reasoning. 

### **14. Real-Time Prediction** 

Several predictive layers can be added: 

- A. Shuttle trajectory prediction — the next 100–300 ms of motion, landing zone, whether the shuttle is going in/out, expected height, and approximate arrival time. 

- B. Player movement prediction — next footwork direction, recovery position, likely interception point, and time to shuttle. 

- C. Stroke prediction — before contact, estimate smash, clear, drop, drive, lift, net shot, serve, or block. 

- D. Tactical prediction — likely opponent response, open court area, high-probability next shot, whether the player is under pressure, and whether a player is preparing an attack. 

The predictive system could be structured as: 

Current state → Short-horizon motion prediction → Candidate future states → Tactical scoring → Likely next action 

### **15. A Possible Formal Research Contribution** 

This could be framed as: "Agentic Multimodal Perception and Physics-Grounded Intelligence for Badminton Analytics," or more specifically: "Uncertainty-Aware Agentic Orchestration for Fine-Grained Badminton Motion Understanding." 

The research question could be: can an uncertainty-aware agentic orchestration layer improve the accuracy, efficiency, and interpretability of badminton motion analysis by dynamically selecting specialized perception, geometric, temporal, and physics-based modules? This is much stronger than simply saying "we will add agents to TrackNetV3." 

### **16. Research Hypotheses** 

- H1 — Accuracy: an agentic refinement layer improves shuttle tracking accuracy under occlusion, motion blur, small-object conditions, camera movement, and fast rallies. 

- H2 — Efficiency: conditional invocation of expensive modules reduces average computation compared with running all models continuously. 

- H3 — Geometry: court-calibrated and physics-constrained trajectory estimation improves angle and landing estimates compared with raw 2D tracking. 

- H4 — Contact detection: combining shuttle, racket, pose, and temporal evidence improves stroke/contact detection compared with shuttle tracking alone. 

- H5 — Tactical insight: structured evidence plus an agentic reasoning layer produces more accurate and explainable tactical analysis than a generic VLM observing raw video. 

### **17. How to Evaluate It** 

To avoid making "deeper intelligence" purely subjective, measure each layer separately. 

#### **_Perception metrics_** 

Precision, recall, F1, MOTA/HOTA for tracking, position error, missed-frame rate, and ID switches. 

#### **_Geometry metrics_** 

Court calibration error, pixel-to-court coordinate error, contact-point error, angle error, landing-location error, and height estimation error. 

#### **_Temporal metrics_** 

Stroke classification accuracy, contact-frame error, rally segmentation F1, and event detection latency. 

#### **_Prediction metrics_** 

Landing-zone accuracy, ADE/FDE for trajectory prediction, next-shot accuracy, and player movement prediction error. 

#### **_Agentic metrics_** 

Accuracy improvement after refinement, percentage of cases requiring escalation, average latency, compute cost, number of unnecessary agent calls, calibration of confidence, and recovery from missing or contradictory evidence. 

#### **_Intelligence metrics_** 

Tactical recommendation accuracy, expert agreement, explanation faithfulness, coaching usefulness, and longitudinal improvement tracking. 

### **18. A Practical Implementation Path** 

Do not build the entire multi-agent system at once. A phased path: 

- Phase 1 — Strong deterministic foundation: TrackNetV3 + court calibration + player tracking + racket detection + pose estimation + temporal smoothing, producing structured event data. 

- Phase 2 — Contact and trajectory intelligence: a contact-event detector, trajectory fitting, angle estimation, landing prediction, and uncertainty estimation. This is probably the best first research milestone. 

- Phase 3 — Agentic refinement: an orchestrator, uncertainty triggers, specialist routing, multi-model verification, and retry/refinement logic. 

- Phase 4 — Tactical intelligence: rally understanding, shot classification, player state, tactical patterns, and prediction. 

- Phase 5 — VLM and coaching layer: structured evidence, VLM reasoning, natural-language analytics, and personalized coaching. 

- Phase 6 — Longitudinal intelligence: player memory, historical comparison, recurring-weakness detection, and adaptive recommendations. 

### **19. The Strongest Angle for the Internship Proposal** 

The contribution can be presented as six connected layers: 

- 1. Fine-Grained Perception — improve shuttlecock, racket, player, and court detection. 

- 2. Geometric and Physics-Grounded Reconstruction — estimate court-relative position, racket–shuttle contact, motion direction, launch angle, trajectory, landing point, and uncertainty. 

- 3. Temporal Event Understanding — recognize serves, strokes, rallies, contact moments, attack/defense transitions, and recovery phases. 

- 4. Uncertainty-Aware Agentic Orchestration — dynamically decide which model to invoke, when to refine, when to reprocess frames, when models disagree, and when confidence is insufficient. 

- 5. Predictive Sports Intelligence — predict shuttle trajectory, landing region, player movement, next shot, and tactical response. 

- 6. Grounded Multimodal Coaching Intelligence — convert structured evidence into tactical explanations, player reports, natural-language Q&A, and long-term development insights. 

### **20. The Key Principle** 

The deepest version of this idea is not simply "add agents to TrackNetV3." It is: build an uncertainty-aware, hierarchical intelligence system in which specialized vision, geometry, temporal, physics, and reasoning modules collaborate to reconstruct and understand badminton actions at progressively deeper levels. The final system could move through this chain: 

Where is the shuttle? ↓ Where is it moving? ↓ Where is the racket? ↓ When did contact happen? ↓ What was the true court-relative motion? ↓ What shot was played? ↓ Why was that shot played? ↓ What will happen next? 

↓ What should the player do differently? 

That is a genuinely ambitious and coherent research direction. 

One important caution: the agentic layer can improve system-level accuracy and efficiency, but it cannot automatically overcome missing visual information. For "true" 3D angles and contact geometry, the project will need calibrated cameras, multi-view data, strong assumptions, or physics-based estimation with explicit uncertainty. 

