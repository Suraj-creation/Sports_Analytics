# Racket evidence and four-player identity recovery — 31 October 2026

This follow-up starts at `03641c3` on local `main`. It implements executable racket evidence, reviewed four-player identity, per-person travel, pair positions and named doubles service order. It does **not** establish real-video accuracy, pretrained-model performance or physical collision ground truth. The original local-only restriction remains in force: no SSH, remote jobs, model/data/browser downloads, dependency installation or environment replacement.

## Recovery and architecture decisions

The existing `PersistentPlayerAssociator`, local-only OSNet loader, `ParticipantTracker`, `IdentityReviewLedger`, canonical individual-shot fold and measured court-path fold were recovered into a connected workflow. No usable RacketVision architecture or racket checkpoint exists in this checkout, its inspected history or the preserved legacy copies; profile references alone were not treated as implementations. The new racket stage uses already installed OpenCV and actual image edges.

The pipeline remains:

```text
BGR frame + current detected person + observed wrist pose
  -> local ellipse/shaft detector -> optional observed racket geometry
  -> camera stabilization -> exact-frame participant/named observation series
  -> temporal shuttle/body/pose/racket fusion -> estimated contact/stroke events
  -> racket Parquet rows + versioned diagnostic observations
  -> REST/WebSocket track windows -> exact-frame labelled geometry overlay

Optional pinned local OSNet -> bounded neural/motion visual identities
  -> explicit roster person / track-episode interval review
  -> separate hitter-only review -> canonical official individual shot totals
  -> exact reviewed track intervals + validated camera + existing path gates
  -> per-person travel and pair front/back/side-by-side position measurements

Explicit named server/receiver setup + team-to-score-slot mapping
  -> canonical point transition replay -> named doubles service order
```

### Racket observation and contact semantics

`perception/racket.py:RacketDetector.detect` searches near confident, uniquely detected, currently posed wrists. An observation requires a sufficiently complete fitted ellipse **and actual shaft edge support** between the ellipse and wrist. A wrist, body box, shaft alone, isolated ellipse, low-confidence person, duplicate track ID, carried detector output or ambiguous owner cannot manufacture a racket observation. Coordinates return in original analysis-image pixels. Degenerate contour fits are rejected.

`RacketObservation` records ellipse center, diameters, angle, geometric support, wrist index and method `opencv_ellipse_shaft_v1`. Camera transforms map the ellipse along with the shuttle and body. The method is conservative and untrained: blur, occlusion, an edge-on racket, court-line clutter or a missing pose can defeat it. Geometric support is not a calibrated probability.

The explicit profile choice is `racket_geometry_v1` with `opencv-cpu`. It never opens a model registry path. Unsupported neural choices degrade explicitly; no checkpoint architecture is guessed. CPU and GPU profiles now select the executable geometric stage. `contact_fusion_v2` adds observed racket overlap to existing temporal/body/pose support. Two overlapping rackets remain ambiguous even if their centers have unequal distances. Missing racket observations preserve the existing body/motion estimate and never become observed equipment through interpolation.

Events retain `contact_status=estimated` and `racket_contact_observed=false`. New fields `racket_overlap_observed` and `racket_evidence_method` distinguish image-supported overlap. A two-dimensional overlap plus a shuttle redirect is evidence for contact, not proof of a physical collision. Racket rows persist independently as `TrackObject.RACKET`, reach both REST and WebSocket windows and render as labelled geometric bounds. They are never held into missing frames. Diagnostic codec **12** and the profile/runtime/identity fingerprints invalidate incompatible observations; diagnostic caches still cannot restore private tracker state.

### Four-player identities, motion and pair measurements

GPU doubles profiles now request the existing pinned `osnet_ain_x0_25` loader with FP32 and explicit Torch CUDA. Loading remains `fetch=False`; missing weights disable that neural stage with its existing reason. CPU development keeps neural re-identification optional. No neural checkpoint was loaded in this recovery.

The associator accepts explicit bounded retention. Production doubles profiles use eight seconds; the backwards-compatible constructor default stays one second. Dormant matches require distinctive neural evidence, including comparison against competitors below the absolute similarity cutoff. A recycled raw tracker ID cannot establish a dormant identity. Ambiguous descriptors, missing trusted galleries and reset/cut boundaries withhold associations. Galleries stay private, bounded and in memory; saved results do not need them to reopen.

