from __future__ import annotations


def test_memory_loop_returns_capsule_and_proposal(svc):
    mem = svc.memory.propose(
        "procedure", 2, "Alpha reports use make report-safe.", None, ["project"]
    )
    svc.memory.commit(mem.id, None)
    result = svc.loop.run("How do I generate the Alpha report?", None, scope=["project"])
    assert result.context_capsule_id.startswith("ctx_")
    assert mem.id in result.memories_used
    assert result.proposed_memories
