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
    assert result.context_policy["name"] == "compact_capsule"


def test_memory_loop_uses_compact_policy_for_tiny_low_pressure_task(svc):
    result = svc.loop.run("Ping?", None, scope=["project"], token_budget=500)
    assert result.memory_calls == []
    assert result.context_policy["name"] == "compact_capsule"
    assert result.context_policy["reason"] == "tiny_task_low_memory_pressure"


def test_memory_loop_short_circuits_exact_evidence_even_for_tiny_task(svc):
    mem = svc.memory.propose(
        "fact",
        2,
        "Alpha command evidence.",
        None,
        ["project"],
        evidence=[
            {
                "evidence_kind": "procedure",
                "claim": "Alpha report command",
                "value": "make report-safe",
                "slot": "evidence",
                "confidence": 1.0,
            }
        ],
    )
    svc.memory.commit(mem.id, None)
    result = svc.loop.run("Alpha?", None, scope=["project"], token_budget=500)
    assert result.context_policy["name"] == "memory_calls"
    assert result.context_policy["reason"] == "structured_evidence_available"
    assert result.answered_deterministically is True
    assert "make report-safe" in result.final_answer


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


def test_memory_loop_deepening_respects_subagent_scope(svc):
    actor = svc.actors.create("agent", "DeepeningSubagent")
    svc.capabilities.grant_shared_memory(actor.id, "system", ["project"])
    mem = svc.memory.propose(
        "fact",
        2,
        "Org-only Gamma reports use make gamma-report.",
        None,
        ["org"],
        evidence=[
            {
                "evidence_kind": "procedure",
                "claim": "Gamma report command",
                "value": "make gamma-report",
                "slot": "evidence",
                "confidence": 1.0,
            }
        ],
    )
    svc.memory.commit(mem.id, None)

    result = svc.loop.run("How do I generate the Gamma report?", actor.id, scope=["project"])

    assert mem.id not in result.memories_used
    assert result.answered_deterministically is False
