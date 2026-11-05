"""Provider-reported token semantics, distinct from strict preflight bounds."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


def _count(value: Any) -> int | None:
    return value if type(value) is int and 0 <= value <= 2**63 - 1 else None


@dataclass(frozen=True, slots=True)
class ReportedTokenUsage:
    semantics: str
    components: tuple[tuple[str, int], ...]
    total: int | None
    complete: bool
    missing: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        items = tuple(self.components.items()) if isinstance(self.components, Mapping) else tuple(self.components)
        if not isinstance(self.semantics, str) or not self.semantics or len(self.semantics) > 160:
            raise ValueError("invalid token usage semantics")
        if len(items) > 16 or len({key for key, _ in items}) != len(items):
            raise ValueError("invalid token usage components")
        for key, count in items:
            if not isinstance(key, str) or not key or len(key) > 64 or _count(count) is None:
                raise ValueError("invalid token usage component")
        if type(self.complete) is not bool or (self.total is not None and _count(self.total) is None):
            raise ValueError("invalid token usage total")
        if self.complete and self.total is None:
            raise ValueError("complete token accounting requires a total")
        if len(self.missing) > 16 or any(not isinstance(key, str) or len(key) > 64 for key in self.missing):
            raise ValueError("invalid missing token fields")
        object.__setattr__(self, "components", tuple(sorted(items)))
        object.__setattr__(self, "missing", tuple(self.missing))

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantics": self.semantics,
            "components": dict(self.components),
            "total": self.total,
            "complete": self.complete,
            "missing": list(self.missing),
        }

    @classmethod
    def from_dict(cls, value: Any) -> ReportedTokenUsage:
        if not isinstance(value, dict) or set(value) != {"semantics", "components", "total", "complete", "missing"}:
            raise ValueError("invalid token accounting payload")
        if not isinstance(value["components"], dict) or not isinstance(value["missing"], list):
            raise ValueError("invalid token accounting payload")
        return cls(
            value["semantics"],
            tuple(value["components"].items()),
            value["total"],
            value["complete"],
            tuple(value["missing"]),
        )


def openai_usage(usage: Any) -> ReportedTokenUsage:
    """The declared SDK total includes prompt+completion, cached input is a subset."""
    fields = {
        "input": _count(getattr(usage, "prompt_tokens", None)),
        "output": _count(getattr(usage, "completion_tokens", None)),
        "provider_total": _count(getattr(usage, "total_tokens", None)),
    }
    details = getattr(usage, "prompt_tokens_details", None)
    for key, attr in (("cache_read_subset", "cached_tokens"), ("cache_write_subset", "cache_write_tokens")):
        value = _count(getattr(details, attr, None))
        if value is not None:
            fields[key] = value
    missing = tuple(key for key in ("input", "output", "provider_total") if fields[key] is None)
    if fields["input"] is not None:
        missing += tuple(
            f"{key}_exceeds_input"
            for key in ("cache_read_subset", "cache_write_subset")
            if key in fields and fields[key] > fields["input"]
        )
    complete = not missing and fields["provider_total"] == fields["input"] + fields["output"]
    if not missing and not complete:
        missing = ("consistent_total",)
    return ReportedTokenUsage(
        "openai-prompt-plus-completion:v1",
        tuple((k, v) for k, v in fields.items() if v is not None),
        fields["provider_total"] if complete else None,
        complete,
        missing,
    )


def anthropic_usage(usage: Any) -> ReportedTokenUsage:
    """Uncached input, cache reads/writes and output are disjoint usage categories.

    Missing optional cache fields are unknown rather than silently zero. The
    application does not configure server tools/compaction; if iteration usage
    appears, its complete bill is not assumed to equal the top-level counters.
    """
    fields = {
        key: _count(getattr(usage, attr, None))
        for key, attr in (
            ("input_uncached", "input_tokens"),
            ("output", "output_tokens"),
            ("cache_read", "cache_read_input_tokens"),
            ("cache_write", "cache_creation_input_tokens"),
        )
    }
    missing = tuple(key for key, value in fields.items() if value is None)
    if getattr(usage, "iterations", None):
        missing = (*missing, "iteration_usage_not_normalized")
    complete = not missing
    known = tuple((key, value) for key, value in fields.items() if value is not None)
    return ReportedTokenUsage(
        "anthropic-disjoint-input-cache-output:v1",
        known,
        sum(value for _, value in known) if complete else None,
        complete,
        missing,
    )
