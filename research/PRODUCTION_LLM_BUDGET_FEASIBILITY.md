# LLM session-budget feasibility audit

**Stage note:** this is the preserved pre-integration candidate/feasibility analysis. The applied state, final controls and limits are in [PRODUCTION_LLM_BUDGET_REPORT.md](PRODUCTION_LLM_BUDGET_REPORT.md).

**Recommendation: implement a durable application admission/accounting guard after the current source freeze; this is feasible locally and is not blocked on a new distributed service. Do not describe an output cap or a post-response counter as a hard total-session billing limit.** A strict total-token reservation additionally needs a provider-specific input bound and complete usage/retry semantics. Those contracts are absent today. No production change is made by this audit.

## Actual current interfaces and failure paths

- `engine/config.py::Settings.llm_budget_tokens_per_session` defaults to400000, has no nonnegative constraint and is never consumed by the agent/API/provider path.
- `agents/agent.py::ask` calls the shared `LLMProvider.complete` for up to six rounds and an additional grounding repair. It does not pass `max_tokens`; the implemented Anthropic default is16000 while the OpenAI-compatible default is4096. These are per-call requested output ceilings, not input-plus-output reservations.
- Each `LLMTurn.usage` is summed in memory and returned with a successful `Answer`. If a later call raises `LLMError`, `answer` returns a deterministic answer and the earlier paid turns' accumulated usage is lost from that returned object. Provider metrics count some successful usage, but Prometheus counters are neither a session ledger nor an admission mechanism.
- The API runs the provider loop in `asyncio.to_thread`, with a cached provider shared across requests. Its event-generation/sequence fence can withhold a completed answer after analysis changes. That must not refund consumed model tokens. The existing read snapshot correctly does not span a network wait.
- The provider interface offers no input-token count, conservative bound, receipt/idempotency identifier or usage-completeness state. Anthropic records input/output/cache_read but does not expose all possible cache-write categories in the neutral turn. The OpenAI-compatible adapter can return an empty usage dictionary. The present interface does not define whether any categories overlap, and it does not define a currency budget.
- Local installed SDK source declares two default automatic retries and600-second default timeouts. The application constructors do not override these. A wrapper cannot silently count one logical `complete` as exactly one transmitted/billed attempt, or conclude that every connection/status exception means zero consumption.
- Installed Anthropic SDK exposes a message token-count API. Installed OpenAI SDK exposes a Responses input-token-count API, but this application sends Chat Completions, including Azure/local-compatible backends. Those are different request contracts; the count endpoint is not a proven drop-in upper bound here. No endpoint was called, no credential inspected and no tokenizer/model/dependency installed. `tiktoken` is absent locally.

## Smallest durable storage/composition

A new optional budget wrapper can implement the existing `LLMProvider` interface around the configured provider. Construct it per request/session rather than modifying the cached provider's session state. Supply a persistent ledger dependency and explicit policy through the API. Every `complete`, including textual-tool recovery and the final grounding repair, passes through the wrapper. Reconcile each successful turn before returning it to the agent loop; settlement does not depend on final publication or citation validity.

The existing public `EventStore.transaction/get_meta/set_meta` APIs are sufficient for atomic durable reservations. A separate path such as `data/llm_budget/<session_id>.sqlite`, outside the resettable analysis database, reuses the existing schema and requires no migration of existing databases or external service. It creates a local ledger file. Its retention/deletion/backup policy must be explicit. This is a feasible minimum using existing interfaces; a dedicated small budget table would be cleaner if an additive schema change is accepted later.

Use a versioned bounded ledger containing spent totals, outstanding reservation amounts, per-turn identifiers and settlement state. Validate nonnegative canonical integer policy/usage values; zero means no model calls, with deterministic fallback still available. Reserve under a short `BEGIN IMMEDIATE` transaction, commit, release every lock, call the provider, then settle under another short transaction. Independent SQLite connections serialize the same ledger. An in-memory lock or separate untransactional get/set is insufficient. Never put this counter only in `Session.meta` via read-modify-save or in the analysis EventStore: whole-body writes can race and `reset_analysis` deletes/replaces that event database.

