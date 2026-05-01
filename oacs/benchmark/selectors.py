from __future__ import annotations

import re

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
    """MemoryArena group-travel selector over participant/day/slot evidence."""

    SLOT_ALIASES = {
        "breakfast": ("breakfast",),
        "lunch": ("lunch",),
        "dinner": ("dinner",),
        "accommodation": ("accommodation", "stay", "same place"),
        "attraction": ("attraction",),
        "transportation": ("transportation", "flight", "self-driving"),
        "evidence": ("evidence", "answer", "marker", "claim", "procedure", "command"),
    }
    DAY_WORDS = {"first": 1, "second": 2, "third": 3, "1": 1, "2": 2, "3": 3}

    def select(self, task: str, memories: list[MemoryRecord]) -> EvidenceSelection:
        intent = self.parse_intent(task)
        evidence = self.extract_evidence(memories, intent)
        return EvidenceSelection(intent=intent, evidence=evidence)

    def parse_intent(self, task: str) -> dict[str, object]:
        task_lower = task.lower()
        slots = [
            slot
            for slot, aliases in self.SLOT_ALIASES.items()
            if any(alias in task_lower for alias in aliases)
        ]
        days = sorted(
            {
                day
                for word, day in self.DAY_WORDS.items()
                if re.search(
                    rf"\b{re.escape(word)}[- ]day\b|\bday {re.escape(word)}\b",
                    task_lower,
                )
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
            "kind": "memoryarena_travel_evidence_retrieval",
            "current_participant": current.group(1) if current else None,
            "referenced_participants": referenced,
            "slots": slots or list(self.SLOT_ALIASES),
            "days": days,
        }

    def extract_evidence(
        self, memories: list[MemoryRecord], intent: dict[str, object]
    ) -> list[MemoryCallEvidence]:
        requested_slots = set(strings(intent.get("slots"))) or set(self.SLOT_ALIASES)
        raw_days = intent.get("days", [])
        requested_days = (
            {day for day in raw_days if isinstance(day, int)}
            if isinstance(raw_days, list)
            else set()
        )
        raw_referenced = intent.get("referenced_participants", [])
        referenced = (
            {str(name) for name in raw_referenced} if isinstance(raw_referenced, list) else set()
        )
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
