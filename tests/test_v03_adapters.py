from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from oacs.api.server import create_app
from oacs.app import services
from oacs.cli.main import _evidence_ingest_grant_hint, app
from oacs.core.errors import AccessDenied
from oacs.tools.models import ToolBinding


def test_tool_and_skill_capability_allowlists_are_enforced(svc) -> None:
    actor = svc.actors.create("agent", "AdapterAgent")

    with pytest.raises(AccessDenied):
        svc.policy.require(actor.id, "tool.call", tool="tool_local_echo")

    svc.capabilities.grant(
        actor.id,
        "system",
        ["tool.call", "skill.run"],
        tools_allowed=["tool_local_echo"],
        skills_allowed=["skill_task_trace_distiller"],
    )

    assert svc.policy.allows(actor.id, "tool.call", tool="tool_local_echo")
    assert not svc.policy.allows(actor.id, "tool.call", tool="other_tool")
    assert svc.policy.allows(actor.id, "skill.run", skill="skill_task_trace_distiller")
    assert not svc.policy.allows(actor.id, "skill.run", skill="skill_memory_critical_solver")


def test_context_build_filters_tools_and_skills_by_actor_grants(svc) -> None:
    actor = svc.actors.create("agent", "CapsuleAdapterAgent")
    svc.capabilities.grant(actor.id, "system", ["context.build", "memory.query", "memory.read"])
    capsule = svc.context.build("adapter task", actor.id, scope=[])
    assert capsule.included_tools == []
    assert capsule.included_skills == []

    svc.capabilities.grant(
        actor.id,
        "system",
        ["tool.call", "skill.run"],
        tools_allowed=["tool_local_echo"],
        skills_allowed=["skill_task_trace_distiller"],
    )
    capsule = svc.context.build("adapter task", actor.id, scope=[])
    assert capsule.included_tools == ["tool_local_echo"]
    assert capsule.included_skills == ["skill_task_trace_distiller"]


def test_loop_rejects_unauthorized_allowed_tools(svc) -> None:
    actor = svc.actors.create("agent", "LoopToolAgent")
    svc.capabilities.grant(actor.id, "system", ["context.build", "memory.observe"])

    with pytest.raises(AccessDenied):
        svc.loop.run("use a tool", actor.id, allowed_tools=["tool_local_echo"])


def test_audit_chain_verify_detects_tampering(svc) -> None:
    first = svc.audit.record("test.first", "actor")
    svc.audit.record("test.second", "actor")
    assert svc.audit.verify_chain()["valid"] is True

    row = svc.store.get("audit_events", first["id"])
    row["metadata"] = {"tampered": True}
    svc.store.put_json("audit_events", row)

    result = svc.audit.verify_chain()
    assert result["valid"] is False
    assert result["errors"][0]["error"] == "content_hash_mismatch"


