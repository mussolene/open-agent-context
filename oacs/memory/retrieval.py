from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from oacs.core.errors import ValidationFailure
from oacs.memory.models import MemoryRecord


@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    scope: list[str] = field(default_factory=list)
    limit: int = 10


@dataclass(frozen=True)
class RetrievalHit:
    memory: MemoryRecord
    score: float
    provider: str
    reasons: list[str] = field(default_factory=list)
    evidence_values: list[str] = field(default_factory=list)


class RetrievalProvider(Protocol):
    name: str

    def retrieve(
        self, query: RetrievalQuery, memories: list[MemoryRecord]
    ) -> list[RetrievalHit]:
        """Rank already policy-filtered memories."""


class LexicalRetrievalProvider:
    name = "lexical"

    def retrieve(
        self, query: RetrievalQuery, memories: list[MemoryRecord]
    ) -> list[RetrievalHit]:
        hits = [
            RetrievalHit(
                memory=memory,
                score=float(lexical_score(query.text, memory.content.text)),
                provider=self.name,
                reasons=["lexical_text_overlap"],
            )
            for memory in memories
        ]
        ranked = sorted(hits, key=lambda hit: (-hit.score, hit.memory.depth, hit.memory.id))
        nonzero = [hit for hit in ranked if hit.score > 0]
        return (nonzero or ranked)[: query.limit]


class StructuredEvidenceRetrievalProvider:
    name = "structured_evidence"

    def retrieve(
        self, query: RetrievalQuery, memories: list[MemoryRecord]
    ) -> list[RetrievalHit]:
        query_tokens = tokens(query.text)
        hits: list[RetrievalHit] = []
        for memory in memories:
            score = 0
            values: list[str] = []
            reasons: list[str] = []
            for item in memory.content.evidence:
                evidence_text = " ".join(
                    [
                        item.claim,
                        item.value,
                        item.evidence_kind,
                        item.slot,
                        item.participant or "",
                        str(item.day or ""),
                    ]
                )
                overlap = len(query_tokens & tokens(evidence_text))
                if overlap <= 0:
                    continue
                score += overlap
                values.append(item.value)
                reasons.append(f"evidence_overlap:{item.slot}")
            if score:
                hits.append(
                    RetrievalHit(
                        memory=memory,
                        score=float(score),
                        provider=self.name,
                        reasons=list(dict.fromkeys(reasons)),
                        evidence_values=list(dict.fromkeys(values)),
                    )
                )
        return sorted(hits, key=lambda hit: (-hit.score, hit.memory.depth, hit.memory.id))[
            : query.limit
        ]


class HybridRetrievalProvider:
    """Deterministic baseline: structured evidence first, lexical fallback."""

    name = "hybrid_lexical_structured"

    def __init__(self) -> None:
        self.structured = StructuredEvidenceRetrievalProvider()
        self.lexical = LexicalRetrievalProvider()

    def retrieve(
        self, query: RetrievalQuery, memories: list[MemoryRecord]
    ) -> list[RetrievalHit]:
        structured_hits = self.structured.retrieve(query, memories)
        lexical_hits = self.lexical.retrieve(query, memories)
        by_id: dict[str, RetrievalHit] = {hit.memory.id: hit for hit in structured_hits}
        for hit in lexical_hits:
            existing = by_id.get(hit.memory.id)
            if existing is None:
                by_id[hit.memory.id] = hit
                continue
            by_id[hit.memory.id] = RetrievalHit(
                memory=hit.memory,
                score=existing.score + hit.score,
                provider=self.name,
                reasons=list(dict.fromkeys(existing.reasons + hit.reasons)),
                evidence_values=existing.evidence_values,
            )
        ranked = sorted(
            by_id.values(), key=lambda hit: (-hit.score, hit.memory.depth, hit.memory.id)
        )
        return ranked[: query.limit]


class EmbeddingRetrievalProvider:
    name = "embeddings"

    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def retrieve(
        self, query: RetrievalQuery, memories: list[MemoryRecord]
    ) -> list[RetrievalHit]:
        if not self.enabled:
            raise ValidationFailure(
                "embedding retrieval is disabled by default; enable an explicit adapter"
            )
        raise ValidationFailure("embedding retrieval adapter is not configured")


def tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower()))


def lexical_score(query: str, text: str) -> int:
    return len(tokens(query) & tokens(text))


def rank_memories(
    query: str,
    memories: list[MemoryRecord],
    limit: int = 10,
    provider: RetrievalProvider | None = None,
) -> list[MemoryRecord]:
    active_provider = provider or HybridRetrievalProvider()
    hits = active_provider.retrieve(RetrievalQuery(text=query, limit=limit), memories)
    return [hit.memory for hit in hits]