The executed research probe confirms the storage mechanism with two separate connections and concurrent threads. Naive get/check/set admits two4096-token requests against a4096 budget while reporting only4096. One transaction admits exactly one and persists its4096 reservation across close/reopen. This validates storage feasibility only; it is not an implemented quota or remote-provider test. Exact source, result and input hashes are in `prod_20261105_llm_budget_feasibility_v1/`.

## Scope the enforcement claim correctly

For a hard **output-token** admission policy, reserve the explicit per-call output ceiling before each call, pass that ceiling to the provider and retain uncertain reservations after ambiguous failures. Count/receipt normalization and retry policy still need controls. This policy must be named output-only; it does not implement the current generic total-token setting by itself.

For a conservative **total-token** admission policy, add an optional explicit provider capability that supplies a verified upper bound for the exact serialized input, including system text, history, tools, returned tool data and provider framing. Reserve that bound plus the requested maximum completion before each call. Unknown/unsupported input bounds must fail closed to deterministic fallback in strict mode. A character-count estimate, average tokens-per-character, the Responses count for a different Chat request, or the model's claimed usage is not a proven bound. History is capped in entry count but not per-entry size; tool results can also grow, so account again on every round.

Normalize vendor-reported usage under a versioned policy, separating totals from diagnostic subsets. Missing, negative, malformed or inconsistent usage must not become zero. Keep the reservation or conservatively debit it and stop further strict calls pending reconciliation. If a reported total exceeds its reservation, record an overrun, exhaust further admission and surface the violated bound; already consumed billing cannot be undone.

Define automatic retry behavior explicitly. The smallest auditable option is disable hidden SDK retries for budgeted calls and let the wrapper own any retry as a new reserved attempt. A timeout after dispatch is uncertain consumption: do not refund or automatically expire its reservation merely because a local request ended. Crash-recovered outstanding reservations stay held or are conservatively charged unless a provider receipt supports exact reconciliation. Known pre-dispatch failure can release a reservation. Stale/withheld answers, refusal, tool errors and later-round failure do not erase earlier settled usage.

The software ledger, caps, atomicity and fallback can be implemented now without another service. Full billing equality or account-wide dollar guarantees remain provider/deployment limits; API token counts, caching, retry receipts and usage completeness must be validated per supported backend. With current shared interfaces alone, claiming a universal strict total billing cap would be false. The production-readiness inventory should therefore distinguish a fixable local missing guard from those external billing-contract limits.

## Required tests before enabling enforcement

| Case | Required observable result |
|---|---|
| Zero/negative/boolean/malformed limit | Zero takes deterministic path; invalid policy rejected; no remote call |
| Six tool rounds plus repair | Every model call reserves and settles; no bypass on repair/textual tool path |
| Parallel threads and independent processes | Atomic total spent+outstanding never exceeds the declared admission envelope |
| Two sessions on one cached provider | Separate durable budgets; no shared mutable session counter |
| Restart and analysis reset | Prior usage/outstanding reservations persist; analysis reset does not replenish budget |
| Later-turn provider error | Earlier successful usage stays charged even when Answer is deterministic |
| Response withheld after sequence change | Model usage remains charged; sporting event store is unchanged |
| Missing/invalid/over-bound usage | Explicit unknown/overrun state; no zero charge or silent extra admission |
| Timeout/crash after dispatch | Outstanding amount retained; no timer refund or accidental double settlement |
| Duplicate settlement/request receipt | Idempotent accounting; identical turn cannot refund/debit twice |
| Explicit retry | Each transmitted retry has an accounted reservation; hidden SDK retries disabled or bounded |
| Large Unicode history/tools | Exact supported input-bound capability used; otherwise strict mode abstains |
| Network wait and slow provider | No EventStore/repository writer lock held; analysis still appends events |
| Provider count/output enforcement | Verify actual request cap and counting semantics with scripted SDK transport first; remote deployment validation separate |

The probe and source review use no sporting labels, model execution, credentials or paid calls. They do not justify modifying frozen source or deployment mid-experiment.
