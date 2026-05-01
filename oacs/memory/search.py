from __future__ import annotations

import re

from oacs.memory.models import MemoryRecord


def lexical_score(query: str, memory: MemoryRecord) -> int:
    q = set(re.findall(r"\w+", query.lower()))
    m = set(re.findall(r"\w+", memory.content.text.lower()))
    return len(q & m)


def rank_memories(query: str, memories: list[MemoryRecord], limit: int = 10) -> list[MemoryRecord]:
    ranked = sorted(memories, key=lambda mem: (lexical_score(query, mem), -mem.depth), reverse=True)
    return [mem for mem in ranked if lexical_score(query, mem) > 0][:limit] or ranked[:limit]
