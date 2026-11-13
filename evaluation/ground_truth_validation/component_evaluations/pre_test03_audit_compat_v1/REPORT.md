# Test2 completed neural run: audit incompatibility diagnosis

The original neural worker and parent both completed all29,296 frames. The outer analysis failure is reproducible at frame355: the original structural audit requires a strong raw hypothesis for every epoch increment, while the actual producer supports a separate, positively corroborated weak acquisition. No inference rerun is required to diagnose this incompatibility.

The unchanged native2418 strict completion loader passed. All489 catalogue packets passed the actual native `BadmintonSession.decode_perception()` validator. The source-plan files and consumed inputs were rehashed before/after diagnosis; original worker, parent, cache, predictions and failed outer analysis receipts were not changed. No annotations, evaluation metrics or models were loaded by this probe.

A diagnosis-local version-aware epoch check accepts actual native-validated weak positive barriers and rejects weak unknown/no-barrier/missing authority. It passes all saved Test2 frames. The original audit also passes the preserved17,268-frame Test1 strong-reset control; that control verifies retained catalogue bytes and does not claim the deleted/original Test1 video was revalidated here.

| Structural control | Result |
|---|---|
| Actual Test2 original guard | RED: `content epoch reset lacks raw source hypothesis`, frame355 |
| Actual Test2 native decoder + proposed structural epoch rule | GREEN,29,296frames489packets |
| Missing mandatory decision | Rejected by native decoder |
| New proof downgraded to codec22 | Rejected by native decoder |
| Unknown weak decision at actual reset | Rejected by proposed epoch check |
| No-barrier weak decision | Rejected by native decoder |
| Forged raw acquisition cohort | Rejected by native decoder |
| Forged current calibrated polygon | Rejected by native decoder |
| Forged relative camera transform | Rejected by native decoder |
| Unconfirmed source format | Rejected by native decoder |
| Preserved Test1 original structural audit | PASS,17,268frames |

Actual weak barrier frames are **355, 699, 1095, 3394, 4581, 5958, 11691, 11985, 25521**. Strong raw-hypothesis barrier frames are 1829, 2451, 2679, 3866, 4257, 5174, 5505, 6151, 6307, 7012, 8772, 10230, 10366, 11346, 11860, 12298, 12602, 13081, 14107, 14294, 14890, 17242, 17663, 17992, 18370, 20910, 22946, 23697, 24391, 25208, 26058, 26503, 27664, 28707, 28978. Weak-proof validity is not physical scene-edit accuracy; all new/lost barriers require subsequent source visual review. In particular,699/1095/3394/4581/11691/11985 must not silently be accepted as true cuts.

The independent adjacent-camera audit checked251 relative claims, including4 across packet boundaries (frames1620, 7140, 7800, 7860). The serialized previous camera equals the actual adjacent recorded camera, and relative-transform arithmetic agrees. Any source-format context transition flags remain diagnostic ordering questions until reviewed in the eventual full report.

Use a new, explicitly versioned postprocessing adapter with separate producer/tool roots. Keep the native loader/decoder and numeric helper implementations unchanged. Preserve the failed outer receipt and write a separate postprocessing-recovery receipt; do not rewrite metadata or patch imported ROOT. The exact proposed dependency boundary and structural rule are in [PROPOSAL.md](PROPOSAL.md).

Evidence: [diagnostic receipt and all bound input hashes](diagnostic_receipt.json), [actual probe log](probe.log), [diagnosis-local script](probe_completed_nn.py). This report is a diagnosis, not completed evaluation or pipeline acceptance.
