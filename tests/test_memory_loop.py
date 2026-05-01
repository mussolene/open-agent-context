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
    assert [call["op"] for call in result.memory_calls] == [
        "memory.query",
        "memory.read",
        "memory.extract_evidence",
    ]
    assert result.benchmark_metrics["memory_calls_count"] == 3


def test_memory_loop_can_disable_memory_calls(svc):
    result = svc.loop.run(
        "Short task",
        None,
        scope=["project"],
        model_config={"memory_calls": False},
    )
    assert result.memory_calls == []
    assert result.model_prompt is None


def test_memory_loop_deepens_when_scoped_capsule_has_no_evidence(svc):
    mem = svc.memory.propose(
        "fact",
        2,
        "Cross-scope evidence says Beta reports use make beta-report.",
        None,
        ["org"],
        evidence=[
            {
                "evidence_kind": "procedure",
                "claim": "Beta report command",
                "value": "make beta-report",
                "slot": "evidence",
                "confidence": 1.0,
            }
        ],
    )
    svc.memory.commit(mem.id, None)

    result = svc.loop.run("How do I generate the Beta report?", None, scope=["project"])

    assert mem.id in result.memories_used
    assert [call["op"] for call in result.memory_calls][:2] == [
        "memory.query",
        "memory.query.deepen",
    ]
    assert result.evidence[0]["value"] == "make beta-report"
    assert result.answered_deterministically is True
