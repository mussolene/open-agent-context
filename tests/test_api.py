from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from jsonschema import validate

from oacs.api.server import create_app
from oacs.app import services
from oacs.context.capsule import ContextCapsule

ROOT = Path(__file__).resolve().parents[1]


def schema(name: str) -> dict[str, object]:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def test_api_health_and_actor(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/v1/actors", json={"type": "human", "name": "User"})
    assert response.status_code == 200
    assert response.json()["name"] == "User"


def test_api_agent_actor_does_not_receive_wildcard_grant(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    client = TestClient(create_app())
    response = client.post("/v1/actors", json={"type": "agent", "name": "Subagent"})
    assert response.status_code == 200
    actor_id = response.json()["id"]
    grants = services(str(db), require_key=False).capabilities.for_actor(actor_id)
    assert grants == []


def test_api_registries_and_capsule_round_trip(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    client = TestClient(create_app())
    assert client.get("/v1/capabilities").status_code == 200
    assert client.get("/v1/skills").status_code == 200
    assert client.get("/v1/tools").status_code == 200
    assert client.get("/v1/mcp").status_code == 200
    capsule = ContextCapsule(purpose="api", token_budget=1, permissions={}).seal()
    payload = capsule.model_dump()
    assert client.post("/v1/context/validate", json=payload).json()["valid"] is True
    imported = client.post("/v1/context/import", json=payload)
    assert imported.status_code == 200
    assert client.get(f"/v1/context/{capsule.id}").json()["id"] == capsule.id
    bad = payload | {"purpose": "tampered"}
    assert client.post("/v1/context/validate", json=bad).status_code >= 400


def test_api_context_export_envelope_and_audit(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    capsule = svc.context.build("api export", None, scope=["project"])
    client = TestClient(create_app())

    response = client.post(f"/v1/context/{capsule.id}/export", json={})

    assert response.status_code == 200
    payload = response.json()
    validate(payload, schema("context_capsule_export.schema.json"))
    assert client.post("/v1/context/validate", json=payload).json()["valid"] is True
    imported = client.post("/v1/context/import", json=payload)
    assert imported.status_code == 200
    operations = [event["operation"] for event in services(str(db)).audit.list()]
    assert operations.count("context.export") >= 1
    assert "context.import" in operations


def test_api_context_export_rejects_tampering(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    capsule = svc.context.build("api tamper", None, scope=["project"])
    payload = svc.context.export_capsule(capsule.id, None).model_dump()
    payload["capsule"]["purpose"] = "changed"
    client = TestClient(create_app())

    response = client.post("/v1/context/validate", json=payload)

    assert response.status_code >= 400


def test_api_loop_run_returns_memory_calls(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    svc = services(str(db))
    mem = svc.memory.propose(
        "procedure", 2, "Alpha reports use make report-safe.", None, ["project"]
    )
    svc.memory.commit(mem.id, None)
    client = TestClient(create_app())

    response = client.post(
        "/v1/loop/run",
        json={
            "user_request": "How do I generate the Alpha report?",
            "scope": ["project"],
            "model_config": {"memory_calls": True},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["memory_calls"][0]["op"] == "memory.query"
    assert payload["memory_calls"][1]["op"] == "memory.read"
    assert payload["operation_metrics"]["memory_calls_count"] == 3
