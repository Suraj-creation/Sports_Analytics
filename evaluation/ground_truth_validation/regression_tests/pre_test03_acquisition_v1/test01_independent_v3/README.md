# Prepared independent Test1 acquisition-candidate review

Status: **tools prepared; actual fresh results have not been consumed or declared complete**. The new run is bound by `review_config.json` to source-frozen native checkout `test03-scene-acquisition-20261112`, commit `a14695372f0d66d0c80a0bbad8d2c63864001d95`. MAIN is the reporting workspace, not the executed pipeline checkout.

Run only after the complete orchestration publishes `completion.json`:

```bash
cd /home/administrator/Desktop/sport-analytics/test03-scene-acquisition-20261112
source ../gpu-env.sh
PYTHONPATH="$PWD:$PWD/sports/badminton/src:$PWD/engine/src" .venv/bin/python /home/administrator/Desktop/sport-analytics/Sports_Analytics/evaluation/ground_truth_validation/regression_tests/pre_test03_acquisition_v1/test01_independent_v3/review_completed_run.py
```

The review refuses an incomplete orchestration before opening any new predictions/metrics, invokes the actual native strict `load_analysis_input` without rebasing an imported ROOT, and verifies preserved artifact/source/profile/model/annotation/method identities. All outputs are exclusive new files; historical baseline and previous review artifacts remain untouched.

Prepared outputs cover all six interval families and unchanged matching policy, partial-Full2 null metrics, common/new-only/old-only generated point populations, original13 content barriers and every new/lost barrier, every historical182 withheld region, all current gross participant-count losses, latest445-contact semantic control versus fresh events (kept distinct from the older446-contact full neural baseline), contact/class changes and anonymous actor-region changes, runtime/model/config provenance, and cross-chunk actual previous-camera/relative-transform proofs with chunk-start format context. Unsupported physical metrics must remain null.

`source_frame_plan.json` will retain every required source frame; `source_frame_plans/batch_*.json` will partition it into at most128-frame batches without silently dropping cases. Root owns rendering and visual acceptance. Generated-reference agreement and anonymous episode changes do not become physical accuracy or named identity labels.

Sixteen small preparation tests pass. They reject incomplete/foreign runs and forged cross-chunk camera/format proofs. No neural inference, video decoding, new dataset access or pipeline changes were performed by these tools during preparation. Actual completed-run results and acceptance findings will be documented separately after the run finishes.
