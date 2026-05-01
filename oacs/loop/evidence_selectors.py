from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from oacs.memory.models import MemoryRecord


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
class EvidenceSelection:
    intent: dict[str, object]
    evidence: list[MemoryCallEvidence]


class EvidenceSelector(Protocol):
    def select(self, task: str, memories: list[MemoryRecord]) -> EvidenceSelection:
        """Return a structured intent and selected evidence for a memory call."""


class StructuredEvidenceSelector:
    """Generic selector over typed MemoryRecord.content.evidence fields."""

    def select(self, task: str, memories: list[MemoryRecord]) -> EvidenceSelection:
        intent: dict[str, object] = {
            "kind": "structured_evidence_retrieval",
            "query": task,
            "selectors": {},
        }
        evidence: list[MemoryCallEvidence] = []
        for memory in memories:
            evidence.extend(memory_evidence(memory, reason="structured_evidence"))
        return EvidenceSelection(intent=intent, evidence=focus_generic_evidence(evidence))


def memory_evidence(
    memory: MemoryRecord,
    requested_slots: set[str] | None = None,
    referenced: set[str] | None = None,
    requested_days: set[int] | None = None,
    reason: str | None = None,
) -> list[MemoryCallEvidence]:
    result: list[MemoryCallEvidence] = []
    for item in memory.content.evidence:
        slot = item.slot or "evidence"
        if (
            requested_slots is not None
            and slot not in requested_slots
            and "evidence" not in requested_slots
        ):
            continue
        if not item.value.strip():
            continue
        result.append(
            MemoryCallEvidence(
                memory_id=memory.id,
                participant=item.participant,
                day=item.day,
                slot=slot,
                value=item.value,
                reason=reason
                or evidence_reason(
                    item.participant,
                    item.day,
                    slot,
                    referenced or set(),
                    requested_days or set(),
                ),
                order=item.order,
            )
        )
    return result


def is_focused(
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


def evidence_reason(
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


def dedupe_evidence(items: list[MemoryCallEvidence], limit: int = 12) -> list[MemoryCallEvidence]:
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


def focus_generic_evidence(items: list[MemoryCallEvidence]) -> list[MemoryCallEvidence]:
    generic = [item for item in items if item.slot == "evidence"]
    structured = [item for item in items if item.slot != "evidence"]
    if not generic:
        return items
    ordered = [item for item in generic if item.order is not None]
    if ordered:
        latest = max(ordered, key=lambda item: item.order or 0)
        return structured + [latest]
    return structured + generic[:3]


def strings(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []
