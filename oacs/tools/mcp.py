from __future__ import annotations

import json
from pathlib import Path

from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository
from oacs.tools.models import McpBinding, ToolBinding
from oacs.tools.registry import ToolRegistry


class McpRegistry:
    def __init__(self, repo: Repository, tools: ToolRegistry):
        self.repo = repo
        self.tools = tools

    def import_config(self, path: str) -> list[McpBinding]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        servers = data.get("mcpServers", data)
        imported: list[McpBinding] = []
        for name, cfg in servers.items():
            binding = McpBinding(
                name=name,
                server_name=name,
                command=cfg.get("command"),
                args=cfg.get("args", []),
                env=cfg.get("env", {}),
                allowed_tools=cfg.get("allowed_tools", cfg.get("tools", [])),
            )
            self.add(binding)
            for tool_name in binding.allowed_tools:
                self.tools.add(
                    ToolBinding(
                        name=tool_name,
                        type="mcp",
                        mcp_ref=binding.id,
                        risk_level=binding.risk_level,
                    )
                )
            imported.append(binding)
        return imported

    def add(self, binding: McpBinding) -> McpBinding:
        now = now_iso()
        manifest = binding.model_dump()
        self.repo.save(
            {
                "id": binding.id,
                "name": binding.name,
                "server_name": binding.server_name,
                "transport": binding.transport,
                "manifest": manifest,
                "risk_level": binding.risk_level,
                "status": binding.status,
                "namespace": "default",
                "scope": [],
                "owner_actor_id": None,
                "created_at": now,
                "updated_at": now,
                "content_hash": hash_json(manifest),
            }
        )
        return binding

    def list(self) -> list[McpBinding]:
        return [
            McpBinding(**row["manifest"])
            for row in self.repo.list(filters={"status": "active"})
        ]

    def inspect(self, binding_id: str) -> McpBinding:
        for binding in self.list():
            if binding.id == binding_id or binding.name == binding_id:
                return binding
        raise KeyError(f"mcp binding not found: {binding_id}")
