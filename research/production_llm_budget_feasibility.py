"""Read-only-interface budget-storage feasibility; no LLM/provider/network calls."""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from bai_engine.store import EventStore

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/benchmarking/experiments/prod_20261105_llm_budget_feasibility_v1"


def main():
    OUT.mkdir(exist_ok=False)
    naive = OUT / "naive.sqlite"
    stores = [EventStore(naive, "S1"), EventStore(naive, "S1")]
    stores[0].set_meta("spent", "0")
    ready = threading.Barrier(2)

    def unsafe(store):
        spent = int(store.get_meta("spent") or 0)
        allowed = spent + 4096 <= 4096
        ready.wait()
        if allowed:
            store.set_meta("spent", str(spent + 4096))
        return allowed

    with ThreadPoolExecutor(max_workers=2) as pool:
        admitted = list(pool.map(unsafe, stores))
    naive_result = {
        "admitted": sum(admitted),
        "reported_spent": int(stores[0].get_meta("spent")),
        "reserved_total": sum(admitted) * 4096,
        "budget": 4096,
    }
    assert naive_result["admitted"] == 2 and naive_result["reported_spent"] == 4096
    for store in stores:
        store.close()

    atomic = OUT / "atomic.sqlite"
    stores = [EventStore(atomic, "S1"), EventStore(atomic, "S1")]
    stores[0].set_meta("spent", "0")
    ready = threading.Barrier(2)

    def reserve(store):
        ready.wait()
        with store.transaction():
            spent = int(store.get_meta("spent") or 0)
            if spent + 4096 > 4096:
                return False
            store.set_meta("spent", str(spent + 4096))
            return True

    with ThreadPoolExecutor(max_workers=2) as pool:
        admitted = list(pool.map(reserve, stores))
    atomic_result = {"admitted": sum(admitted), "durable_reserved": int(stores[0].get_meta("spent")), "budget": 4096}
    assert atomic_result["admitted"] == 1 and atomic_result["durable_reserved"] == 4096
    for store in stores:
        store.close()
    with EventStore(atomic, "S1") as reopened:
        assert reopened.get_meta("spent") == "4096"
    result = {
        "mode": "model-free existing public EventStore storage-contract probe, not an implemented LLM quota",
        "naive_separate_get_set_race": naive_result,
        "atomic_cross_connection_reservation": atomic_result,
        "restart_preserves_outstanding_reservation": True,
        "providers_constructed": 0,
        "network_calls": 0,
        "limitation": (
            "This tests atomic storage feasibility only, not provider token counting, SDK retries, "
            "crash recovery, or complete budget policy."
        ),
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "executed_probe.py").write_bytes(Path(__file__).read_bytes())
    sources = [
        Path(__file__),
        ROOT / "engine/src/bai_engine/config.py",
        ROOT / "engine/src/bai_engine/store/events.py",
        ROOT / "engine/src/bai_engine/store/sessions.py",
        ROOT / "agents/src/bai_agents/agent.py",
        ROOT / "agents/src/bai_agents/providers.py",
        ROOT / "apps/api/src/bai_api/routes/agents.py",
    ]
    (OUT / "source_sha256.json").write_text(
        json.dumps({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, indent=2)
        + "\n"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
