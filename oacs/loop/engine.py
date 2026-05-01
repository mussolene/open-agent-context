from __future__ import annotations

from dataclasses import replace

from pydantic import BaseModel, Field

from oacs.context.builder import ContextBuilder
from oacs.loop.context_policy import AdaptiveContextPolicy
from oacs.loop.intent import classify_intent
from oacs.loop.memory_calls import (
    DeterministicMemoryCallLoop,
    MemoryCall,
    build_memory_call_prompt,
    item_to_dict,
    memory_call_to_dict,
)
from oacs.memory.models import MemoryRecord
from oacs.memory.service import MemoryService


class MemoryLoopResult(BaseModel):
    final_answer: str
    context_capsule_id: str
    intent: dict[str, object] = Field(default_factory=dict)
    memories_used: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    rules_applied: list[str] = Field(default_factory=list)
    proposed_memories: list[str] = Field(default_factory=list)
    committed_memories: list[str] = Field(default_factory=list)
    audit_trail: list[str] = Field(default_factory=list)
    memory_calls: list[dict[str, object]] = Field(default_factory=list)
    evidence: list[dict[str, object]] = Field(default_factory=list)
    model_prompt: str | None = None
    context_policy: dict[str, object] = Field(default_factory=dict)
    operation_metrics: dict[str, object] = Field(default_factory=dict)


class MemoryLoopEngine:
    def __init__(self, memory: MemoryService, context_builder: ContextBuilder):
        self.memory = memory
        self.context_builder = context_builder
        self.context_policy = AdaptiveContextPolicy()

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
        config = model_config or {}
        checked_tools = self._authorized_tools(actor_id, allowed_tools or [], scope or [])
        intent_name = classify_intent(user_request)
        intent: dict[str, object] = {"name": intent_name, "query": user_request}
        self.memory.observe(user_request, actor_id, scope or [])
        capsule = self.context_builder.build(
            intent_name, actor_id, agent_id, scope or [], token_budget
        )
        memories = [self.memory.read(mid, actor_id) for mid in capsule.included_memories]
        context_policy = self.context_policy.decide(user_request, memories, token_budget, config)
        memory_call_payload: list[dict[str, object]] = []
        evidence_payload: list[dict[str, object]] = []
        model_prompt: str | None = None
        if context_policy.use_memory_calls:
            call_result = DeterministicMemoryCallLoop(include_read=True).build_prompt(
                user_request, memories
            )
            if not call_result.evidence and context_policy.allow_deepening:
                deepened = self._deepen_if_needed(user_request, actor_id, scope or [], memories)
                if len(deepened) > len(memories):
                    existing_ids = {memory.id for memory in memories}
                    deepened_ids = [
                        memory.id for memory in deepened if memory.id not in existing_ids
                    ]
                    memories = deepened
                    call_result = DeterministicMemoryCallLoop(include_read=True).build_prompt(
                        user_request, memories
                    )
                    call_result.memory_calls.insert(
                        1,
                        MemoryCall(
                            id="mcall_deepen",
                            op="memory.query.deepen",
                            status="completed",
                            arguments={
                                "query": user_request,
                                "original_scope": scope or [],
                            },
                            result={
                                "memory_ids": deepened_ids,
                                "count": len(deepened_ids),
                            },
                        ),
                    )
                    call_result = replace(
                        call_result,
                        prompt=build_memory_call_prompt(
                            user_request,
                            call_result.intent,
                            call_result.memory_calls,
                            call_result.evidence,
                        ),
                    )
            intent = intent | {"memory_call_intent": call_result.intent}
            memory_call_payload = [memory_call_to_dict(call) for call in call_result.memory_calls]
            evidence_payload = [item_to_dict(item) for item in call_result.evidence]
            model_prompt = call_result.prompt
        facts = [
            m.content.text for m in memories if m.depth <= 2 and m.lifecycle_status == "active"
        ]
        hypotheses = [m.content.text for m in memories if m.depth >= 3]
        answer_parts = []
        if facts:
            answer_parts.append("Relevant facts: " + " ".join(facts))
        if hypotheses:
            answer_parts.append("Hypotheses only: " + " ".join(hypotheses))
        if evidence_payload:
            answer_parts.append(
                "Selected evidence: "
                + " ".join(str(item.get("value", "")) for item in evidence_payload)
            )
        answer_parts.append(f"Task: {user_request}")
        proposed = self.memory.propose(
            "episode", 1, f"Task handled: {user_request}", actor_id, scope or []
        )
        return MemoryLoopResult(
            final_answer="\n".join(answer_parts),
            context_capsule_id=capsule.id,
            intent=intent,
            memories_used=[memory.id for memory in memories],
            tools_used=checked_tools,
            rules_applied=capsule.included_rules,
            proposed_memories=[proposed.id],
            memory_calls=memory_call_payload,
            evidence=evidence_payload,
            model_prompt=model_prompt,
            context_policy={
                "name": context_policy.name,
                "use_memory_calls": context_policy.use_memory_calls,
                "allow_deepening": context_policy.allow_deepening,
                "reason": context_policy.reason,
            },
            operation_metrics={
                "tokens_estimated": len(" ".join(answer_parts).split()),
                "memory_calls_count": len(memory_call_payload),
                "evidence_items": len(evidence_payload),
            },
        )

    def _deepen_if_needed(
        self,
        user_request: str,
        actor_id: str | None,
        scope: list[str],
        memories: list[MemoryRecord],
    ) -> list[MemoryRecord]:
        if not scope:
            return memories
        if actor_id not in (None, "", "system"):
            return memories
        deepened = self.memory.query(user_request, actor_id, [])
        seen = {memory.id for memory in memories}
        return memories + [memory for memory in deepened if memory.id not in seen]

    def _authorized_tools(
        self, actor_id: str | None, allowed_tools: list[str], scope: list[str]
    ) -> list[str]:
        checked: list[str] = []
        for requested in allowed_tools:
            tool = self.context_builder.tools.inspect(requested)
            check_scope = tool.scope or scope
            if not (
                self.context_builder.policy.allows(
                    actor_id,
                    "tool.call",
                    scope=check_scope,
                    namespace=tool.namespace,
                    tool=tool.id,
                )
                or self.context_builder.policy.allows(
                    actor_id,
                    "tool.call",
                    scope=check_scope,
                    namespace=tool.namespace,
                    tool=tool.name,
                )
            ):
                self.context_builder.policy.require(
                    actor_id,
                    "tool.call",
                    scope=check_scope,
                    namespace=tool.namespace,
                    tool=tool.id,
                )
            checked.append(tool.id)
        return checked
