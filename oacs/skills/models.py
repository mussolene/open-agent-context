from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id


class SkillManifest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("skill"))
    name: str
    description: str = ""
    version: str = "0.1.0"
    entrypoint: str = "builtin"
    instructions: str = ""
    required_memory_types: list[str] = Field(default_factory=list)
    required_rules: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    input_schema: dict[str, object] = Field(default_factory=dict)
    output_schema: dict[str, object] = Field(default_factory=dict)
    permissions: dict[str, object] = Field(default_factory=dict)
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None
