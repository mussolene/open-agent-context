from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso


class RuleManifest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("rule"))
    name: str
    scope: list[str] = Field(default_factory=list)
    namespace: str = "default"
    priority: int = 100
    rule_kind: str
    content: str
    applies_to: list[str] = Field(default_factory=list)
    enforcement_mode: str = "warn"
    blocking: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    status: str = "active"
    owner_actor_id: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    content_hash: str = ""

    def to_record(self) -> dict[str, object]:
        data = self.model_dump()
        data["content_hash"] = hash_json({k: v for k, v in data.items() if k != "content_hash"})
        return data


class RuleResult(BaseModel):
    rule_id: str
    name: str
    status: str
    message: str
    blocking: bool = False
