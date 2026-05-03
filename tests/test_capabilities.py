from __future__ import annotations

import pytest

from oacs.core.errors import AccessDenied


def test_capability_denies_memory_read(svc):
    actor = svc.actors.create("agent", "Denied")
    mem = svc.memory.propose("fact", 2, "blocked", None, ["project"])
    svc.memory.commit(mem.id, None)
    with pytest.raises(AccessDenied):
        svc.memory.read(mem.id, actor.id)


def test_capability_allows_memory_read(svc):
    actor = svc.actors.create("agent", "Allowed")
    svc.capabilities.grant(actor.id, "system", ["memory.read"], memory_depth_allowed=2)
    mem = svc.memory.propose("fact", 2, "allowed", None, ["project"])
    svc.memory.commit(mem.id, None)
    assert svc.memory.read(mem.id, actor.id).content.text == "allowed"


def test_strict_policy_denies_bootstrap_bypass(svc, monkeypatch):
    mem = svc.memory.propose("fact", 2, "strict seed", "system", ["project"])
    mem.lifecycle_status = "active"
    svc.memory._save(mem)
    monkeypatch.setenv("OACS_POLICY_MODE", "strict")

    with pytest.raises(AccessDenied):
        svc.memory.read(mem.id, None)
    with pytest.raises(AccessDenied):
        svc.memory.read(mem.id, "")
    with pytest.raises(AccessDenied):
        svc.memory.read(mem.id, "system")


def test_dev_policy_records_bootstrap_bypass_audit(svc):
    mem = svc.memory.propose("fact", 2, "dev seed", None, ["project"])
    svc.memory.commit(mem.id, None)

    operations = [event["operation"] for event in svc.audit.list()]

    assert "policy.bootstrap_bypass" in operations


def test_shared_memory_grant_filters_query_by_scope_and_depth(svc):
    actor = svc.actors.create("agent", "ScopedSubagent")
    svc.capabilities.grant_shared_memory(
        actor.id,
        "system",
        ["repo:oacs", "task:allowed"],
        memory_depth_allowed=2,
    )
    allowed = svc.memory.propose("fact", 2, "allowed task memory", None, ["task:allowed"])
    denied_same_repo = svc.memory.propose(
        "fact", 2, "same repo wrong task", None, ["repo:oacs", "task:other"]
    )
    denied_scope = svc.memory.propose("fact", 2, "other task memory", None, ["task:other"])
    denied_depth = svc.memory.propose("pattern", 3, "fuzzy memory", None, ["task:allowed"])
    svc.memory.commit(allowed.id, None)
    svc.memory.commit(denied_same_repo.id, None)
    svc.memory.commit(denied_scope.id, None)
    denied_depth.evidence_refs.append("ev_sharp")
    denied_depth.lifecycle_status = "active"
    svc.memory._save(denied_depth)

    results = svc.memory.query("memory", actor.id, ["task:allowed"])

    assert [memory.id for memory in results] == [allowed.id]
    with pytest.raises(AccessDenied):
        svc.memory.read(denied_same_repo.id, actor.id)
    with pytest.raises(AccessDenied):
        svc.memory.read(denied_scope.id, actor.id)
    with pytest.raises(AccessDenied):
        svc.memory.read(denied_depth.id, actor.id)


def test_shared_memory_grant_blocks_out_of_scope_write(svc):
    actor = svc.actors.create("agent", "WriterSubagent")
    svc.capabilities.grant(
        actor.id,
        "system",
        ["memory.propose"],
        scope=["task:allowed"],
        memory_depth_allowed=2,
    )

    with pytest.raises(AccessDenied):
        svc.memory.propose("fact", 2, "outside", actor.id, ["task:other"])


def test_capability_definitions_are_listable(svc):
    definitions = svc.capabilities.list_definitions()
    assert any(definition.operation == "memory.read" for definition in definitions)
    assert any(definition.operation == "context.read" for definition in definitions)
    assert any(definition.operation == "context.import" for definition in definitions)
    assert svc.capabilities.inspect_definition("cap_context_build").operation == "context.build"
