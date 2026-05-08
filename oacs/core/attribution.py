from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AttributionRole = Literal[
    "user_instruction",
    "agent_decision",
    "tool_observation",
    "project_policy",
    "human_approval",
    "derived_memory",
    "system_policy",
]

AttributionActorType = Literal[
    "human",
    "agent",
    "tool",
    "service",
    "application",
    "organization",
    "system",
]


class Attribution(BaseModel):
    source_actor_id: str | None = None
    source_actor_type: AttributionActorType | None = None
    recorded_by_actor_id: str | None = None
    role: AttributionRole
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
