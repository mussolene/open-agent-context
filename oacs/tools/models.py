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