Names are not guessed from side, colour or track number. The existing append-only identity ledger now has dedicated GET/POST/DELETE endpoints. Reviews require completed saved analysis, a current revision, an existing roster participant, exact episode birth evidence and a finite interval. Simultaneous one-to-many/many-to-one assignments, track reuse, exits, epoch changes and stale revisions are rejected. A roster edit re-reads the current session under the same repository snapshot lock so a stale request cannot reassign a reviewed person.

Hitter review is separate from identity review and shot-family/contact verification. It references the current machine stroke, unchanged original episode evidence and a valid identity interval. Revocation and ordinary shot-label corrections refold correctly. The API resolves canonical stroke ancestry for the UI's existing-review/revoke state, so a corrected shot cannot hide its hitter review. Generic event verification cannot edit identity or service setup evidence.

The browser's Visual track observations panel supports all four roster people, exact interval entry, hitter confirmation and revocation. Overlay labels use the same birth/track/interval and reset restrictions; unlinked people retain anonymous labels. Generic event actor IDs now support roster identities without turning an unknown ID into “Player 2.” Score-side slots remain P1/P2.

`analytics/reviewed_motion.py` derives named paths from exact reviewed observation IDs and track IDs, explicitly official rallies, validated main-camera rows and the existing `court_path_v2` continuity, speed and jitter rules. It never joins review intervals or fills missing positions. Public output includes distance, travel heading/speed, latest sample frame and observed/expected frame counts. Pair output requires two reviewed teammates on the same court side in a frame. Front/back means at least 0.5 m difference in distance to the net; side-by-side is the remaining observed positional configuration. These are position measurements, not inferred tactical responsibility or facing direction.

### Doubles partner service order

`rules/doubles.py` models four distinct named members and each team's right-court occupant. A serving team winning a rally swaps its members' service courts and retains the same server. A receiving team winning chooses its next server from its new score parity and current member positions; the receiving pair does not swap solely because the opponent scored.

The dedicated `/doubles-service` API requires explicit opposing server/receiver selection and a roster mapping each two-person team to a P1/P2 score slot. Frame zero without an existing score anchor explicitly represents an opening selection at 0–0. Mid-game/later-game selection requires recorded score evidence. Canonical point states take priority over potentially stale snapshots; point winners and before/after transitions must form a coherent chain. The service anchor binds its score-history prefix, roster members and analysis revision. Changed history, incomplete transitions, reanalysis, or a new game with no new selection yields **unknown**.

The pair tab exposes service setup at frame zero or a selected/current frame. It queries again when the relevant point/setup changes, rather than requesting a replay on every rendered video frame. It does not infer who physically served or received from team score slots.

## Defects found and repaired during this follow-up

