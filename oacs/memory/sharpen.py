from __future__ import annotations

from oacs.memory.service import MemoryService


def sharpen_memory(service: MemoryService, memory_id: str, evidence_ref: str, actor_id: str | None):
    return service.sharpen(memory_id, evidence_ref, actor_id)
