from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.context.builder import ContextBuilder
from oacs.loop.intent import classify_intent
from oacs.memory.service import MemoryService


class MemoryLoopResult(BaseModel):
    final_answer: str
    context_capsule_id: str
    memories_used: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    proposed_memories: list[str] = Field(default_factory=list)
    committed_memories: list[str] = Field(default_factory=list)
    audit_trail: list[str] = Field(default_factory=list)
    benchmark_metrics: dict[str, object] = Field(default_factory=dict)


class MemoryLoopEngine:
    def __init__(self, memory: MemoryService, context_builder: ContextBuilder):
        self.memory = memory
        self.context_builder = context_builder

    def run(
        self,
        user_request: str,
        actor_id: str | None,
        agent_id: str | None = None,
        scope: list[str] | None = None,
        token_budget: int = 4000,
        allowed_tools: list[str] | None = None,
        model_config: dict[str, object] | None = None,
    ) -> MemoryLoopResult:
        intent = classify_intent(user_request)
        self.memory.observe(user_request, actor_id, scope or [])
        capsule = self.context_builder.build(intent, actor_id, agent_id, scope or [], token_budget)
        memories = [self.memory.read(mid, actor_id) for mid in capsule.included_memories]
        facts = [
            m.content.text for m in memories if m.depth <= 2 and m.lifecycle_status == "active"
        ]
        hypotheses = [m.content.text for m in memories if m.depth >= 3]
        answer_parts = []
        if facts:
            answer_parts.append("Relevant facts: " + " ".join(facts))
        if hypotheses:
            answer_parts.append("Hypotheses only: " + " ".join(hypotheses))
        answer_parts.append(f"Task: {user_request}")
        proposed = self.memory.propose(
            "episode", 1, f"Task handled: {user_request}", actor_id, scope or []
        )
        return MemoryLoopResult(
            final_answer="\n".join(answer_parts),
            context_capsule_id=capsule.id,
            memories_used=capsule.included_memories,
            tools_used=allowed_tools or [],
            rules_applied=capsule.included_rules,
            proposed_memories=[proposed.id],
            benchmark_metrics={"tokens_estimated": len(" ".join(answer_parts).split())},
        )
