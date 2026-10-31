# Contact and four-player recovery implementation plan

**Goal:** Connect real image-based racket evidence and usable four-player identity workflows locally, preserving uncertainty and existing saved work.

**Architecture:** Extend current PersonObs and temporal series with optional observed racket geometry. Reuse OpenCV contours, ellipse fitting and wrist/shaft evidence; never manufacture racket points from a wrist or missing detector. Feed that evidence through existing contact scoring, persisted racket tracks and codec. Reuse the existing neural/motion associator with configurable bounded retention, and reconnect the scoped identity ledger to four-person roster analytics through dedicated review endpoints and UI. Roster names remain explicitly associated; a raw track number never proves a name.

**Constraints:** Current main checkout; preserve initial Design deletions, web dependency edits and unrelated directories. No remote access, dependency/model/data downloads, installs or real-session reanalysis. Existing source-only validation runner and cached packages only. No claim that synthetic tests establish real-video accuracy.

## Tasks

- [x] Preserve starting state and inspect existing code/history/artifacts. Record absent RacketVision architecture/weights; do not invent its checkpoint interface.
- [x] Test first: actual synthetic image racket localization, wrist-only/blank/ambiguous rejection, scale/rotation/ROI and invalid inputs. Implement explicit OpenCV racket stage, optional observation contract, cache version/fingerprint and persisted tracks.
- [x] Test first: racket-supported contact versus trajectory/body-only estimate; owner ambiguity, missing/held evidence, chunk equivalence. Wire temporal fusion and evidence through current engine and APIs.
- [x] Test first: four distinct neural identities through longer gaps, swapped raw IDs, ambiguous galleries, stale/reset limits and missing descriptors. Extend existing associator only through explicit bounded policy/configuration.
- [x] Reconnect existing finite-interval identity ledger and scoped shot review for all four roster people. Test authorization/validation, simultaneous one-to-one mappings, revoked/superseded evidence, reanalysis revisions and coherent persistence reads. Expose the dedicated workflow in the current visual-observation panel.
- [x] Inspect downstream doubles service state, exports, movement, runtime metadata and unsupported-stage contracts; fix demonstrated remaining defects with targeted regressions.
- [x] Run focused red/green suites, then full offline backend/research, frontend, typecheck/build and meaningful browser coverage. Obtain independent review, address findings and document exact limits.
- [ ] Verify original work byte-for-byte, commit only task files on main, and deliver report with implemented capabilities and remaining external validation.
