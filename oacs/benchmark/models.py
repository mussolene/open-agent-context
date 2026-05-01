from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id


class BenchmarkTask(BaseModel):
    id: str = Field(default_factory=lambda: new_id("bench"))
    type: str
    setup_memories: list[dict[str, object]]
    user_prompt: str
    expected_facts: list[str]
    forbidden_facts: list[str] = Field(default_factory=list)
    rubric: dict[str, object] = Field(default_factory=dict)


class BenchmarkRun(BaseModel):
    id: str = Field(default_factory=lambda: new_id("run"))
    mode: str
    task_results: list[dict[str, object]]
    summary: dict[str, object]
