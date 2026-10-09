"""Typed access to ``ontology.yaml``."""

from __future__ import annotations

import functools
from importlib import resources
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from bai_engine.schema import ConfidenceBand


class StrokeDef(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: str
    attacking: bool
    label: str


class Ontology(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: int
    confidence_bands: dict[str, float]
    event_types: dict[str, str]
    strokes: dict[str, StrokeDef]
    subtypes: dict[str, dict[str, str]]
    bst_class_map: dict[str, str]
    finebadminton_map: dict[str, str]
    legacy_map: dict[str, str]
    rally_outcomes: dict[str, str]
    highlight_categories: dict[str, str]
    court_zones: dict[str, list[str]]

    def band(self, p: float | None) -> ConfidenceBand:
        return ConfidenceBand.from_confidence(
            p, confirmed=self.confidence_bands["confirmed"], probable=self.confidence_bands["probable"]
        )

    def normalize_stroke(self, raw: str, source: str = "bst") -> str:
        """Map a model / dataset / legacy stroke label to a canonical stroke id."""
        key = raw.strip().lower()
        for prefix in ("top ", "bottom ", "top_", "bottom_"):
            if key.startswith(prefix):
                key = key[len(prefix) :]
        table = {"bst": self.bst_class_map, "finebadminton": self.finebadminton_map, "legacy": self.legacy_map}[source]
        if key in self.strokes:
            return key
        return table.get(key, "unknown")

    def stroke(self, stroke_id: str) -> StrokeDef:
        return self.strokes.get(stroke_id, self.strokes["unknown"])


@functools.cache
def get_ontology() -> Ontology:
    text = resources.files("bai_badminton").joinpath("ontology.yaml").read_text(encoding="utf-8")
    data: dict[str, Any] = yaml.safe_load(text)
    return Ontology.model_validate(data)
