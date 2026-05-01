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
