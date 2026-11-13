# Implemented native postprocessing compatibility

The implementation is in two new MAIN files:

- `research/scene_epoch_audit_v3.py` validates every cache packet using the actual native decoder, binds adjacent source cameras across catalogue chunks, and admits raw-false resets only with a positive V4/V3 court/camera/format proof. Raw hypothesis flags remain false in counts and CSV.
- `evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py` uses explicit producer/tool roots and unchanged native loaders, numeric helpers and component reference policies. It provides `--mode analysis` (default) and `--mode components-test2`, with `--coordinate-binding` for the latter.

Both modes require genuine original worker/parent/catalogue completion. The recorded executor's worker-script path and the complete source-file paths/hashes bind the producer. `plan.root` identifies the external protocol workspace; it is deliberately not treated as a code checkout. Imported native module ROOT and decoder file paths must match the explicit producer checkout. No globals or ROOT are replaced. Output must be a new directory outside the original run.

The new component function transparently preserves the original native Test2 evaluator's full assembly, constants, annotation paths, reference matching, point pairing, distributions, court arithmetic, coverage and null policies. It records the original native helper identity and separately identifies the executed adapter. The technical report similarly calls original numerical/event/resource/model functions. Separate compatibility receipts identify the new tool and structural version; original failed outer receipts remain failed and preserved.

Validation uses28 focused cases, including the actual Test2 frame355 RED-to-GREEN control, nine invalid native-proof/epoch controls, legacy strong/unknown fallback, raw-false CSV preservation, cross-chunk camera forgery, wrong producer rejection and exact AST comparisons of both report assemblies. Normalization removes only the declared structural/provenance additions and explicit native namespace prefixes; all remaining original assembly ASTs match exactly. Focused tests pass in [implementation_focused_tests_v5.log](implementation_focused_tests_v5.log).

The final full Test1 analysis used the actual unchanged native loader and all17,268 original frames. Every original technical report value is identical except the explicit input-provenance expansion. The sole added top-level field is `structural_compatibility`. The coverage CSV is byte-identical, no weak resets are present, and all1,472 original consumed input hashes remain present and unchanged. The new analysis records1,763 input paths with tool/source bindings. [Final parity receipt](implementation_parity_receipt.json) contains exact source and output hashes. The original report and validation output are separate.

Two initial pytest invocations correctly rejected accidental MAIN module selection from the project's pytest configuration; their logs remain. The final invocation explicitly sets the native `-c`, `--rootdir` and `--import-mode=importlib`. An intermediate analysis guard incorrectly compared the protocol workspace root to the producer checkout and rejected before analysis; that failure log remains and the corrected final guard binds the recorded worker and source population. No original metadata was changed to make a guard pass.

Root owns the new `test02_postprocessing_v1` continuation, final report publication and acceptance. The implementation does not rerun NN inference, claim reset accuracy or authorize Test3. The nine weak reset source panels require independent visual adjudication.

Example from the frozen native checkout:

```bash
source ../gpu-env.sh
PYTHONPATH="$PWD:$PWD/engine/src:$PWD/sports/badminton/src" .venv/bin/python \
  /home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py \
  --producer-root "$PWD" \
  --tool-root /home/administrator/Desktop/sport-analytics/Sports_Analytics \
  --run /absolute/original/completed/run \
  --output /absolute/new/postprocessing/analysis
```

For component reference diagnostics, use the same explicit roots/run with `--mode components-test2 --coordinate-binding /absolute/source-bound/certificate.json` and a different new output directory. This evaluates saved predictions and references; it does not perform inference.