def test_cli_tool_and_skill_calls_require_resource_grants(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    actor = runner.invoke(
        app,
        ["actor", "create", "--db", str(db), "--type", "agent", "--name", "ToolAgent", "--json"],
    )
    actor_id = json.loads(actor.output)["id"]

    denied = runner.invoke(
        app,
        ["tool", "call", "local_echo", "--db", str(db), "--actor", actor_id, "--json"],
    )
    assert denied.exit_code != 0

    grant = runner.invoke(
        app,
        [
            "capability",
            "grant",
            "--db",
            str(db),
            "--subject",
            actor_id,
            "--operation",
            "tool.call",
            "--operation",
            "skill.run",
            "--tool",
            "tool_local_echo",
            "--skill",
            "skill_task_trace_distiller",
            "--json",
        ],
    )
    assert grant.exit_code == 0, grant.output
    assert (
        runner.invoke(
            app,
            ["tool", "call", "local_echo", "--db", str(db), "--actor", actor_id, "--json"],
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            app,
            [
                "skill",
                "run",
                "task_trace_distiller",
                "--db",
                str(db),
                "--actor",
                actor_id,
                "--json",
            ],
        ).exit_code
        == 0
    )


def test_api_tool_call_and_audit_verify(db, monkeypatch) -> None:
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    actor = svc.actors.create("agent", "ApiToolAgent")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["tool.call"],
        tools_allowed=["tool_local_echo"],
    )
    client = TestClient(create_app())

    response = client.post(
        "/v1/tools/local_echo/call",
        json={"actor_id": actor.id, "payload": {"ok": True}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["output"]["echo"] == {"ok": True}
    assert body["evidence_ref"].startswith("ev_")

    verify = client.get("/v1/audit/verify")
    assert verify.status_code == 200
    assert verify.json()["valid"] is True


def test_tool_runner_records_evidence_and_validates_output_schema(svc) -> None:
    actor = svc.actors.create("agent", "ToolRunnerAgent")
    tool = svc.tools.add(
        ToolBinding(
            name="local_echo",
            type="python_function",
            output_schema={
                "type": "object",
                "required": ["echo"],
                "properties": {"echo": {"type": "object"}},
            },
        )
    )
    svc.capabilities.grant(actor.id, "system", ["tool.call"], tools_allowed=[tool.id])

    result = svc.tool_runner.call(tool.id, {"value": 42}, actor_id=actor.id)

    assert result.output == {"echo": {"value": 42}}
    assert result.evidence_ref is not None
    evidence = svc.store.get("evidence_refs", result.evidence_ref)
    assert evidence is not None
    assert evidence["kind"] == "tool_result"
    assert evidence["public_payload"]["tool_id"] == tool.id


def test_external_tool_result_ingest_projects_through_memory_into_context(svc) -> None:
    actor = svc.actors.create("agent", "ExternalEvidenceAgent")
    tool_id = "external_search"
    svc.capabilities.grant(
        actor.id,
        "system",
        [
            "evidence.ingest",
            "memory.propose",
            "memory.commit",
            "memory.correct",
            "memory.read",
            "memory.query",
            "context.build",
        ],
        tools_allowed=[tool_id],
    )

    result = svc.evidence.ingest_tool_result(
        tool_id=tool_id,
        tool_name="External Search",
        tool_type="external",
        input_payload={"query": "canonical OACS context"},
        output={"answer": "Canonical docs say OACS packages governed context."},
        actor_id=actor.id,
        scope=[],
        source_uri="https://example.test/docs/oacs",
    )
    memory = svc.memory.propose(
        "fact",
        2,
        "Canonical docs say OACS packages governed context.",
        actor.id,
        [],
    )
    svc.memory.commit(memory.id, actor.id)
    sharpened = svc.memory.sharpen(memory.id, result.evidence_ref or "", actor.id)
    capsule = svc.context.build(
        "What do canonical docs say about OACS context?", actor.id, scope=[]
    )

    assert result.evidence_ref is not None
    assert result.executed is True
    assert sharpened.evidence_refs == [result.evidence_ref]
    assert result.evidence_ref in capsule.evidence_refs
    evidence = svc.store.get("evidence_refs", result.evidence_ref)
    assert evidence["kind"] == "tool_result"
    assert evidence["public_payload"]["source_uri"] == "https://example.test/docs/oacs"
    assert any(
        event["operation"] == "evidence.ingest_tool_result"
        and event["target_id"] == result.evidence_ref
        for event in svc.audit.list()
    )


def test_local_cli_tool_binding_uses_json_stdin_and_evidence(svc, tmp_path) -> None:
    script = tmp_path / "tool.py"
    script.write_text(
        "\n".join(
            [
                "import json, sys",
                "payload = json.load(sys.stdin)",
                "print(json.dumps({'seen': payload['value']}))",
            ]
        ),
        encoding="utf-8",
    )
    actor = svc.actors.create("agent", "LocalCliAgent")
    tool = svc.tools.add(
        ToolBinding(
            name="json_cli",
            type="local_cli",
            command=f"python3 {script}",
            output_schema={
                "type": "object",
                "required": ["json", "returncode"],
                "properties": {
                    "json": {"type": "object"},
                    "returncode": {"const": 0},
                },
            },
        )
    )
    svc.capabilities.grant(actor.id, "system", ["tool.call"], tools_allowed=[tool.id])

    result = svc.tool_runner.call(tool.id, {"value": "ok"}, actor_id=actor.id)

    assert result.output["returncode"] == 0
    assert result.output["json"] == {"seen": "ok"}
    assert result.evidence_ref is not None


def test_cli_grant_tool_helper_and_schema_file(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    schema = tmp_path / "out.schema.json"
    schema.write_text(
        json.dumps(
            {
                "type": "object",
                "required": ["echo"],
                "properties": {"echo": {"type": "object"}},
            }
        ),
        encoding="utf-8",
    )
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    actor = runner.invoke(
        app,
        ["actor", "create", "--db", str(db), "--type", "agent", "--name", "ToolAgent", "--json"],
    )
    actor_id = json.loads(actor.output)["id"]
    added = runner.invoke(
        app,
        [
            "tool",
            "add",
            "--db",
            str(db),
            "--name",
            "local_echo",
            "--type",
            "python_function",
            "--output-schema",
            str(schema),
            "--json",
        ],
    )
    assert added.exit_code == 0, added.output
    tool_id = json.loads(added.output)["id"]
    grant = runner.invoke(
        app,
        [
            "capability",
            "grant-tool",
            "--db",
            str(db),
            "--subject",
            actor_id,
            "--tool",
            tool_id,
            "--json",
        ],
    )
    assert grant.exit_code == 0, grant.output
    call = runner.invoke(
        app,
        [
            "tool",
            "call",
            "local_echo",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--payload",
            '{"ok":true}',
            "--json",
        ],
    )
    assert call.exit_code == 0, call.output
    body = json.loads(call.output)
    assert body["output"] == {"echo": {"ok": True}}
    assert body["evidence_ref"].startswith("ev_")


def test_cli_ingests_external_tool_result(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    svc = services(str(db), require_key=False)
    actor = svc.actors.create("agent", "CliExternalEvidenceAgent")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["evidence.ingest"],
        tools_allowed=["external_cli"],
    )
    runner = CliRunner()

    ingest = runner.invoke(
        app,
        [
            "tool",
            "ingest-result",
            "--db",
            str(db),
            "--actor",
            actor.id,
            "--tool-id",
            "external_cli",
            "--tool-name",
            "External CLI",
            "--input",
            '{"query":"alpha"}',
            "--output",
            '{"result":"alpha evidence"}',
            "--source-uri",
            "file:///tmp/external-cli-result.json",
            "--json",
        ],
    )

    assert ingest.exit_code == 0, ingest.output
    body = json.loads(ingest.output)
    assert body["tool_id"] == "external_cli"
    assert body["tool_name"] == "External CLI"
    assert body["output"] == {"result": "alpha evidence"}
    assert body["evidence_ref"].startswith("ev_")

    inspect = runner.invoke(
        app,
        [
            "evidence",
            "inspect",
            body["evidence_ref"],
            "--db",
            str(db),
            "--json",
        ],
    )
    assert inspect.exit_code == 0, inspect.output
    evidence = json.loads(inspect.output)
    assert evidence["id"] == body["evidence_ref"]
    assert evidence["kind"] == "tool_result"
    assert evidence["public_payload"]["source_uri"] == "file:///tmp/external-cli-result.json"

    listed = runner.invoke(
        app,
        [
            "evidence",
            "list",
            "--db",
            str(db),
            "--kind",
            "tool_result",
            "--json",
        ],
    )
    assert listed.exit_code == 0, listed.output
    evidence_refs = json.loads(listed.output)
    assert [record["id"] for record in evidence_refs] == [body["evidence_ref"]]


def test_cli_grant_evidence_helper_allows_tool_result_ingest(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()

    grant = runner.invoke(
        app,
        [
            "capability",
            "grant-evidence",
            "--db",
            str(db),
            "--subject",
            "agent_cli",
            "--tool",
            "external_cli",
            "--json",
        ],
    )
    assert grant.exit_code == 0, grant.output
    grant_body = json.loads(grant.output)
    assert grant_body["allowed_operations"] == ["evidence.ingest"]
    assert grant_body["tools_allowed"] == ["external_cli"]

    ingest = runner.invoke(
        app,
        [
            "tool",
            "ingest-result",
            "--db",
            str(db),
            "--actor",
            "agent_cli",
            "--tool-id",
            "external_cli",
            "--input",
            '{"query":"alpha"}',
            "--output",
            '{"result":"alpha evidence"}',
            "--json",
        ],
    )

    assert ingest.exit_code == 0, ingest.output
    assert json.loads(ingest.output)["evidence_ref"].startswith("ev_")


def test_cli_ingest_result_denial_explains_tool_scoped_grant(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()

    ingest = runner.invoke(
        app,
        [
            "tool",
            "ingest-result",
            "--db",
            str(db),
            "--actor",
            "agent_cli",
            "--tool-id",
            "external_cli",
            "--output",
            '{"result":"alpha evidence"}',
            "--json",
        ],
        env={"COLUMNS": "200", "NO_COLOR": "1"},
        color=False,
    )

    assert ingest.exit_code != 0
    assert "Traceback" not in ingest.output
    assert _evidence_ingest_grant_hint("agent_cli", "external_cli") == (
        "acs capability grant-evidence --subject agent_cli --tool external_cli"
    )


def test_api_ingests_external_tool_result(db, monkeypatch) -> None:
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    actor = svc.actors.create("agent", "ApiExternalEvidenceAgent")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["evidence.ingest"],
        tools_allowed=["external_api"],
    )
    client = TestClient(create_app())

    response = client.post(
        "/v1/tools/results/ingest",
        json={
            "actor_id": actor.id,
            "tool_id": "external_api",
            "tool_name": "External API",
            "input": {"query": "beta"},
            "output": {"result": "beta evidence"},
            "source_uri": "https://example.test/result/beta",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_id"] == "external_api"
    assert body["output"] == {"result": "beta evidence"}
    assert body["evidence_ref"].startswith("ev_")


def test_mcp_import_creates_scoped_tools_and_blocks_unlisted_binding_tool(svc, tmp_path) -> None:
    config = tmp_path / "mcp.json"
    config.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "demo": {
                        "command": "demo-mcp",
                        "allowed_tools": ["search"],
                        "scope": ["project"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    imported = svc.mcp.import_config(str(config))
    tool = svc.tools.inspect("search")
    assert imported[0].allowed_tools == ["search"]
    assert tool.type == "mcp"
    assert tool.scope == ["project"]

    actor = svc.actors.create("agent", "McpAgent")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["tool.call"],
        scope=["project"],
        tools_allowed=[tool.id],
    )
    assert svc.policy.allows(actor.id, "tool.call", scope=["project"], tool=tool.id)
    assert not svc.policy.allows(actor.id, "tool.call", scope=["project"], tool="not-imported")
