from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id


class ToolBinding(BaseModel):
    id: str = Field(default_factory=lambda: new_id("tool"))
    name: str
    type: str
    description: str = ""
    command: str | None = None
    http: dict[str, object] | None = None
    mcp_ref: str | None = None
    input_schema: dict[str, object] = Field(default_factory=dict)
    output_schema: dict[str, object] = Field(default_factory=dict)
    permissions: dict[str, object] = Field(default_factory=dict)
    risk_level: str = "low"
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None


class ToolCallResult(BaseModel):
    id: str = Field(default_factory=lambda: new_id("toolcall"))
    tool_id: str
    tool_name: str
    tool_type: str
    actor_id: str | None = None
    scope: list[str] = Field(default_factory=list)
    input: dict[str, object] = Field(default_factory=dict)
    output: dict[str, object] = Field(default_factory=dict)
    evidence_ref: str | None = None
    executed: bool = True
    status: str = "completed"


class McpBinding(BaseModel):
    id: str = Field(default_factory=lambda: new_id("mcp"))
    name: str
    server_name: str
    transport: str = "stdio"
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    risk_level: str = "medium"
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None
