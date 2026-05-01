from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import ValidationError, validate

from oacs.api.server import create_app
from oacs.app import services
from oacs.core.errors import AccessDenied
from oacs.core.ids import new_id
from oacs.core.time import now_iso
from oacs.loop.memory_calls import memory_call_to_dict

ROOT = Path(__file__).resolve().parents[1]


def schema(name: str) -> dict[str, object]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def test_memory_call_schema_accepts_loop_output(svc) -> None:
    mem = svc.memory.propose(
        "fact",
        2,
        "Alpha reports use make report-safe.",
        None,
        ["project"],
        evidence=[
            {
                "claim": "Alpha report command",
                "value": "make report-safe",
                "slot": "evidence",
            }
        ],
    )
    svc.memory.commit(mem.id, None)

    result = svc.loop.run("Alpha report?", None, scope=["project"])

    call_schema = schema("memory_call.schema.json")
    for call in result.memory_calls:
        validate(call, call_schema)
    assert result.memory_calls[1]["result"]["memories"][0]["content_hash"]
    assert "Alpha reports use make report-safe." not in json.dumps(result.memory_calls)


def test_memory_call_schema_rejects_invalid_status_and_unknown_operation() -> None:
    payload = {
        "id": "mcall_bad",
        "op": "memory.write_hidden",
        "status": "ok",
        "arguments": {},
        "result": {},
    }

    with pytest.raises(ValidationError):
        validate(payload, schema("memory_call.schema.json"))


def test_operation_schemas_accept_v026_envelopes() -> None:
    validate(
        {
            "id": new_id("mop"),
            "operation": "memory.query",
            "status": "completed",
            "actor_id": "act_1",
            "target_id": None,
            "scope": ["project"],
            "namespace": "default",
            "depth": None,
            "arguments": {"query": "Alpha"},
            "result": {"memory_ids": ["mem_1"]},
            "audit_event_id": "aud_1",
            "created_at": now_iso(),
        },
        schema("memory_operation.schema.json"),
    )
    validate(
        {
            "id": new_id("cop"),
            "operation": "context.build",
            "status": "completed",
            "actor_id": "act_1",
            "agent_id": None,
            "capsule_id": "ctx_1",
            "scope": ["project"],
            "token_budget": 4000,
            "arguments": {"intent": "answer_project_question"},
            "result": {"included_memories": ["mem_1"]},
            "audit_event_id": "aud_2",
            "created_at": now_iso(),
        },
        schema("context_operation.schema.json"),
    )


def test_explicit_denied_memory_query_overrides_allowed_operation(svc) -> None:
    actor = svc.actors.create("agent", "DeniedQuery")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["memory.query", "memory.read"],
        denied_operations=["memory.query"],
    )

    with pytest.raises(AccessDenied):
        svc.memory.query("anything", actor.id, ["project"])


def test_empty_grant_scope_does_not_match_requested_scope(svc) -> None:
    actor = svc.actors.create("agent", "EmptyScope")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["memory.query", "memory.read"],
        scope=[],
    )

    with pytest.raises(AccessDenied):
        svc.memory.query("anything", actor.id, ["project"])


def test_memory_read_and_query_enforce_namespace_allowlist(svc) -> None:
    actor = svc.actors.create("agent", "NamespaceLimited")
    svc.capabilities.grant_shared_memory(
        actor.id,
        "system",
        ["project"],
        namespaces_allowed=["default"],
    )
    private_mem = svc.memory.propose("fact", 2, "private namespace memory", None, ["project"])
    private_mem.namespace = "private"
    private_mem.lifecycle_status = "active"
    svc.memory._save(private_mem)

    assert svc.memory.query("private", actor.id, ["project"]) == []
    with pytest.raises(AccessDenied):
        svc.memory.read(private_mem.id, actor.id)


def test_api_audits_memory_and_context_operations(db, monkeypatch) -> None:
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    mem = svc.memory.propose("fact", 2, "audited memory", None, ["project"])
    svc.memory.commit(mem.id, None)
    client = TestClient(create_app())

    assert client.post("/v1/memory/query", json={"query": "audited"}).status_code == 200
    assert client.get(f"/v1/memory/{mem.id}").status_code == 200
    built = client.post(
        "/v1/context/build",
        json={"intent": "audited", "scope": ["project"]},
    )
    assert built.status_code == 200
    capsule_id = built.json()["id"]
    assert client.get(f"/v1/context/{capsule_id}").status_code == 200

    operations = [event["operation"] for event in services(str(db)).audit.list()]
    assert "memory.query" in operations
    assert "memory.read" in operations
    assert "context.build" in operations
    assert "context.export" in operations


def test_api_denied_memory_read_and_query_are_audited(db, monkeypatch) -> None:
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    actor = svc.actors.create("agent", "DeniedApi")
    mem = svc.memory.propose("fact", 2, "hidden content", None, ["project"])
    svc.memory.commit(mem.id, None)
    client = TestClient(create_app())

    query_response = client.post(
        "/v1/memory/query",
        json={"actor_id": actor.id, "query": "hidden", "scope": ["project"]},
    )
    read_response = client.get(f"/v1/memory/{mem.id}", params={"actor_id": actor.id})

    assert query_response.status_code == 403
    assert read_response.status_code == 403
    assert "hidden content" not in query_response.text
    assert "hidden content" not in read_response.text
    events = services(str(db)).audit.list()
    denied = [event for event in events if event["metadata"].get("status") == "denied"]
    assert [event["operation"] for event in denied] == ["memory.query", "memory.read"]


def test_memory_call_to_dict_is_schema_stable() -> None:
    from oacs.loop.memory_calls import MemoryCall

    payload = memory_call_to_dict(
        MemoryCall(
            id="mcall_1",
            op="memory.query",
            status="completed",
            arguments={"query": "Alpha"},
            result={"memory_ids": ["mem_1"], "count": 1},
        )
    )

    validate(payload, schema("memory_call.schema.json"))
