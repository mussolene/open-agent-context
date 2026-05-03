from __future__ import annotations

import pytest

from oacs.core.errors import ValidationFailure


def test_memory_propose_commit_query_read(svc):
    mem = svc.memory.propose("procedure", 2, "Alpha uses make report-safe.", None, ["project"])
    committed = svc.memory.commit(mem.id, None)
    assert committed.lifecycle_status == "active"
    results = svc.memory.query("Alpha report", None, ["project"])
    assert results[0].id == mem.id
    assert svc.memory.read(mem.id, None).content.text == "Alpha uses make report-safe."


def test_forget_blocks_normal_read(svc):
    mem = svc.memory.propose("fact", 2, "secret forgotten text", None, ["project"])
    svc.memory.commit(mem.id, None)
    svc.memory.forget(mem.id, None)
    try:
        svc.memory.read(mem.id, None)
    except Exception as exc:
        assert "forgotten" in str(exc)
    else:
        raise AssertionError("forgotten memory was readable")


def test_d3_memory_commit_accepts_embedded_structured_evidence(svc):
    mem = svc.memory.propose(
        "pattern",
        3,
        "Reports usually use the safe target.",
        None,
        ["project"],
        evidence=[
            {
                "evidence_kind": "pattern_support",
                "claim": "safe report target observed",
                "value": "make report-safe",
                "source_ref": "ev_local",
                "confidence": 0.5,
                "depth": 2,
                "scope": ["project"],
            }
        ],
    )

    committed = svc.memory.commit(mem.id, None)

    assert committed.lifecycle_status == "active"


def test_d4_memory_commit_rejects_low_confidence_embedded_evidence(svc):
    mem = svc.memory.propose(
        "pattern",
        4,
        "Reports may use the safe target.",
        None,
        ["project"],
        evidence=[
            {
                "evidence_kind": "pattern_support",
                "claim": "weak report target observation",
                "value": "make report-safe",
                "source_ref": "ev_local",
                "confidence": 0.69,
                "depth": 2,
                "scope": ["project"],
            }
        ],
    )

    with pytest.raises(ValidationFailure):
        svc.memory.commit(mem.id, None)


def test_d5_memory_commit_requires_embedded_source_ref_without_external_ref(svc):
    mem = svc.memory.propose(
        "prior",
        5,
        "The community may prefer explicit evidence refs.",
        None,
        ["project"],
        evidence=[
            {
                "evidence_kind": "domain_prior_support",
                "claim": "community prior support",
                "value": "evidence-backed memory",
                "source_ref": None,
                "confidence": 0.9,
                "depth": 2,
                "scope": ["project"],
            }
        ],
    )

    with pytest.raises(ValidationFailure):
        svc.memory.commit(mem.id, None)
