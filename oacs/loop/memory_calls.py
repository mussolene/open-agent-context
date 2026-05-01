from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from oacs.loop.evidence_selectors import (
    EvidenceSelector,
    MemoryCallEvidence,
    StructuredEvidenceSelector,
)
from oacs.memory.models import MemoryRecord


@dataclass(frozen=True)
class MemoryCall:
    id: str
    op: str
    status: Literal["completed", "denied", "failed"]
    arguments: dict[str, object]
    result: dict[str, object]


@dataclass(frozen=True)
class MemoryCallLoopResult:
    intent: dict[str, object]
    memory_calls: list[MemoryCall]
    evidence: list[MemoryCallEvidence]
    prompt: str
    answered_deterministically: bool = False
    answer: str | None = None


class DeterministicMemoryCallLoop:
    """Deterministic OACS memory_calls before an LLM call."""

    def __init__(
        self, selector: EvidenceSelector | None = None, include_read: bool = False
    ) -> None:
        self.selector = selector or StructuredEvidenceSelector()
        self.include_read = include_read

    def build_prompt(self, task: str, memories: list[MemoryRecord]) -> MemoryCallLoopResult:
        selection = self.selector.select(task, memories)
        intent = selection.intent
        memory_calls: list[MemoryCall] = [
            MemoryCall(
                id="mcall_1",
                op="memory.query",
                status="completed",
                arguments={
                    "query": task,
                    "selectors": intent.get("selectors", {}),
                    "slots": intent.get("slots", []),
                    "days": intent.get("days", []),
                    "referenced_participants": intent.get("referenced_participants", []),
                },
                result={
                    "memory_ids": [memory.id for memory in memories],
                    "count": len(memories),
                },
            )
        ]
        if self.include_read:
            memory_calls.append(
                MemoryCall(
                    id="mcall_2",
                    op="memory.read",
                    status="completed",
                    arguments={
                        "memory_ids": [memory.id for memory in memories],
                    },
                    result={
                        "memories": [
                            {
                                "id": memory.id,
                                "depth": memory.depth,
                                "memory_type": memory.memory_type,
                                "lifecycle_status": memory.lifecycle_status,
                                "content_hash": memory.content_hash,
                            }
                            for memory in memories
                        ],
                        "count": len(memories),
                    },
                )
            )
        evidence = selection.evidence
        memory_calls.append(
            MemoryCall(
                id=f"mcall_{len(memory_calls) + 1}",
                op="memory.extract_evidence",
                status="completed",
                arguments={
                    "memory_ids": [memory.id for memory in memories],
                    "selectors": intent.get("selectors", {}),
                    "slots": intent.get("slots", []),
                    "days": intent.get("days", []),
                },
                result={
                    "count": len(evidence),
                    "evidence": [item_to_dict(item) for item in evidence],
                },
            )
        )
        deterministic_answer = _deterministic_answer(task, evidence)
        prompt = build_memory_call_prompt(task, intent, memory_calls, evidence)
        return MemoryCallLoopResult(
            intent=intent,
            memory_calls=memory_calls,
            evidence=evidence,
            prompt=prompt,
            answered_deterministically=deterministic_answer is not None,
            answer=deterministic_answer,
        )


def build_memory_call_prompt(
    task: str,
    intent: dict[str, object],
    memory_calls: list[MemoryCall],
    evidence: list[MemoryCallEvidence],
) -> str:
    evidence_lines = [
        (
            f"- participant={item.participant or 'unknown'} day={item.day or 'unknown'} "
            f"slot={item.slot} value={item.value!r} source={item.memory_id} reason={item.reason}"
        )
        for item in evidence
    ]
    return "\n".join(
        [
            "You are an agent operating over OACS memory_calls.",
            "The deterministic memory layer already executed the memory_calls below.",
            "Use only the evidence values below when they answer the task.",
            "Preserve exact names and strings from evidence.",
            f"Intent: {json.dumps(intent, ensure_ascii=False, sort_keys=True)}",
            "Memory calls:",
            "\n".join(_memory_call_prompt_line(call) for call in memory_calls),
            "Evidence:",
            "\n".join(evidence_lines) or "- none",
            "Task:",
            task,
            'Return JSON: {"answer":"...","used_evidence":[],"confidence":0.0,'
            '"needs_clarification":false,"policy_notes":[]}',
        ]
    )


def _deterministic_answer(task: str, evidence: list[MemoryCallEvidence]) -> str | None:
    if not evidence:
        return None
    values = ", ".join(dict.fromkeys(item.value for item in evidence))
    return (
        '{"answer":'
        + json.dumps(values, ensure_ascii=False)
        + ',"used_evidence":'
        + json.dumps([item.memory_id for item in evidence], ensure_ascii=False)
        + ',"confidence":0.9,"needs_clarification":false,"policy_notes":[]}'
    )


def item_to_dict(item: MemoryCallEvidence) -> dict[str, object]:
    return {
        "memory_id": item.memory_id,
        "participant": item.participant,
        "day": item.day,
        "slot": item.slot,
        "value": item.value,
        "reason": item.reason,
        "order": item.order,
    }


def memory_call_to_dict(call: MemoryCall) -> dict[str, object]:
    return {
        "id": call.id,
        "op": call.op,
        "status": call.status,
        "arguments": call.arguments,
        "result": call.result,
    }


def _memory_call_prompt_line(call: MemoryCall) -> str:
    count = call.result.get("count")
    count_text = f" count={count}" if count is not None else ""
    return f"- {call.id} op={call.op} status={call.status}{count_text}"
