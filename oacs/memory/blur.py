from __future__ import annotations

from oacs.memory.service import MemoryService


def blur_memory(service: MemoryService, memory_id: str, actor_id: str | None):
    return service.blur(memory_id, actor_id)
