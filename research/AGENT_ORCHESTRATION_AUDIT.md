# Agent and orchestration readiness audit — 2026-11-05

The existing system has a grounded match Q&A agent and a separate pipeline command
service. This work fixes reproducible Q&A failures and exercises the existing
command service; it does not introduce another agent framework or confer sporting
authority on an LLM. Starting source was `181cb917dd923524c48772b55ecc71a49ae68518`
on `Benchmarking`. Repository instructions, the complete unchanged handoff, current
inventory additions and latest Nov5 report were reconciled before edits. Every
original inventory field and prior status is preserved; selected metrics and all
36 rows exactly match the previously audited final comparison.

## Actual responsibility map

| Responsibility | Existing owner and path | Contract / evidence limit |
| --- | --- | --- |
| Match Q&A loop | `agents/src/bai_agents/agent.py:ask` | Up to six model/tool rounds plus one grounding repair; citations and numeric consistency checks, not semantic fact verification. |
| Providers | `agents/src/bai_agents/providers.py` | Anthropic and OpenAI-compatible adapters share `LLMProvider`, `LLMTurn`, `ToolCall`; SDK failures use `LLMError` and deterministic fallback. No live provider called here. |
| Read-only match tools | `agents/src/bai_agents/tools.py` | Eight tools consume the event fold, tracks and background passages. Current analytics/tools are badminton-specific, not a general CV task coordinator. |
| Background knowledge | `agents/src/bai_agents/kb.py` | Packaged BM25 passages; background citations remain separate from match evidence. |
| HTTP answer lifecycle | `apps/api/src/bai_api/routes/agents.py` | `asyncio.to_thread` keeps blocking provider work off the event loop. Short repository read snapshots protect tool reads and publication. |
| Pipeline task transport | `engine/src/bai_engine/bus.py` | Local ordered command queue or Redis list; pub/sub notifications are distinct from the durable event ledger. |
| Pipeline task ownership | `engine/src/bai_engine/runtime/runner.py:EngineService` | Existing command consumer owns runners, start/reanalysis/stop, shutdown fencing and recovery. This stream does not modify it. |
| Media/models/stages | `SessionRunner`, sport/plugin/component registries | Shared engine/runtime/schema and sport perception remain separate owners. Agent tools never run inference, write reviews or manufacture events. |
| Evaluation | Existing shot, participant, tracking, reference and rally evaluators | Source-bound reviewed labels, matching semantics and missingness remain independent of agent answers. |

There is no existing persistent multi-agent research-task scheduler under
`agents/`. The historical `docs/testing/eval_agent.py` is a seven-question live-API
script with a fixed session, port and historical output filename. It was inspected
but not invoked because doing so would overwrite historical results and could call
a configured model. Scripted-provider tests below use the actual agent loop and
event tools without remote requests.

## Reproduced failures and fixes

1. A provider returning JSON-array arguments crashed the real agent with
   `AttributeError: 'list' object has no attribute 'items'`. Central tool dispatch
   now validates object shape, known properties and declared scalar types before
   execution. Invalid textual calls remain errors rather than becoming valid empty
   requests. Errors remain inspectable tool results, allowing a subsequent answer
   or explicit abstention.
2. An unknown player's stroke filter returned all 14 fixture strokes and identical
   evidence. A whitespace name resolved to P1; ambiguous aliases selected the first
   matching person. Resolution now requires a unique supported alias, and explicit
   unresolved filters fail closed in rallies, strokes and highlights. Canonical
   player/scoring IDs and unfiltered queries remain available.
3. The real `/ask` flow published `grounded=true` with a cited event retracted
   during provider completion, because `analysis_revision` changes only for an
   analysis reset. The route now fences one event sequence across tool reads and
   publication and verifies cited events against the current live fold. A changed
   sequence, correction or retraction produces the existing retry response. No
   repository or database lock spans a provider/network wait.

These are software/evidence-lifecycle repairs. They do not establish that a cited
contact happened physically or that an LLM's interpretation of a citation is true.
The sequence fence intentionally withholds answers when active analysis appends
new events during a request. A caller can retry against the updated results.

## Executed validation

Evidence: `artifacts/benchmarking/experiments/prod_20261105_systems_initial/`.

| Check | Result | Meaning |
| --- | --- | --- |
| Pre-fix tiny actual-loop/store/API counterexamples | Four reproduced failures in `counterexamples.json` | No models, remote APIs, media or held-out labels involved. |
| Pre-fix regression set | 18 failed / 20 passed, 16.00 s | Failures exercise malformed arguments, unsupported filters/aliases and same-generation stale publication. |
| Final agents + revision guards | 41 passed, 17.35 s | Existing controls plus new fixes, textual malformed calls and service lifecycle control. |
| Actual HTTP grounded/fallback/reset integration | 2 passed, 9 deselected, 7.04 s | Existing `TestClient` path, scripted provider and deterministic fallback. |
| Dataset metadata protocol | 11 passed, 0.17 s | Split/hash aliases, prior exposure, missing identity/rights, immutable snapshots and no media opening. |

The orchestration test uses actual `LocalBus` and `EngineService` with a model-free
runner boundary: one initialization fault must not kill the consumer; a retry
starts successfully; a queued stop reaches that runner; shutdown closes cleanly.
It proves local task lifecycle behavior, not GPU inference, Redis deployment or
remote LLM cancellation. Its first fixture run failed because a temporary empty
model registry lacked `manifest.yaml`; that log is retained. The corrected fixture
supplies an empty registry and the complete final run passes.