| Area / function | Defect or disconnected capability | Repair and evidence |
|---|---|---|
| `perception/racket.py` | Configured racket specialist had no executable local implementation. | Actual ellipse/shaft/wrist image processing; rendered-image positives at multiple scales/angles and negative/missing/ambiguous-owner cases. |
| Observation/engine/codec boundaries | No equipment observation survived camera stabilization, temporal windows or persistence. | Optional typed geometry, camera transform, codec 12, exact-frame series and independent racket Parquet rows. Round-trip and transform regressions. |
| `contact.score_frame` | Only wrist/box proximity supported a hit; adjacent real equipment evidence was unavailable. | Explicit image-overlap support; missing geometry stays missing; multiple overlaps abstain. |
| Contact attribution | Initial implementation used unequal center distance to pick between two overlapping rackets. | Independent review reproduced the error; explicit `ambiguous_racket_overlap` branch. |
| `PersistentPlayerAssociator.update` | One-second expiry prevented bounded longer returns; reused raw IDs could otherwise impersonate dormant people. | Configurable retention, distinctive neural-only dormant recovery, four-person raw-ID swap and expiry/reset tests. |
| Dormant identity margin | A .89 competitor disappeared before a .91 candidate's margin comparison. | Independent review regression; all relevant retained galleries participate in distinctiveness checks. |
| `identity_reviews` API / panel | Existing finite review ledger and canonical four-person counts were unreachable through the product. | Dedicated revision-guarded endpoints, four-person form, separate hitter confirmation/revocation and real API/SQLite tests. |
| Review lineage | Corrected shot retained credit while losing its UI revoke action. | Canonical current stroke ID in review responses; API and UI correction/revocation regressions. |
| Overlay identity boundaries | Same-frame conflicting births, changed epoch markers and older overlapping reset intervals differed from ledger semantics. | Match the backend's birth-time/sequence/epoch rules; failing regressions for false names and incorrectly withheld names, followed by focused rendering tests. |
| `update_roster` | A stale session dependency could remove the actual reviewed person's team association. | Re-read and guard roster changes under the repository snapshot lock; reproduced before repair. |
| Reviewed movement | Four roster people had no named measured travel or pair positions. | Reuse existing measured-path gates over exact review intervals; expose time/heading/coverage and pair position summaries. |
| Official-rally gate | Legacy missing-flag fallback could credit named motion while individual shots remained excluded. | Explicit `payload.official is True` event-ID set, matching the shot fold; regression from 46 expected frames to zero. |
| Doubles service rules | Only team score slots existed; partner rotation was absent. | Pure four-person service state, explicit setup, canonical point replay, prefix invalidation and UI controls. |
| Service seed | A stale snapshot supplied 0–0 despite a canonical 1–0 point state. | Canonical state wins; full point-transition validation rejects an inconsistent chain. Failing regression followed by repair. |
| Later-game service UI | Initial form always submitted frame zero. | Setup-frame input/current-frame action and recorded-score submission. |
| Wire / browser buffers | Racket rows were omitted from store publication, REST and WS reads; malformed bounds could reach canvas. | Include racket data throughout; exact-frame replacement/clear semantics, finite and positive bounds validation. |
| Capability/configuration assertions | Earlier tests enforced retired reviews and disabled GPU identity even after these capabilities were deliberately restored. | Update contract assertions while retaining rejection of legacy aliases, stale/unscoped writes and historical-data mutation. |

## Validation evidence and limits

Logs and original-work backups are in ignored `.kilo/contact-identity-20261031/`. Tests use the existing `docs/testing/validate_local.py` source-checkout runner and the compatible packages already available through the earlier cached-paths file. No dependency or model was installed. Private user session stores were not opened or reanalysed.

The image tests execute real OpenCV on rendered images. Neural identity tests use controlled 512-dimensional descriptors to test assignment policies; they are not OSNet accuracy measurements. Temporal/codec tests use controlled observations. API tests use actual temporary SQLite/Parquet and the real application routes/folds.

The browser test server has a controlled review-observation fixture installed only by `apps/web/e2e/server.py`; no fixture endpoint is registered by the production `create_app`. The browser workflow uploads a real generated clip, then exercises four reviewed people, scoped hitter credit/revocation, measured pair output, racket wire delivery and service setup against real HTTP/persistence. Fixture observations are labelled `controlled_browser_fixture` and are not model detections or evidence of real-video accuracy.

### Final results

| Check | Executed command / scope | Result | Log in `.kilo/contact-identity-20261031/` |
|---|---|---|---|
| Broad backend / research | `python -u docs/testing/validate_local.py --paths-file .kilo/recovery-20261031/cached-paths.json test -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests -m "not gpu and not slow and not network" --tb=short -o faulthandler_timeout=90` | **1,105 passed, 3 skipped**, 283.18 s; zero failures | `backend-final.txt` |
| Additional equipment partitions | Same runner, `test -q sports/badminton/tests/test_racket_pipeline.py -k partition --tb=short` | **5 passed**, 6 deselected, 4.05 s | `racket-partitions-verified.txt` |
| Frontend | From `apps/web`: `node_modules/.bin/vitest.cmd run` | **34 files, 120 passed**, 73.59 s | `web-verified.txt` |
| Browser | Installed Edge, `PW_CHANNEL=msedge`, `BAI_E2E_PORT=8769`, unset `CI`; `node_modules/.bin/playwright.cmd test --reporter=list` | **7 passed**, 2.6 min | `browser-verified.txt` |
| TypeScript | From `apps/web`: `node_modules/.bin/tsc.cmd -b --noEmit` | Passed | `typecheck-verified.txt` |
| Production build | From `apps/web`: `node_modules/.bin/vite.cmd build` | Passed, 11.76 s | `build-verified.txt` |
| Python syntax | `python docs/testing/validate_local.py static` | **238 files**, zero errors | `static-final.txt` |
| Python lint / format | `ruff check` and `ruff format --check` on the explicit task Python file list | All checks passed; **34 files** already formatted | `ruff-verified.txt`, `ruff-format-verified.txt` |
| Frontend lint / format | `biome check --config-path=biome.json` on the explicit 21 task TS/TSX files | Zero errors; five existing warnings | `biome-verified.txt` |
| Patch / preservation | `git diff --check`, staged diff review, protected binary diff comparison | Passed; original protected diff remains byte-identical | Original patch and `protected-current.patch` |

