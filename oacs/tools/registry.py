from __future__ import annotations

from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository
from oacs.tools.models import ToolBinding


def builtin_tools() -> list[ToolBinding]:
    return [
        ToolBinding(
            id="tool_local_echo",
            name="local_echo",
            type="python_function",
            description="Deterministic local echo tool for POC exercises.",
        )
    ]


class ToolRegistry:
    def __init__(self, repo: Repository):
        self.repo = repo

    def ensure_builtin(self) -> None:
        existing = {row["id"] for row in self.repo.list()}
        for tool in builtin_tools():
            if tool.id not in existing:
                self.add(tool)

    def add(self, tool: ToolBinding) -> ToolBinding:
        now = now_iso()
        manifest = tool.model_dump()
        self.repo.save(
            {
                "id": tool.id,
                "name": tool.name,
                "type": tool.type,
                "manifest": manifest,
                "risk_level": tool.risk_level,
                "status": tool.status,
                "namespace": "default",
                "scope": [],
                "owner_actor_id": None,
                "created_at": now,
                "updated_at": now,
                "content_hash": hash_json(manifest),
            }
        )
        return tool

    def list(self) -> list[ToolBinding]:
        self.ensure_builtin()
        return [ToolBinding(**row["manifest"]) for row in self.repo.list("WHERE status='active'")]

    def inspect(self, tool_id: str) -> ToolBinding:
        for tool in self.list():
            if tool.id == tool_id or tool.name == tool_id:
                return tool
        raise KeyError(f"tool not found: {tool_id}")
