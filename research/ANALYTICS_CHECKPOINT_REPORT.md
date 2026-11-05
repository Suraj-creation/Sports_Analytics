# H21: analytics journal isolation and checkpoint cost

Date:2026-11-05; branch:`Benchmarking`; initial HEAD:`181cb91`. This is a focused baseline-analytics implementation change, not a perception/model experiment or a full-pipeline performance claim. Custom provider checkpoints remain opaque and are never copied by the host.

## Reproduced defects

The previous`TransactionalAnalytics` stored original stroke/retraction Event references in its operation list. Although Event fields are frozen, nested payloads are mutable. Appending a smash, mutating its caller-owned payload to clear, then checkpointing/resetting/restoring changed the aggregate from smash1 to clear1. A snapshot could therefore disagree with the state it supposedly captured.

Rally input ownership was inconsistent in the other direction: the journal copied a RallyRecord, while the live aggregate retained the original caller object. Mutating a caller's duration1→999 changed current active-play duration to999, while restoring the checkpoint returned1. Both official and unofficial records were affected. A failure after a projection mutation could also leave an operation in history and a partial aggregate behind.

The checkpoint implementation additionally deep-copied all historical operations for every transaction. CPU-only measurements using actual typed Event and RallyRecord instances demonstrated its scaling cost. No sporting labels or model inference were involved.

## Change and compatibility

The assigned block in`sports/badminton/src/bai_badminton/components.py` now uses a private persistent linked journal. Frozen links share the prior history, while each append stores copied typed inputs and passes a separate copy to the existing MatchAnalytics projection. A caller cannot rewrite an earlier operation by mutating the originally supplied Event payload, RallyRecord, nested shot list or presence list.

A checkpoint contains an owner identity and journal head; taking it does not traverse, copy or replay history. Restore iterates the captured chain in chronological order and replays the existing base implementation. Prior checkpoints survive resets and branching refolds. Failed appends rebuild from the previous head before propagating the original error. Baseline close behavior and owner-bound rejection of foreign checkpoints remain intact.

The engine's generic checkpoint/restore contract, custom providers, scoring rules, operation ordering and analytics output schema are unchanged. Checkpoints are process-local opaque tokens; they are not a new persisted event/cache format. The existing engine transaction lock still owns serialized use; the journal is not claimed to support concurrent writers.

Checkpoint work is O(1); append is proportional to the new input payload; restore and exceptional recovery remain O(history). Retained history remains O(history), and retained checkpoint tokens keep their historical branches alive until released. This change does not claim to bound match-long event history or make every analytics API output immutable.

## Measured before/after experiment

Reproducer:

```sh
source ../gpu-env.sh
.venv/bin/python research/production_analytics_checkpoint_probe.py \
  --output artifacts/benchmarking/experiments/NEW_analytics_checkpoint
```

The unchanged probe alternates stroke, legacy presence, rally and stroke-retraction operations. It measures five untraced checkpoints per history size, a separately traced allocation sample, append cost and reset/restore. Tracer overhead is excluded from reported checkpoint walltimes. Every restored public aggregate exactly matches its pre-checkpoint aggregate for these typed fixtures.

| Operations | Old checkpoint median ms | New checkpoint median ms | Old checkpoint traced peak bytes | New traced peak bytes |
| --- | ---: | ---: | ---: | ---: |
|100 |1.470598 |.000623 |145,608 |48 |
|1,000 |15.177686 |.000499 |1,729,224 |48 |
|5,000 |85.189013 |.000461 |8,747,688 |48 |

The sub-microsecond samples are near measurement overhead and are not stable tail-latency estimates. The structural test preventing any history deepcopy or replay during checkpoint is stronger evidence of constant work than a large speedup ratio would be.

Input ownership has a measured cost that remains explicit:

| Operations | Old append ms | New append ms | Old restore ms | New restore ms |
| --- | ---: | ---: | ---: | ---: |
|100 |1.653 |6.261 |1.647 |2.477 |
|1,000 |14.270 |62.348 |16.635 |22.839 |
|5,000 |70.110 |306.494 |116.046 |113.648 |

Copies now occur once per new admission rather than once per complete history at every checkpoint. The experiment does not predict full-pipeline throughput, and normal process/CPU scheduling was not isolated. Restore is intentionally linear; no claim of constant-time rollback is made.

Artifacts preserve the exact executed component and probe source, SHA-256 values, raw samples and limits:

* `artifacts/benchmarking/experiments/prod_20261105_analytics_checkpoint_before/`: component SHA`df15829d403fc18d143939c29a831a34fc10b798000a5e2dbca66d14c73cd6ba`.
* `artifacts/benchmarking/experiments/prod_20261105_analytics_checkpoint_after/`: component SHA`70d6222550584fb49047503d2a29c06231df58f1a1ff1851eddb4835a774193a`.

Both source guards passed. The same probe script SHA is`67059fe5fab973ffb58992ddc4d428de76332d3db416ded6ff5bbb2269b4b8db`.

## Regression controls

New`sports/badminton/tests/test_transactional_analytics_checkpoint.py` has12 meaningful controls: caller Event mutation; official/unofficial RallyRecord mutation; no history deepcopy/replay at checkpoint; reset survival; corrections/retractions and branching order; retraction payload mutation; presence-list ownership; foreign checkpoints; injected partial projection failure; empty/repeated restore; and close/checkpoint compatibility.

The first red run exposed five actual mutation/scaling failures plus an incorrect fixture assumption that an invalid player would raise. The base aggregate uses a default dictionary, so that assumption was corrected to a deterministic failure injected **after** a real projection append. Historical logs remain untouched. The corrected suite run against the measured pre-fix source snapshot, using only a process-local constructor substitution, records6failed/6passed in`prod_20261105_analytics_checkpoint_corrected_red.log`. This negative control changes no production source.

Current journal, scoring-transaction, analytics-integrity and independent domain-component selection tests pass51 tests in1.98s (`prod_20261105_analytics_checkpoint_green_v4.log`). Changed Python lint/format checks pass. These synthetic input tests establish software transaction and ownership contracts, not sporting analytics accuracy.

The separate independent contact-consumer audit also reproduced pose-cadence, physical-status propagation, epoch and provider-frontier defects; those fixes belong to the orchestrator and are documented by their own red/green controls. This journal patch changes no contact support, rally boundary, player identity, shot classifier or perception provider.
