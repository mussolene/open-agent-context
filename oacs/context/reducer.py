from __future__ import annotations

from oacs.context.capsule import ContextCapsule


def reduce_capsule(capsule: ContextCapsule, max_memories: int) -> ContextCapsule:
    capsule.included_memories = capsule.included_memories[:max_memories]
    return capsule.seal()
