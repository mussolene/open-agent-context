from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

from oacs.memory.models import MemoryRecord

SLOT_ALIASES = {
    "breakfast": ("breakfast",),
    "lunch": ("lunch",),
    "dinner": ("dinner",),
    "accommodation": ("accommodation", "stay", "same place"),
    "attraction": ("attraction",),
    "transportation": ("transportation", "flight", "self-driving"),
    "evidence": ("evidence", "answer", "marker", "claim", "procedure", "command"),
}
SLOTS = tuple(SLOT_ALIASES)
DAY_WORDS = {"first": 1, "second": 2, "third": 3, "1": 1, "2": 2, "3": 3}


@dataclass(frozen=True)
class MemoryCallEvidence:
    memory_id: str
    participant: str | None
    day: int | None
    slot: str
    value: str
    reason: str
    order: int | None = None


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

    def build_prompt(self, task: str, memories: list[MemoryRecord]) -> MemoryCallLoopResult:
        intent = parse_memory_intent(task)
        memory_calls: list[MemoryCall] = [
            MemoryCall(
                id="mcall_1",
                op="memory.query",
                status="completed",
                arguments={
                    "query": task,
                    "slots": intent["slots"],
                    "days": intent["days"],
                    "referenced_participants": intent["referenced_participants"],
                },
                result={
                    "memory_ids": [memory.id for memory in memories],
                    "count": len(memories),
                },
            )
        ]
        evidence = extract_evidence(task, memories, intent)
        memory_calls.append(
            MemoryCall(
                id="mcall_2",
                op="memory.extract_evidence",
                status="completed",
                arguments={
                    "memory_ids": [memory.id for memory in memories],
                    "slots": intent["slots"],
                    "days": intent["days"],
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


def parse_memory_intent(task: str) -> dict[str, object]:
    task_lower = task.lower()
    slots = [
        slot
        for slot, aliases in SLOT_ALIASES.items()
        if any(alias in task_lower for alias in aliases)
    ]
    days = sorted(
        {
            day
            for word, day in DAY_WORDS.items()
            if re.search(rf"\b{re.escape(word)}[- ]day\b|\bday {re.escape(word)}\b", task_lower)
        }
    )
    referenced = list(
        dict.fromkeys(
            match.group(1)
            for match in re.finditer(
                r"\b(?:join|share with|same place as|same room type as|like)\s+([A-Z][a-z]+)",
                task,
            )
        )
    )
    current = re.search(r"\bI am ([A-Z][a-z]+)\b", task)
    return {
        "kind": "memory_reuse_or_constraint_resolution",
        "current_participant": current.group(1) if current else None,
        "referenced_participants": referenced,
        "slots": slots or list(SLOTS),
        "days": days,
    }


def extract_evidence(
    task: str, memories: list[MemoryRecord], intent: dict[str, object]
) -> list[MemoryCallEvidence]:
    requested_slots = set(_strings(intent.get("slots"))) or set(SLOTS)
    raw_days = intent.get("days", [])
    requested_days = (
        {day for day in raw_days if isinstance(day, int)} if isinstance(raw_days, list) else set()
    )
    raw_referenced = intent.get("referenced_participants", [])
    referenced = (
        {str(name) for name in raw_referenced} if isinstance(raw_referenced, list) else set()
    )
    focused: list[MemoryCallEvidence] = []
    broad: list[MemoryCallEvidence] = []
    for memory in memories:
        for evidence in _structured_evidence(memory, requested_slots, referenced, requested_days):
            if _is_focused(
                evidence.participant,
                evidence.day,
                evidence.slot,
                referenced,
                requested_days,
                requested_slots,
            ):
                focused.append(evidence)
            else:
                broad.append(evidence)
    return _focus_generic_evidence(_dedupe_evidence(focused or broad))


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


def _structured_evidence(
    memory: MemoryRecord,
    requested_slots: set[str],
    referenced: set[str],
    requested_days: set[int],
) -> list[MemoryCallEvidence]:
    result: list[MemoryCallEvidence] = []
    for item in memory.content.evidence:
        slot = item.slot or "evidence"
        if slot not in requested_slots and "evidence" not in requested_slots:
            continue
        if not _specific_value(item.value):
            continue
        result.append(
            MemoryCallEvidence(
                memory_id=memory.id,
                participant=item.participant,
                day=item.day,
                slot=slot,
                value=item.value,
                reason=_reason(item.participant, item.day, slot, referenced, requested_days),
                order=item.order,
            )
        )
    return result


def _specific_value(value: str) -> bool:
    return value.strip() not in {"", "-"}


def _day_number(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _is_focused(
    participant: str | None,
    day: int | None,
    slot: str,
    referenced: set[str],
    requested_days: set[int],
    requested_slots: set[str],
) -> bool:
    participant_ok = not referenced or participant in referenced
    day_ok = not requested_days or day in requested_days
    return participant_ok and day_ok and slot in requested_slots


def _reason(
    participant: str | None,
    day: int | None,
    slot: str,
    referenced: set[str],
    requested_days: set[int],
) -> str:
    bits: list[str] = []
    if referenced and participant in referenced:
        bits.append("referenced_participant")
    if requested_days and day in requested_days:
        bits.append("requested_day")
    bits.append(f"requested_slot:{slot}")
    return ",".join(bits)


def _dedupe_evidence(items: list[MemoryCallEvidence], limit: int = 12) -> list[MemoryCallEvidence]:
    seen: set[tuple[str, str, int | None, str | None, int | None]] = set()
    result: list[MemoryCallEvidence] = []
    for item in items:
        key = (item.value, item.slot, item.day, item.participant, item.order)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
        if len(result) >= limit:
            break
    return result


def _focus_generic_evidence(items: list[MemoryCallEvidence]) -> list[MemoryCallEvidence]:
    generic = [item for item in items if item.slot == "evidence"]
    structured = [item for item in items if item.slot != "evidence"]
    if not generic:
        return items
    ordered = [item for item in generic if item.order is not None]
    if ordered:
        latest = max(ordered, key=lambda item: item.order or 0)
        return structured + [latest]
    return structured + generic[:3]


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


def _strings(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


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
