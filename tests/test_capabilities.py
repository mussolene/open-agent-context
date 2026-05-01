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


def test_capability_definitions_are_listable(svc):
    definitions = svc.capabilities.list_definitions()
    assert any(definition.operation == "memory.read" for definition in definitions)
    assert svc.capabilities.inspect_definition("cap_context_build").operation == "context.build"
