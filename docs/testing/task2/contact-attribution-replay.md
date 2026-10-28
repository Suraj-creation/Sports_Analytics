# Contact-attribution replay (semantic diagnostic)

The cache replay was run in fresh temporary stores against archived `3cc74e2` and the working tree after the low-proximity and tied-swing safeguards, before later tracker-evidence protection imports. Inputs and media hashes are recorded in `contact-replay-before.json` and `contact-replay-after.json`; no original event database was modified and no fresh GPU inference was run. Both runs used the same current replay harness and omitted historical human corrections.

| Source session | Before contacts / unattributed | After contacts / unattributed | After reason |
|---|---:|---:|---|
| 01M55MFY9GQF6ZXP2SQPQ8X1KG | 2 / 0 | 2 / 0 | nearest_proximity: 2 |
| 01M55NQMRAS0ATB73XE3XA6S74 | 236 / 236 | 236 / 236 | no_player_observation: 236 |
| 01M56T2EED5Z7W9VTGG19FHNTF | 202 / 202 | 202 / 202 | no_player_observation: 202 |
| 01M5EXGZNEVGYAJ3AR6CJS5ZG9 | 272 / 272 | 272 / 272 | no_player_observation: 272 |
| 01M5MBR3087FH07N5B1XR5VGHW | 0 / 0 | 0 / 0 | none |

The replayed working tree used contact.py SHA-256 `9db0c068d9b0b61506e075511ce48c182c54532d9358ccdbfb4420449ee34efc`, engine.py SHA-256 `6c3166e597a6322d6e68a1c7ea993386173bdda12d346dff6f2cd18236c26cdd`, and replay harness SHA-256 `997ea881a84e893e08fd65d15ee11352e9dc77eae4916b52a5f4ac059ed97588`; hashes were unchanged before and after the run. The after summary is an exact copy of that isolated replay summary. The subsequent tracker-evidence guard changes have not been replayed; they do not alter contact scoring during this replay. Source media hashes, cached-observation hashes, frame counts, and fps match the archived baseline for each session. The final replay did not exercise the new competing-player near-tie or insufficient-proximity policy and does not establish its accuracy. The current branch conservatively latches identity ambiguity after tracker resets or multi-person evidence; the replay deliberately excludes historical human corrections. Consequently those 710 unattributed contacts expose limited identity evidence, not a ground-truth measurement of hitter accuracy. The near-tie and minimum-proximity thresholds are uncalibrated heuristics; even a supported non-tied proximity is not proof of a hitter. Contact and stroke hypotheses, official event ownership, and actual play must be evaluated separately with independent labels.

The following counts are before/after in each cell. For every session, canonical contact, stroke, rally-end and point records also have equal multisets of `(frame_start, frame_end, player_id)` between runs; that comparison does not assert equality of event payloads or correctness.

| Source session | Rallies | Points | Strokes |
|---|---:|---:|---:|
| 01M55MFY9GQF6ZXP2SQPQ8X1KG | 1 / 1 | 0 / 0 | 2 / 2 |
| 01M55NQMRAS0ATB73XE3XA6S74 | 25 / 25 | 0 / 0 | 235 / 235 |
| 01M56T2EED5Z7W9VTGG19FHNTF | 27 / 27 | 0 / 0 | 202 / 202 |
| 01M5EXGZNEVGYAJ3AR6CJS5ZG9 | 65 / 65 | 0 / 0 | 272 / 272 |
| 01M5MBR3087FH07N5B1XR5VGHW | 0 / 0 | 0 / 0 | 0 / 0 |

Comparisons to earlier `d932684` counts have different match-phase and identity policies. The newer default requires explicit match evidence; it is inappropriate to interpret the reduced official/point count as a change in detector accuracy.
