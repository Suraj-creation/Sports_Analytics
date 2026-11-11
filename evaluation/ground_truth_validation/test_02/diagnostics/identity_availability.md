# Test 2 identity availability: missing artifact, available adapter, unresolved names

Read-only inspection on2026-11-11 of the genuine completed fresh **29,296-frame** Test2 baseline, current registry/profile/adapter code and retained Test1 identity findings. No model download, checkpoint load, cache/lock/profile/source change or inference was performed for this report. The reviewed perception/adapter/plugin files still match their hashes in the fresh Test2 protocol plan.

## What was configured and what actually ran

The executed `experimental-pipeline-repair-v1` profile requests `player_reid.model=osnet_ain_x0_25`, backend **torch-cuda**, precision **fp32**, retention **8seconds**. It is a configured optional stage, not evidence that a neural ReID model loaded. `models/manifest.yaml` declares the exact candidate checkpoint and pinned SHA256 `ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347`.

The baseline's immutable `run/inference.json` records exactly:

| Recorded stage | Recorded reason | Interpretation |
|---|---|---|
| player_identity | `osnet_ain_x0_25: osnet_ain_x0_25 is not downloaded; run ` + `` `bai models fetch osnet_ain_x0_25` `` | Specific local-artifact lookup failure |
| player_reid | `baseline player_reid provider is unavailable` | Generic component-factory consequence of the preceding loader returning no model |

These are **two reporting layers for the same failed construction**, not evidence of two independent missing implementations. The model-staging receipt lists OSNet as `missing_artifact_or_existing_pin`; there is no player-ReID runtime/backend entry. The expected local `models/cache/osnet_ain_x0_25/osnet_ain_x0_25.pt` is absent. The first and last actual cache segments,0–59 and29280–29295, retain `player_identity={state:disabled,model:null,policy:bytetrack_v1,court_membership:observed_box_continuity_v1,requested_model:osnet_ain_x0_25}`. Tracking still executed; neural appearance association did not.

The current configured model/backend/precision **pass the adapter's explicit compatibility checks**. This run failed at the absent file; it did not reach a CUDA initialization or model-forward test. Do not call the configured Torch-CUDA provider unsupported, or claim that merely placing the file guarantees successful inference.

## Exact code path and format caveat

1. `perception/pipeline.py` constructs the ReID component for initial **unknown/doubles** format, or for an explicit `profile.components["player_reid"]` override on singles. The Test2 cache starts with unknown format and later records inferred singles; this explains why this nominal singles video attempted the optional loader.
2. `_load_reid` accepts the pinned model, FP32 and explicit `torch-cpu`/`torch-cuda`. It calls `registry.path(model,fetch=False)`. `engine/runtime/registry.py::ModelRegistry.path` raises the observed missing-artifact error instead of downloading it.
3. On success, the existing `offline_reid.py::OSNetAppearanceEmbedder` independently verifies the exact checkpoint digest before loading its vendored Torch architecture. It takes current bounded BGR image crops, converts to RGB128×256 and returns finite normalized512-dimensional descriptors. It explicitly makes no named-identity claim.
4. The baseline component factory raises its generic provider-unavailable exception when the loader returns `None`. `players.py` consequently has no `PersistentPlayerAssociator`; it retains ByteTrack episode IDs and observed-box court membership. With ReID available, motion/appearance association can maintain a separate canonical visual namespace. Descriptors stay private; they are not authoritative roster evidence.

**Reporting inconsistency to preserve for later review:** `plugin.py::capabilities` currently changes a nonloaded identity stage to `disabled` with a doubles-only explanation whenever the *current* format is not doubles. That public explanation is narrower than the actual loader/provider contract: the provider advertises singles/doubles/unknown, unknown acquisition attempts loading, and an explicit component override can enable singles. Therefore distinguish the authoritative recorded missing-file reason from this generic public format label. It does not establish that the provider lacks an implementation or that current Test2 named identities would become verified if the label were changed. No reporting code was modified here.

## What enabling OSNet could and could not resolve

It could provide a new appearance cue for short-lived track association after occlusion, crossing or raw tracker-ID changes. Crop/model/device failures still have explicit degradation, and the associator retains ambiguity rather than forcing a match. This requires a **separate fresh-perception experiment** with new cache identity and before/after validation; it cannot be silently injected into the current engine-only racket fix or called an unchanged baseline.

