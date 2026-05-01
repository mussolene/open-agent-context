from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from oacs.memory.models import MemoryRecord

SLOT_ALIASES = {
    "breakfast": ("breakfast",),
    "lunch": ("lunch",),
    "dinner": ("dinner",),
    "accommodation": ("accommodation", "stay", "same place"),
    "attraction": ("attraction",),
    "transportation": ("transportation", "flight", "self-driving"),
    "evidence": ("accepted answer", "evidence answer", "trajectory answer"),
}
SLOTS = tuple(SLOT_ALIASES)
DAY_WORDS = {"first": 1, "second": 2, "third": 3, "1": 1, "2": 2, "3": 3}


@dataclass(frozen=True)
class MemoryToolEvidence:
    memory_id: str
    participant: str | None
    day: int | None
    slot: str
    value: str
    reason: str


@dataclass(frozen=True)
class MemoryToolLoopResult:
    intent: dict[str, object]
    operations: list[dict[str, object]]
    evidence: list[MemoryToolEvidence]
    prompt: str
    answered_deterministically: bool = False
    answer: str | None = None


class DeterministicMemoryToolLoop:
    """MCP-like deterministic memory operations before an LLM call."""

    def build_prompt(self, task: str, memories: list[MemoryRecord]) -> MemoryToolLoopResult:
        intent = parse_memory_intent(task)
        operations: list[dict[str, object]] = [
            {"tool": "intent.classify", "result": intent},
            {
                "tool": "memory.query",
                "arguments": {
                    "slots": intent["slots"],
                    "days": intent["days"],
                    "referenced_participants": intent["referenced_participants"],
                },
                "result_count": len(memories),
            },
        ]
        evidence = extract_evidence(task, memories, intent)
        operations.append(
            {
                "tool": "memory.extract_structured",
                "result_count": len(evidence),
                "evidence_values": [item.value for item in evidence],
            }
        )
        deterministic_answer = _deterministic_answer(task, evidence)
        prompt = build_tool_evidence_prompt(task, intent, evidence)
        return MemoryToolLoopResult(
            intent=intent,
            operations=operations,
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
) -> list[MemoryToolEvidence]:
    requested_slots = set(_strings(intent.get("slots"))) or set(SLOTS)
    raw_days = intent.get("days", [])
    requested_days = (
        {day for day in raw_days if isinstance(day, int)} if isinstance(raw_days, list) else set()
    )
    raw_referenced = intent.get("referenced_participants", [])
    referenced = (
        {str(name) for name in raw_referenced} if isinstance(raw_referenced, list) else set()
    )
    parsed = [_parse_memory(mem) for mem in memories]
    focused: list[MemoryToolEvidence] = []
    broad: list[MemoryToolEvidence] = []
    for item in parsed:
        if item is None:
            continue
        participant, plan, memory_id = item
        for day_plan in plan:
            if not isinstance(day_plan, dict):
                continue
            day = _day_number(day_plan.get("days"))
            for slot in requested_slots:
                value = day_plan.get(slot)
                if not isinstance(value, str) or not _specific_value(value):
                    continue
                evidence = MemoryToolEvidence(
                    memory_id=memory_id,
                    participant=participant,
                    day=day,
                    slot=slot,
                    value=value,
                    reason=_reason(participant, day, slot, referenced, requested_days),
                )
                if _is_focused(participant, day, slot, referenced, requested_days, requested_slots):
                    focused.append(evidence)
                else:
                    broad.append(evidence)
    return _focus_generic_evidence(_dedupe_evidence(focused or broad))


def build_tool_evidence_prompt(
    task: str, intent: dict[str, object], evidence: list[MemoryToolEvidence]
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
            "You are an agent using OACS memory tools.",
            "The deterministic memory layer already queried and read scoped memory.",
            "Use only the evidence values below when they answer the task.",
            "Preserve exact names and strings from evidence.",
            f"Intent: {json.dumps(intent, ensure_ascii=False, sort_keys=True)}",
            "Evidence:",
            "\n".join(evidence_lines) or "- none",
            "Task:",
            task,
            'Return JSON: {"answer":"...","used_evidence":[],"confidence":0.0,'
            '"needs_clarification":false,"policy_notes":[]}',
        ]
    )


def _parse_memory(memory: MemoryRecord) -> tuple[str | None, list[Any], str] | None:
    text = memory.content.text
    participant = _participant_from_text(text)
    if "Exact accepted plan:\n" in text:
        payload = text.split("Exact accepted plan:\n", 1)[1]
        plan = _load_json(payload)
        if isinstance(plan, list):
            return participant, plan, memory.id
    if "base plan:\n" in text:
        payload = text.split("base plan:\n", 1)[1]
        base = _load_json(payload)
        if isinstance(base, dict):
            plan = base.get("daily_plans")
            name = base.get("name")
            if isinstance(name, str):
                participant = name
            if isinstance(plan, list):
                return participant, plan, memory.id
    for marker in ("Accepted answer:\n", "AMA-Bench evidence answer:\n"):
        if marker in text:
            payload = text.split(marker, 1)[1].strip()
            if _specific_value(payload):
                day = _generic_memory_order(text)
                plan = {"evidence": payload}
                if day is not None:
                    plan["days"] = day
                return participant, [plan], memory.id
    return None


def _participant_from_text(text: str) -> str | None:
    match = re.search(r"\bI am ([A-Z][a-z]+)\b", text)
    if match:
        return match.group(1)
    name_match = re.search(r'"name"\s*:\s*"([^"]+)"', text)
    return name_match.group(1) if name_match else None


def _load_json(payload: str) -> Any:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


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


def _dedupe_evidence(items: list[MemoryToolEvidence], limit: int = 12) -> list[MemoryToolEvidence]:
    seen: set[tuple[str, str, int | None, str | None]] = set()
    result: list[MemoryToolEvidence] = []
    for item in items:
        key = (item.value, item.slot, item.day, item.participant)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
        if len(result) >= limit:
            break
    return result


def _focus_generic_evidence(items: list[MemoryToolEvidence]) -> list[MemoryToolEvidence]:
    generic = [item for item in items if item.slot == "evidence"]
    structured = [item for item in items if item.slot != "evidence"]
    if not generic:
        return items
    ordered = [item for item in generic if item.day is not None]
    if ordered:
        latest = max(ordered, key=lambda item: item.day or 0)
        return structured + [latest]
    return structured + generic[:3]


def _generic_memory_order(text: str) -> int | None:
    match = re.search(r"\bprior question (\d+)\b", text)
    return int(match.group(1)) + 1 if match else None


def _deterministic_answer(task: str, evidence: list[MemoryToolEvidence]) -> str | None:
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
