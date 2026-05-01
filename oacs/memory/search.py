from __future__ import annotations

from oacs.memory.models import MemoryRecord
from oacs.memory.retrieval import lexical_score as score_text
from oacs.memory.retrieval import rank_memories as provider_rank_memories


def lexical_score(query: str, memory: MemoryRecord) -> int:
    return score_text(query, memory.content.text)


def rank_memories(query: str, memories: list[MemoryRecord], limit: int = 10) -> list[MemoryRecord]:
    return provider_rank_memories(query, memories, limit)
