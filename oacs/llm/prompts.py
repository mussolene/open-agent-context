from __future__ import annotations

from oacs.context.capsule import ContextCapsule
from oacs.memory.models import MemoryRecord

BASELINE_SYSTEM = "You are a helpful assistant. Solve the task."
OACS_SYSTEM = (
    "You are an agent operating inside OACS. Use the provided Context Capsule. "
    "Respect rules, capabilities, memory depth constraints and evidence. "
    "D3-D5 memory is hypothesis only. D0-D2 may support factual answers. "
    "If required facts are missing, ask clarification."
)


def build_oacs_prompt(task: str, capsule: ContextCapsule, memories: list[MemoryRecord]) -> str:
    facts = [m for m in memories if m.depth <= 2]
    fuzzy = [m for m in memories if m.depth >= 3]
    capsule_view = {
        "id": capsule.id,
        "purpose": capsule.purpose,
        "scope": capsule.scope,
        "token_budget": capsule.token_budget,
        "included_memories": capsule.included_memories,
        "included_rules": capsule.included_rules,
        "forbidden_assumptions": capsule.forbidden_assumptions,
        "permissions": capsule.permissions,
    }
    return "\n".join(
        [
            f"Task: {task}",
            f"Context Capsule: {capsule_view}",
            "Relevant D0-D2 facts/procedures:",
            "\n".join(f"- {m.id}: {m.content.text}" for m in facts) or "- none",
            "D3-D5 hypotheses only:",
            "\n".join(f"- {m.id}: {m.content.text}" for m in fuzzy) or "- none",
            'Output JSON: {"answer":"...","used_memories":[],"confidence":0.0,'
            '"needs_clarification":false,"policy_notes":[]}',
        ]
    )
