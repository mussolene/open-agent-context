from __future__ import annotations

from fastapi.testclient import TestClient

from oacs.api.server import create_app
from oacs.context.capsule import ContextCapsule


def test_api_health_and_actor(db, monkeypatch):
    monkeypatch.setenv("OACS_DB", str(db))
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/v1/actors", json={"type": "human", "name": "User"})
    assert response.status_code == 200
    assert response.json()["name"] == "User"


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
