"""Domain-neutral, session-scoped component registration and lifecycle contracts."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from contextlib import suppress
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, cast

ComponentFactory = Callable[[Any, dict[str, Any]], Any]


@dataclass(frozen=True, slots=True)
class ComponentContract:
    """A provider's versioned port, dependencies, capabilities and failure policy.

    Schema identifiers name provider-owned input/output contracts; ``interface``
    is the runtime-checkable protocol used to verify the constructed port. The
    host does not interpret domain-specific schemas, formats or failure policies.
    A stateful provider must implement ``reset()`` and ``close()``. Its factory
    owns restoration or other domain-specific state through the typed context.
    """

    kind: str
    implementation: str
    version: str
    input_schema: str
    output_schema: str
    interface: type[Any]
    context_type: type[Any]
    supported_formats: frozenset[str]
    failure_policy: str
    stateful: bool = False
    declaration: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("kind", "implementation", "version", "input_schema", "output_schema", "failure_policy"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"component {name} must be a nonempty string")
        if not isinstance(self.interface, type) or not (
            getattr(self.interface, "_is_protocol", False) and getattr(self.interface, "_is_runtime_protocol", False)
        ):
            raise TypeError("component interface must be a runtime-checkable Protocol")
        if not isinstance(self.context_type, type):
            raise TypeError("component context_type must be a type")
        if not isinstance(self.stateful, bool):
            raise TypeError("component stateful must be a boolean")
        if isinstance(self.supported_formats, (str, bytes)):
            raise ValueError("component supported_formats must declare format names")
        formats = frozenset(self.supported_formats)
        if not formats or any(not isinstance(value, str) or not value.strip() for value in formats):
            raise ValueError("component supported_formats must contain nonempty format names")
        object.__setattr__(self, "supported_formats", formats)
        if not isinstance(self.declaration, Mapping):
            raise ValueError("component declaration must be a finite JSON object")
        declaration_source = (
            _public_declaration(self.declaration)
            if isinstance(self.declaration, MappingProxyType)
            else dict(self.declaration)
        )
        declaration = _snapshot_json(declaration_source, "declaration")
        object.__setattr__(self, "declaration", _freeze_declaration(declaration))

    def describe(self) -> dict[str, Any]:
        """Return detached JSON metadata, without factories or dependency objects."""
        return {
            "kind": self.kind,
            "implementation": self.implementation,
            "version": self.version,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "interface": f"{self.interface.__module__}.{self.interface.__qualname__}",
            "context_type": f"{self.context_type.__module__}.{self.context_type.__qualname__}",
            "supported_formats": sorted(self.supported_formats),
            "failure_policy": self.failure_policy,
            "stateful": self.stateful,
            "declaration": _public_declaration(self.declaration),
        }


@dataclass(slots=True)
class ComponentHandle:
    """One session's component and the identity of its construction inputs."""

    instance: Any
    contract: ComponentContract
    fingerprint: str
    _closed: bool = field(default=False, init=False, repr=False)

    def reset(self) -> None:
        if self._closed:
            raise RuntimeError("component handle is closed")
        reset = getattr(self.instance, "reset", None)
        if callable(reset):
            reset()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        instance, self.instance = self.instance, None
        close = getattr(instance, "close", None)
        if callable(close):
            close()


def _check_json(value: Any) -> None:
    """Reject coercions (such as integer keys) that would change cache identity."""
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    if isinstance(value, list):
        for item in value:
            _check_json(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            _check_json(item)
        return
    raise ValueError("values must be finite JSON data")


def _snapshot_json(value: dict[str, Any], name: str) -> dict[str, Any]:
    try:
        if not isinstance(value, dict):
            raise ValueError("JSON object required")
        _check_json(value)
        return cast(dict[str, Any], json.loads(json.dumps(value, allow_nan=False, sort_keys=True)))
    except (TypeError, ValueError, OverflowError, RecursionError):
        # Configuration can contain credentials; include neither values nor
        # serialization exceptions in the public failure message.
        raise ValueError(f"component {name} must be finite JSON data with string object keys") from None


def _freeze_declaration(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_declaration(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_declaration(item) for item in value)
    return value


def _public_declaration(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _public_declaration(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_public_declaration(item) for item in value]
    return value


class ComponentRegistry:
    """Resolve explicit providers without global registrations or implicit fallback.

    Factories receive a fresh configuration snapshot and explicit dependencies
    for each creation. Callers provide media/calibration/model identities through
    ``context_identity``; live dependency objects are never serialized or hashed.
    """

    def __init__(self) -> None:
        self._providers: dict[tuple[str, str], tuple[ComponentContract, ComponentFactory]] = {}

    def register(self, contract: ComponentContract, factory: ComponentFactory) -> None:
        key = (contract.kind, contract.implementation)
        if key in self._providers:
            raise ValueError(f"component {contract.kind}/{contract.implementation} is already registered")
        if not callable(factory):
            raise TypeError("component factory must be callable")
        self._providers[key] = (contract, factory)

    def describe(self) -> list[dict[str, Any]]:
        return [self._providers[key][0].describe() for key in sorted(self._providers)]

    def create(
        self,
        kind: str,
        implementation: str,
        *,
        context: Any,
        configuration: dict[str, Any],
        match_format: str,
        context_identity: dict[str, Any] | None = None,
    ) -> ComponentHandle:
        provider = self._providers.get((kind, implementation))
        if provider is None:
            raise RuntimeError(f"component {kind}/{implementation} is missing")
        contract, factory = provider
        if match_format not in contract.supported_formats:
            raise RuntimeError(f"component {kind}/{implementation} does not support format {match_format!r}")
        if not isinstance(context, contract.context_type):
            raise RuntimeError(f"component {kind}/{implementation} received an incompatible context")
        configuration_snapshot = _snapshot_json(configuration, "configuration")
        identity_snapshot = _snapshot_json(context_identity if context_identity is not None else {}, "context identity")
        identity = {
            "contract": contract.describe(),
            "configuration": configuration_snapshot,
            "context_identity": identity_snapshot,
            "format": match_format,
        }
        fingerprint = hashlib.sha256(
            json.dumps(identity, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        instance = factory(context, configuration_snapshot)
        try:
            if not isinstance(instance, contract.interface):
                raise RuntimeError(f"component {kind}/{implementation} does not implement its declared interface")
            if contract.stateful and not all(
                callable(getattr(instance, method, None)) for method in ("reset", "close")
            ):
                raise RuntimeError(
                    f"stateful component {kind}/{implementation} is missing reset/close lifecycle methods"
                )
        except BaseException:
            # The registry owns a returned instance even when its port is wrong.
            # Cleanup errors must not hide the actionable construction failure.
            with suppress(Exception):
                close = getattr(instance, "close", None)
                if callable(close):
                    close()
            raise
        return ComponentHandle(instance=instance, contract=contract, fingerprint=fingerprint)
