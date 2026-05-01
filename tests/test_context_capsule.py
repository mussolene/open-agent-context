from __future__ import annotations


def test_context_build_and_explain(svc):
    mem = svc.memory.propose(
        "procedure", 2, "Alpha reports use make report-safe.", None, ["project"]
    )
    svc.memory.commit(mem.id, None)
    capsule = svc.context.build("Alpha report command", None, scope=["project"])
    assert mem.id in capsule.included_memories
    assert capsule.checksum
    explanation = svc.context.explain(capsule.id, None)
    assert mem.id in explanation["included_memories"]


def test_context_capsule_validate_import_round_trip(svc, tmp_path):
    capsule = svc.context.build("round trip", None, scope=["project"])
    payload = capsule.model_dump()
    assert svc.context.validate_payload(payload)["valid"] is True
    exported = tmp_path / "capsule.json"
    exported.write_text(capsule.model_dump_json(), encoding="utf-8")
    imported = svc.context.import_capsule(payload, None)
    assert imported.id == capsule.id
    assert svc.context.read(capsule.id, None).checksum == capsule.checksum


def test_context_capsule_export_envelope_round_trip(svc):
    capsule = svc.context.build("signed export", None, scope=["project"])

    exported = svc.context.export_capsule(capsule.id, None)
    validation = svc.context.validate_payload(exported.model_dump())
    imported = svc.context.import_capsule(exported.model_dump(), None)

    assert exported.export_type == "context_capsule_export"
    assert exported.integrity.algorithm == "HMAC-SHA256"
    assert exported.integrity.payload_checksum
    assert exported.integrity.signature
    assert validation["integrity"]["signature"] == exported.integrity.signature
    assert imported.id == capsule.id


def test_context_capsule_export_rejects_tampered_integrity(svc):
    capsule = svc.context.build("tampered export", None, scope=["project"])
    payload = svc.context.export_capsule(capsule.id, None).model_dump()
    payload["capsule"]["purpose"] = "tampered"

    try:
        svc.context.validate_payload(payload)
    except Exception as exc:
        assert "checksum" in str(exc) or "signature" in str(exc)
    else:
        raise AssertionError("tampered capsule export passed validation")


def test_context_capsule_rejects_bad_checksum(svc):
    capsule = svc.context.build("bad checksum", None, scope=["project"])
    payload = capsule.model_dump()
    payload["purpose"] = "tampered"
    try:
        svc.context.validate_payload(payload)
    except Exception as exc:
        assert "checksum" in str(exc)
    else:
        raise AssertionError("tampered capsule passed validation")


def test_context_build_respects_subagent_shared_memory_scope(svc):
    actor = svc.actors.create("agent", "CapsuleSubagent")
    svc.capabilities.grant_shared_memory(actor.id, "system", ["task:allowed"])
    allowed = svc.memory.propose("fact", 2, "allowed capsule memory", None, ["task:allowed"])
    denied = svc.memory.propose("fact", 2, "denied capsule memory", None, ["task:other"])
    svc.memory.commit(allowed.id, None)
    svc.memory.commit(denied.id, None)

    capsule = svc.context.build("capsule memory", actor.id, scope=["task:allowed"])

    assert allowed.id in capsule.included_memories
    assert denied.id not in capsule.included_memories
