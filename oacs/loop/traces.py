from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id


class TaskTrace(BaseModel):
    id: str = Field(default_factory=lambda: new_id("trace"))
    events: list[dict[str, object]] = Field(default_factory=list)
