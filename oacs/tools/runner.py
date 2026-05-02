from __future__ import annotations

import json
import shlex
import subprocess
from typing import Any

import httpx
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from oacs.audit import AuditService
from oacs.evidence import EvidenceService
from oacs.identity.policy import PolicyEngine
from oacs.tools.local import call_local_tool
from oacs.tools.mcp import McpRegistry
from oacs.tools.mcp_client import McpClientAdapter
from oacs.tools.models import ToolBinding, ToolCallResult
from oacs.tools.registry import ToolRegistry


class ToolRunner:
    def __init__(
        self,
        registry: ToolRegistry,
        mcp: McpRegistry,
        policy: PolicyEngine,
        audit: AuditService,
        evidence: EvidenceService,
    ):
        self.registry = registry
        self.mcp = mcp
        self.policy = policy
        self.audit = audit
        self.evidence = evidence

    def call(
        self,
        tool_id: str,
        payload: dict[str, object] | None = None,
        actor_id: str | None = None,
        scope: list[str] | None = None,
        execute_mcp: bool = False,
    ) -> ToolCallResult:
        tool = self.registry.inspect(tool_id)
        call_scope = tool.scope or scope or []
        self._require_call(actor_id, tool, call_scope)
        input_payload = payload or {}
        self._validate_input(tool, input_payload)

        if tool.type == "mcp":
            output = self._call_mcp(tool, input_payload, execute_mcp)
        elif tool.type == "python_function":
            output = call_local_tool(tool.name, input_payload or {"called": True})
        elif tool.type == "local_cli":
            output = self._call_local_cli(tool, input_payload)
        elif tool.type == "http":
            output = self._call_http(tool, input_payload)
        else:
            raise ValueError(f"unsupported tool type: {tool.type}")

        self._validate_output(tool, output)
        result = ToolCallResult(
            tool_id=tool.id,
            tool_name=tool.name,
            tool_type=tool.type,
            actor_id=actor_id,
            scope=call_scope,
            input=input_payload,
            output=output,
            evidence_ref=self.evidence.record_tool_result(
                tool_id=tool.id,
                tool_name=tool.name,
                tool_type=tool.type,
                actor_id=actor_id,
                scope=call_scope,
                namespace=tool.namespace,
                input_payload=input_payload,
                output=output,
            ),
            executed=bool(output.get("executed", True)),
        )
        self.audit.record(
            "tool.call",
            actor_id,
            tool.id,
            {
                "status": result.status,
                "type": tool.type,
                "tool_call_id": result.id,
                "evidence_ref": result.evidence_ref,
            },
        )
        return result

    def _require_call(self, actor_id: str | None, tool: ToolBinding, scope: list[str]) -> None:
        if self.policy.allows(
            actor_id, "tool.call", scope=scope, namespace=tool.namespace, tool=tool.id
        ) or self.policy.allows(
            actor_id, "tool.call", scope=scope, namespace=tool.namespace, tool=tool.name
        ):
            return
        self.policy.require(
            actor_id, "tool.call", scope=scope, namespace=tool.namespace, tool=tool.id
        )

    def _call_mcp(
        self, tool: ToolBinding, payload: dict[str, object], execute_mcp: bool
    ) -> dict[str, object]:
        if not execute_mcp:
            return {
                "tool_id": tool.id,
                "mcp_ref": tool.mcp_ref,
                "executed": False,
                "reason": "MCP execution requires execute_mcp=true",
            }
        if not tool.mcp_ref:
            raise ValueError("MCP tool has no mcp_ref")
        return McpClientAdapter().call(self.mcp.inspect(tool.mcp_ref), tool, payload)

    def _call_local_cli(self, tool: ToolBinding, payload: dict[str, object]) -> dict[str, object]:
        if not tool.command:
            raise ValueError("local_cli tool requires command")
        argv = shlex.split(tool.command)
        if not argv:
            raise ValueError("local_cli tool command is empty")
        timeout = _positive_int(tool.permissions.get("timeout_sec"), default=30)
        completed = subprocess.run(
            argv,
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        output: dict[str, object] = {
            "executed": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        parsed_stdout = _json_object(completed.stdout)
        if parsed_stdout is not None:
            output["json"] = parsed_stdout
        return output

    def _call_http(self, tool: ToolBinding, payload: dict[str, object]) -> dict[str, object]:
        config = tool.http or {}
        if config.get("allow_network") is not True:
            raise ValueError("http tool execution requires http.allow_network=true")
        url = config.get("url")
        if not isinstance(url, str) or not url:
            raise ValueError("http tool requires http.url")
        method = str(config.get("method", "POST")).upper()
        timeout = _positive_int(config.get("timeout_sec"), default=30)
        response = httpx.request(method, url, json=payload, timeout=timeout)
        body: object
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return {
            "executed": True,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
        }

    @staticmethod
    def _validate_input(tool: ToolBinding, payload: dict[str, object]) -> None:
        _validate_schema(tool.input_schema, payload, "input")

    @staticmethod
    def _validate_output(tool: ToolBinding, output: dict[str, object]) -> None:
        _validate_schema(tool.output_schema, output, "output")


def _validate_schema(schema: dict[str, object], payload: dict[str, object], label: str) -> None:
    if not schema:
        return
    try:
        validate(instance=payload, schema=schema)
    except ValidationError as exc:
        path = ".".join(str(item) for item in exc.absolute_path)
        where = f" at {path}" if path else ""
        raise ValueError(f"tool {label} schema validation failed{where}: {exc.message}") from exc


def _json_object(text: str) -> dict[str, object] | None:
    try:
        parsed: Any = json.loads(text)
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _positive_int(value: object, default: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    return default