## Remaining production gates — initial audit snapshot

This section preserves the pre-budget-repair findings. The two budget/envelope
observations below are superseded by the applied current-state section later in
this report; the absence of live vendor and reviewed sporting validation remains
an actual limitation.

- External/provider and local-neural Q&A accuracy, latency, refusal and outage
  behavior remain untested here. Scripted providers establish orchestration
  contracts only.
- **Pre-repair observation, superseded below:** `llm_budget_tokens_per_session` is configured in shared settings but is not
  consumed by this agent loop. There is no durable per-session usage reservation,
  and no claim of distributed quota enforcement or interruption of an in-flight
  provider request. Such changes need coordinated persistence/config ownership.
- **Pre-repair observation, superseded below:** history is capped at 12 entries and questions at 1,000 characters; per-history
  content and tool calls within a provider turn have no dedicated budget here.
- The Q&A tools still use badminton analytics and session player/scoring labels.
  They do not supply reviewed four-person identity or general-domain agent tools.
  The independent host/plugin tests are separate evidence.
- A numeric/citation validator is a consistency check. It cannot establish
  qualitative accuracy, calibrated confidence or contact/shot/scoring truth.

No deployment, credentials, environment, historical evidence or unrelated job was
modified. No GPU work was launched by this stream.

## Physical-certainty presentation

The existing shot toast already identifies non-human events as estimates and
prints raw support as a score. Two other views lacked that distinction: the live
feed showed machine-confirmed strokes/rallies without an estimate marker, and
Q&A citation tooltips called a model support band "confirmed evidence". The live
feed now distinguishes "Estimate" from "Human reviewed". Citation tooltips name
estimated/reviewed events separately from their support band. Neither rendering
claims calibrated probability or proves a physical racket impact.

Six new presentation regressions fail before the fix and pass afterward. The full
frontend suite passes 192 tests in 42 files; TypeScript checking and a production
build pass. The build writes only to the new
`prod_20261105_physical_certainty_ui/build/` artifact directory; the deployed
frontend is untouched. Four owned component/test files pass Biome. The existing
shared component test needs a one-line tooltip wording update; its unrelated
broadcast-score fixture has a pre-existing formatting failure, retained in the
check log. That file's lint-only check passes. The initial new test's unsupported
Testing Library `exact` option was removed after the type checker caught it;
the failed log remains available. These are UI contract checks, not a browser HLS
seek validation or measured sporting accuracy.

## Superseding applied token admission and final product state

The budget and envelope gaps in the initial snapshot above have been addressed
by the scoped, reviewed repair documented in
[PRODUCTION_LLM_BUDGET_REPORT.md](PRODUCTION_LLM_BUDGET_REPORT.md). The session
allowance is now consumed through a durable prospective ledger under
`data/llm_budget/`, retained separately from sporting resets/restores. Each model
or repair call receives admission and reservation; known usage settles before
another call, and missing/inconsistent usage preserves uncertainty and blocks
future calls rather than becoming zero. Concurrent connection/process and
reset/restore contracts have executable coverage. Prior unmetered usage remains
unknown; deleting an analysis must not replenish its allowance. Backups and
retention must include the separate ledger directory.

The default mode is **reported**, preserving configured native providers and
their existing adapter output defaults. A response can cross the total because
its input tokens were unknown before dispatch; subsequent calls are withheld.
This is not a pre-dispatch total-token, account-wide currency or remote-provider
billing hard cap. Strict admission is explicit opt-in and remains unsupported by
the current native adapters without an attested exact-request input bound,
enforced output cap and retry contract. Request byte/resource bounds now apply,
including oversized literal text within otherwise opaque history; those are not
token-count approximations. Native clients explicitly disable automatic transport
retries and set 30-second I/O timeouts, which do not establish process-wide
deadlines or cancellation of provider-internal work. No live remote provider or
token-count endpoint was called in this workstream.

The same report preserves the reviewed v2 delta, actual merged **117-test**
overlapping validation scope, durable unknown handling and SDK-stub limits. The
root-owned current-frame contact projection separately passes **15 controls** in
`agents/tests/test_tool_contact_provenance.py`: tools expose the analysis-frame
timebase, typed physical status and source-contact citations; legacy, retracted,
superseded or misaligned support remains unknown. A finalized event or a support
band still does not establish physical contact, named identity or calibrated
probability. No original-camera frame mapping is invented.

Final integrated frontend validation passes **226 tests across 46 files**,
TypeScript and the isolated release-v5 build. Its actual browser product gate
`prod_20261105_product_smoke_v5/` passes unchanged 309-source/45-build/input guards,
six exact pixel seeks, four matching downloads, source ownership, truthful failure
states and public/private diagnostic separation, with complete owned-process
cleanup. The separate nonempty completed-Test7 product-v3 replay preserves raw
32-rally/248-contact event IDs and the 21 intervals marked official by phase
logic; it is a prior-build result-display check, not another inference or
reviewed accuracy measurement. See
[PRODUCTION_PRODUCT_SMOKE_REPORT.md](PRODUCTION_PRODUCT_SMOKE_REPORT.md) and
[PRODUCTION_CALIBRATION_SAVE_REPORT.md](PRODUCTION_CALIBRATION_SAVE_REPORT.md).
No deployment, model/profile default, historical LLM accounting or sporting truth
claim follows from these orchestration and product contracts.