It would **not** supply reviewed roster names, PlayerA/B meaning, scoreboard row binding, side-change/game segmentation, team membership, physical hitter confirmation, or verified rally winners. The engine intentionally starts ambiguous; participant episode IDs never automatically become durable roster IDs. A good embedding cannot identify which symbolic annotation label denotes an athlete without a reviewed mapping. The source panels show actual changes of ends and detection-slot swaps, so fixed near/far or slot-index binding is invalid here.

Retain Test1's already implemented **one vote per independent score transition** fix. Repeating OCR/reconciliation calls must not manufacture identity corroboration. Test1's correct source scoreboard acquisition and unknown names were not repaired by falsifying score observations; that conclusion carries forward without reopening the resolved vote defect.

The completed Test2 live ledger contains **75 rally-end events, all with null winners;819 contact events with zero named contact actors;48 identity-ambiguity events**. These are observed output/abstention counts, **not**0% independently measured winner/identity accuracy. They also do not prove OSNet absence is the sole cause: unknown roster/row/point association and physical contact evidence remain separate prerequisites. Ledger SHA256: `655cafec807fbc0b7c65b79a6e600a47f1d06922630b456ef835fb3c50892000`.

## Checkpoint and licence evidence

The publisher's current [LibreReID-osnet model card](https://huggingface.co/LibreYOLO/LibreReID-osnet) lists `osnet_ain_x0_25.pt` with the same exact pinned digest. It declares **MIT for the converted weights**, identifies unchanged conversion from Torchreid multi-source checkpoints, and names **MSMT17, DukeMTMC-reID and CUHK03** as training datasets with research-oriented terms. This is a publisher declaration, not an independent adjudication of all training-data rights. The [current file listing](https://huggingface.co/LibreYOLO/LibreReID-osnet/tree/main) confirms artifact availability; no file was downloaded.

**Code:** upstream [Torchreid licence](https://github.com/KaiyangZhou/deep-person-reid/blob/master/LICENSE) is MIT, with notices to preserve. **Exact checkpoint:** publisher declares MIT and a hash matching the local pin. **Datasets/footage:** their separate terms remain distinct; no blanket permission is inferred from the model/code licence. The local vendored adapter does not require replacing the whole tracker with the model host's external DeepOCSORT stack.

## Evaluation/regression prerequisites

- Keep this one-variable racket-admission experiment's perceptions, model cache/lock, profile and immutable source outputs unchanged. Any subsequent ReID arm needs a separate authorized artifact acquisition/pin receipt and fresh inference; do not retcon appearance descriptors into the current caches.
- Reuse existing regression suites for local-only/checksum/device/precision loading, canonical namespace on inference failure, observed-versus-propagated crop selection, actor provenance and initial unbound singles identity: `test_player_reid_configuration.py`, `test_offline_reid_review.py`, `test_player_association*.py`, `test_unbound_initial_singles_identity.py`, `test_identity_review_ledger.py`, `test_score_mapping_vote_provenance.py`. Their existence is not a claim that this documentation task reran them or loaded real OSNet weights.
- Validate real crop/preprocessing/output parity, bounded person batches, FP32 CUDA compatibility and actual latency/VRAM without replacing the managed Pascal environment. For singles, explicitly record initial unknown versus configured singles and any component override. For doubles, include four players, similar uniforms, teammate crossings, occlusion and team/name uncertainty; generic provider capacity does not certify doubles identity accuracy.
- Part2 Test2 supplies only generated, swapping two-point player slots—**no independently reviewed persistent IDs/boxes/visibility**. Therefore IDF1/HOTA/true ID-switch or fragmentation accuracy is unavailable. Build a separate source-bound review set with identities, visibility, cuts, roster/team/score-row mappings and game changes before claiming accuracy improvement. Anonymous continuity, rejected/ambiguous assignments and named-output coverage can be reported now with their actual denominators.

Inspection receipts: baseline `inference.json` SHA256 `bf3943868f22053c622deb3724b9511b0bbbc16eaadc43187c649da680b3d299`; unchanged source profile SHA256 `280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756`; source model manifest SHA256 `b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3`; source model lock SHA256 `fb3b69b8ff3224d6f7b647c68acb08ec4ed4ffec6c67e3acf6f08da485ff9966`. The worker's staged model-pin receipt is a separate isolated staging artifact; its serialization digest must not be confused with the protected source lock file.
