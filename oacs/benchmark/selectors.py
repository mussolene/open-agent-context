from __future__ import annotations

from oacs.loop.evidence_selectors import (
    EvidenceSelection,
    MemoryCallEvidence,
    dedupe_evidence,
    focus_generic_evidence,
    is_focused,
    memory_evidence,
    strings,
)
from oacs.memory.models import MemoryRecord


class MemoryArenaTravelSelector:
    """MemoryArena selector over adapter-provided participant/day/slot selectors."""

    def __init__(self, selectors: dict[str, object]) -> None:
        self.selectors = selectors

    def select(self, task: str, memories: list[MemoryRecord]) -> EvidenceSelection:
        intent: dict[str, object] = {
            "kind": "memoryarena_travel_evidence_retrieval",
            "selectors": self.selectors,
            "slots": strings(self.selectors.get("slots")),
            "days": _ints(self.selectors.get("days")),
            "referenced_participants": strings(self.selectors.get("participants")),
        }
        evidence = self.extract_evidence(memories, intent)
        return EvidenceSelection(intent=intent, evidence=evidence)

    def extract_evidence(
        self, memories: list[MemoryRecord], intent: dict[str, object]
    ) -> list[MemoryCallEvidence]:
        requested_slots = set(strings(intent.get("slots")))
        requested_days = set(_ints(intent.get("days")))
        referenced = set(strings(intent.get("referenced_participants")))
        focused: list[MemoryCallEvidence] = []
        broad: list[MemoryCallEvidence] = []
        for memory in memories:
            for evidence in memory_evidence(
                memory,
                requested_slots=requested_slots,
                referenced=referenced,
                requested_days=requested_days,
            ):
                if is_focused(
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
        return focus_generic_evidence(dedupe_evidence(focused or broad))


def _ints(value: object) -> list[int]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, int)]
    return []
