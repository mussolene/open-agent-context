from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from oacs.core.ids import new_id
from oacs.core.time import now_iso

MemoryStatus = Literal[
    "observed",
    "candidate",
    "clarifying",
    "confirmed",
    "active",
    "deprecated",
    "superseded",
    "forgotten",
]


class EvidenceItem(BaseModel):
    evidence_kind: str = "claim"
    claim: str
    value: str
    source_ref: str | None = None
    confidence: float = 1.0
    depth: int | None = Field(default=None, ge=0, le=5)
    scope: list[str] = Field(default_factory=list)
    participant: str | None = None
    day: int | None = None
    slot: str = "evidence"
    order: int | None = None
    trajectory_step: int | None = None


class MemoryContent(BaseModel):
    text: str
    kind: str = "fact"
    tags: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    evidence: list[EvidenceItem] = Field(default_factory=list)


class MemoryRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("mem"))
    memory_type: str
    depth: int = Field(ge=0, le=5)
    lifecycle_status: MemoryStatus = "candidate"
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None
    content: MemoryContent
    evidence_refs: list[str] = Field(default_factory=list)
    supersedes: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    content_hash: str = ""
