from __future__ import annotations

import json
import subprocess
from typing import Any

from oacs.core.errors import ValidationFailure
from oacs.tools.models import McpBinding, ToolBinding


class McpClientAdapter:
    """Small stdio MCP execution adapter for explicitly granted bindings."""

    def call(
        self,
        binding: McpBinding,
        tool: ToolBinding,
        payload: dict[str, object],
        timeout_sec: int = 15,
    ) -> dict[str, object]:
        if binding.transport != "stdio" or not binding.command:
            raise ValidationFailure("MCP execution requires a stdio binding with a command")
        if tool.name not in binding.allowed_tools:
            raise ValidationFailure(f"tool is not allowed by MCP binding: {tool.name}")
        request = {
            "jsonrpc": "2.0",
            "id": "oacs-tool-call-1",
            "method": "tools/call",
            "params": {"name": tool.name, "arguments": payload},
        }
        try:
            result = subprocess.run(
                [binding.command, *binding.args],
                input=json.dumps(request, ensure_ascii=False) + "\n",
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout_sec,
                env={**binding.env} if binding.env else None,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValidationFailure("MCP stdio call failed") from exc
        if result.returncode != 0:
            raise ValidationFailure("MCP stdio command returned non-zero exit status")
        return _parse_json_response(result.stdout)


def _parse_json_response(output: str) -> dict[str, object]:
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parsed: Any = json.loads(line)
        if isinstance(parsed, dict):
            return parsed
    raise ValidationFailure("MCP stdio command did not return a JSON object")