The five partition cases were added after the broad backend run and executed separately against the same production Python source. They test complete-versus-partitioned contact frames, actors and equipment component evidence at partition sizes 1, 7, 16, 32 and 64. They are **not included in the 1,105** broad-run count. Together these are 1,110 distinct passing backend checks; no duplicated focused reruns are added to that total.

The three skips are real RF-DETR/RTMPose adapters requiring absent `rtmlib` and the real RapidOCR reader requiring absent `rapidocr`. Controlled adapter tests are separate evidence. GPU/slow/network-marked tests were intentionally excluded, not counted as passed. The broad suite retained 14 non-fatal warnings for the existing deprecated HTTP 422 constant name. Biome's five existing warnings concern the general event payload `any` type and older roster-test non-null assertions. Vite retains the existing Settings static/dynamic import warning. This report does not claim a warning-free repository.

The first broad run had 1,097 passes and three failures enforcing the former disabled/retired capability policy. Assertions now check the intentionally restored routes and pinned GPU identity request, while still rejecting old aliases and unversioned historical writes. Early draft fixture errors (required event provenance and enum-valued repository updates) were corrected before establishing the missing-route failures. Browser exact-label selection initially failed because wrapped select labels include option text; direct DOM inspection showed label match count zero and accessible-combobox match count one. Role-based selectors preserved all workflow assertions and the original timeout. Final browser checks also wait for visible review/analytics convergence after revocation.

Independent read-only review found the multiple-racket, dormant-margin, corrected-review, official-motion and later-game service-control issues. All received targeted regressions and repairs; follow-up review found no remaining blocker in the changed source. Further parent inspection aligned same-frame/epoch/older-boundary overlay behavior with the ledger. Desktop workflow screenshots were inspected. The owned temporary browser server was stopped; production data and unrelated processes were untouched.

## Remaining external validation

1. Labelled representative video is still required to measure racket recall/false positives, contact timing/precision/recall, hitter attribution and player ID switches. In particular test blur, edge-on rackets, clutter, overlap, missed poses and low shuttle visibility. Physical collision truth cannot be established from synthetic ellipse overlap.
2. Real OSNet and other pretrained weights remain unavailable locally. Load only already pinned server artifacts in the unchanged GPU environment later; compare appearance behavior through crossings and occlusions. Identical or uninformative appearance remains unresolved. Names require an explicit person association; camera cuts and expired episodes require new bounded reviews.
3. Actual CUDA/TensorRT/Pascal execution and performance remain unverified. The new classical stage intentionally runs on CPU. No server environment was changed or contacted.
4. Live stroke families remain heuristic; the previously recovered BST path remains explicit singles shadow evaluation. RacketVision, general live ingestion, second-opinion shuttle models and full VFR source-PTS traceability still lack the required local implementation/artifacts/evaluation and are not represented as restored trained capabilities.
5. Pair position measurements depend on valid calibration and reviewed intervals. They do not establish tactical responsibility. Named service order depends on correct human setup and accepted point evidence; missing setup and ambiguous/changed evidence remain unknown.

These are evidential or separate research-capability limits. The connected local contact/identity/review/movement/service paths are tested separately from those claims.
