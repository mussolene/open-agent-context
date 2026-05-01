from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.errors import ValidationFailure
from oacs.core.ids import new_id
from oacs.core.json import hash_json


class ContextCapsule(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ctx"))
    version: str = "0.1"
    capsule_type: str = "context_capsule"
    purpose: str
    task_id: str | None = None
    actor_id: str | None = None
    agent_id: str | None = None
    scope: list[str] = Field(default_factory=list)
    token_budget: int = 4000
    included_memories: list[str] = Field(default_factory=list)
    included_rules: list[str] = Field(default_factory=list)
    included_skills: list[str] = Field(default_factory=list)
    included_tools: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    forbidden_assumptions: list[str] = Field(default_factory=list)
    permissions: dict[str, bool] = Field(default_factory=dict)
    expires_at: str | None = None
    audit_refs: list[str] = Field(default_factory=list)
    checksum: str = ""

    def seal(self) -> ContextCapsule:
        data = self.model_dump()
        data.pop("checksum", None)
        self.checksum = hash_json(data)
        return self

    def validate_checksum(self) -> None:
        expected = self.model_copy(deep=True)
        provided = expected.checksum
        expected.checksum = ""
        expected.seal()
        if provided != expected.checksum:
            raise ValidationFailure("context capsule checksum mismatch")
        if self.version != "0.1" or self.capsule_type != "context_capsule":
            raise ValidationFailure("unsupported context capsule version or type")
