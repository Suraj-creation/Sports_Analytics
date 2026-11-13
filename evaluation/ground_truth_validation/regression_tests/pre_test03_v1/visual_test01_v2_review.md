# Test1 c7cf871 visual regression evidence

The candidate is a **FAILED regression control**, not an accepted pipeline improvement. Rendering completed 108 curated source frames for both actual completed arms in 124.775 seconds. The set preserves 77 seed frames plus 31 expanded cases without editing either source plan. No inference, production edit, original annotation change or Test3 access occurred.

[Visual index](visual_test01_v2/index.md) · [HTML](visual_test01_v2/index.html) · [Completed renderer receipt](visual_test01_v2/completion.json) · [Independent artifact/pixel verification](visual_test01_v2.verification.json) · [Exact reviewed panel hashes and frame facts](visual_test01_v2.review.json) · [Launch/runtime](test01_visual_render_v2.launch.json).

Independent verification passed 1,370 output artifact hashes, 669 input bindings and 324 decoded native-source/proxy PNG pixel hashes. All 108 selected times equal exact frame/30. Neural artifact pins/version/status and profiles remain equal; the tracking component cache version intentionally changes@1→@2 and is recorded separately. The initial independent verifier incorrectly required that component version to remain equal; [attempt1](visual_test01_v2.verification_attempt1.json) preserves the corrected assertion, rather than conflating cache-version change with model-weight corruption. Failed renderer v1 remains byte-identical.

Agent review inspected 16 panels across 12 distinct frames, including every requested 7854/7856/7857/7859/7860 and 8105/8106/8108/8111 frame, 7858 and two unchanged extreme controls. All 108 frames are rendered, but continuous physical-event adjudication of every selected window is not claimed.

| Source transition/control | Before/after observation | Pipeline evidence |
|---|---|---|
|7856→7857,261.866667→261.900000s|Visible18:16→20:18 and abrupt athlete relocation|c7 keeps epoch 3 and carries its near-right box over empty court through 7859. Baseline advances epoch 4 and returns no people at 7857; c7 fresh athlete boxes recover 7860.|
|8105→8106,270.166667→270.200000s|Visible20:18→20:20 and athlete relocation|c7 immediately returns both fresh athletes but keeps epoch 3. Baseline advances epoch 5 and initially abstains; both box populations align by 8108/8111.|
|13466,448.866667s|Athletes overlap near the left net|Fresh box geometry matches between arms. Raw equipment ellipses still include head/body regions; raw overlays do not imply those estimates were semantically admitted.|
|13153,438.433333s|Sampled source/shuttle control|Boxes and raw shuttle position match across arms. Legacy-filled disagreement is not certified physical trajectory error.|

At 7857 the candidate's carried bottom-center (872.406891,623.345886) is paired to generated slot 2 (713.079468,563.760315), yielding 170.104874 px. The box is visibly unsupported by the post-edit pixels. Baseline has no person there, so this is a new population/coverage case, not a worsening of an existing matched athlete's physical foot accuracy. Frames 7858/7859 continue the same stale box. Preserve this regression; do not hide it with a point-distance threshold.

The displayed score changes are source-text observations across edits, not accepted points or evidence identifying missing winners. Agent image checks and generated reference slots remain diagnostic rather than physical GT.

The renderer's baseline semantic-event links refer to the original completed full-NN improved_v1 ledger. The component review's event_differences.json uses the later latest-code cached-semantic control. Keep those event comparison baselines separate; do not infer event accuracy from this visualization. The source/raw-perception comparison is bound to the exact actual completed arms.
