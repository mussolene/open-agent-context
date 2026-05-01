from __future__ import annotations

from dataclasses import dataclass

from oacs.memory.models import MemoryRecord


@dataclass(frozen=True)
class ContextPolicyDecision:
    name: str
    use_memory_calls: bool
    allow_deepening: bool
    reason: str


class AdaptiveContextPolicy:
    """Choose the cheapest context path that still preserves evidence semantics."""

    def decide(
        self,
        user_request: str,
        memories: list[MemoryRecord],
        token_budget: int,
        config: dict[str, object],
    ) -> ContextPolicyDecision:
        explicit_memory_calls = config.get("memory_calls")
        allow_deepening = bool(config.get("allow_deepening", True))
        requested = str(config.get("context_policy", "auto"))
        if explicit_memory_calls is False or requested == "compact_capsule":
            return ContextPolicyDecision(
                name="compact_capsule",
                use_memory_calls=False,
                allow_deepening=False,
                reason="caller_selected_compact_context",
            )
        if requested == "memory_calls" or explicit_memory_calls is True:
            return ContextPolicyDecision(
                name="memory_calls",
                use_memory_calls=True,
                allow_deepening=allow_deepening,
                reason="caller_selected_memory_calls",
            )
        if _has_structured_evidence(memories):
            return ContextPolicyDecision(
                name="memory_calls",
                use_memory_calls=True,
                allow_deepening=allow_deepening,
                reason="structured_evidence_available",
            )
        if _estimated_tokens(user_request) <= 24 and token_budget <= 1200 and len(memories) <= 1:
            return ContextPolicyDecision(
                name="compact_capsule",
                use_memory_calls=False,
                allow_deepening=False,
                reason="tiny_task_low_memory_pressure",
            )
        return ContextPolicyDecision(
            name="memory_calls",
            use_memory_calls=True,
            allow_deepening=allow_deepening,
            reason="default_medium_or_large_context",
        )


def _has_structured_evidence(memories: list[MemoryRecord]) -> bool:
    return any(memory.content.evidence for memory in memories)


def _estimated_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)
