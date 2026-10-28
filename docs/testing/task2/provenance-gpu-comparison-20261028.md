# GPU doubles diagnostic comparison, 2026-10-28

The same 250-frame, 25-fps doubles clip (SHA-256 `e50e00223bf41468ac4c913ff5a7647d909563326d256be8037fe79fedace640`) was analysed independently by the earlier release and this change on GPU 1. Both completed all frames and produced 17 contact candidates and 16 stroke candidates. The earlier release assigned one stroke unknown; the current version assigned six unknown. These are output counts, not accuracy measurements. They do not demonstrate four-person identity coverage.

The AI-only, non-exhaustive `annotations/doubles-ai-motion-draft.json` was drafted before examining model outputs. Both runs have stroke candidates at frames 22 and 36, within its two possible visual swing windows (frames 20–28 and 32–40). The shuttle contact, shot family and durable hitter identity are not confirmed. Window overlap must not be presented as precision, recall or classification accuracy.

The earlier run took 28.33 seconds and sampled 2,122 MiB of GPU memory; the current run took 31.35 seconds and sampled 2,128 MiB. Wall times include upload, media preparation, model loading, inference, polling and API reads; the later run overlapped the backend test suite. These are not controlled speed measurements, and sampled GPU memory may miss peaks.

The current run adds frame-level detector provenance, limits doubles candidate truncation and abstains from some shot context where player evidence is carried or unknown. A detector-run flag means the detector ran on the frame, not that a particular tracked player was successfully matched.
