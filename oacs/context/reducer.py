from __future__ import annotations

from oacs.context.capsule import ContextCapsule
from oacs.memory.models import MemoryRecord


def reduce_capsule(capsule: ContextCapsule, max_memories: int) -> ContextCapsule:
    capsule.included_memories = capsule.included_memories[:max_memories]
    return capsule.seal()


def select_memories_for_token_budget(
    memories: list[MemoryRecord], token_budget: int
) -> tuple[list[MemoryRecord], dict[str, int]]:
    """Apply the Python reference implementation's deterministic memory budget.

    The portable capsule keeps ``token_budget`` as metadata. This helper is a
    reference selection policy for memory lines, not a model-tokenizer contract
    and not a bound on the fixed prompt envelope.
    """

    selected: list[MemoryRecord] = []
    estimated_tokens = 0
    for memory in memories:
        memory_tokens = _estimated_prompt_line_tokens(memory)
        if estimated_tokens + memory_tokens > token_budget:
            continue
        selected.append(memory)
        estimated_tokens += memory_tokens
    return selected, {
        "estimated_memory_tokens": estimated_tokens,
        "selected_memories": len(selected),
        "skipped_memories": len(memories) - len(selected),
    }


def _estimated_prompt_line_tokens(memory: MemoryRecord) -> int:
    refs = ", ".join(memory.evidence_refs) if memory.evidence_refs else "none"
    line = (
        f"- {memory.id} D{memory.depth} {memory.memory_type}: "
        f"{memory.content.text} (evidence_refs: {refs})"
    )
    return len(line.split())
