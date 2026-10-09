"""Background knowledge (rules, player bios, terminology) — never the source of match truth.

A small BM25 index over plain-text documents.  It replaces the legacy FAISS pickle index (which
required ``allow_dangerous_deserialization=True``) with a dependency-free, rebuild-on-load index
over trusted files shipped in the package.
"""

from __future__ import annotations

import functools
import math
import re
from collections import Counter
from dataclasses import dataclass
from importlib import resources

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "is",
    "was",
    "for",
    "with",
    "at",
    "by",
    "as",
    "his",
    "her",
    "she",
    "he",
    "it",
    "that",
    "this",
    "from",
    "be",
    "are",
    "were",
    "has",
    "have",
}


def _tok(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP]


@dataclass(frozen=True)
class Passage:
    doc: str
    idx: int
    text: str

    @property
    def ref(self) -> str:
        return f"{self.doc}#{self.idx}"


class KnowledgeBase:
    def __init__(self, passages: list[Passage]) -> None:
        self.passages = passages
        self._tf = [Counter(_tok(p.text)) for p in passages]
        self._len = [sum(c.values()) for c in self._tf]
        self._avg = sum(self._len) / max(1, len(self._len))
        df: Counter[str] = Counter()
        for c in self._tf:
            df.update(c.keys())
        n = len(passages)
        self._idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def search(self, query: str, k: int = 4, k1: float = 1.5, b: float = 0.75) -> list[tuple[Passage, float]]:
        q = _tok(query)
        scores = []
        for i, tf in enumerate(self._tf):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self._idf.get(t, 0.0) * f * (k1 + 1) / (f + k1 * (1 - b + b * self._len[i] / self._avg))
            if s > 0:
                scores.append((self.passages[i], s))
        scores.sort(key=lambda x: -x[1])
        return scores[:k]


def _split(text: str, size: int = 700) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) > size and cur:
            chunks.append(cur.strip())
            cur = ""
        cur += " " + s
    if cur.strip():
        chunks.append(cur.strip())
    return chunks


@functools.cache
def get_kb(sport: str = "badminton") -> KnowledgeBase:
    root = resources.files("bai_agents").joinpath("knowledge", sport)
    passages: list[Passage] = []
    for entry in sorted(root.iterdir(), key=lambda e: e.name):
        if not entry.name.endswith(".txt"):
            continue
        doc = entry.name[:-4]
        for i, chunk in enumerate(_split(entry.read_text(encoding="utf-8", errors="replace"))):
            passages.append(Passage(doc, i, chunk))
    return KnowledgeBase(passages)
