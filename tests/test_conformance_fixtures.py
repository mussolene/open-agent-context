from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "conformance" / "fixtures"
NEGATIVE = ROOT / "conformance" / "negative"
SCHEMAS = ROOT / "schemas"

FIXTURE_SCHEMAS = {
    "context_capsule.json": "context_capsule.schema.json",
    "memory_record.json": "memory_record.schema.json",
    "capability_grant.json": "capability_grant.schema.json",
    "evidence_ref.json": "evidence_ref.schema.json",
    "memory_call.json": "memory_call.schema.json",
    "memory_operation.json": "memory_operation.schema.json",
    "context_operation.json": "context_operation.schema.json",
    "memory_loop_run.json": "memory_loop_run.schema.json",
    "tool_call_result.json": "tool_call_result.schema.json",
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def schema(name: str) -> dict[str, object]:
    payload = load_json(SCHEMAS / name)
    if name == "memory_loop_run.schema.json":
        payload = json.loads(json.dumps(payload))
        payload["properties"]["memory_calls"]["items"] = load_json(
            SCHEMAS / "memory_call.schema.json"
        )
    return payload


def hash_json(payload: object) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_language_neutral_conformance_fixtures_validate_against_schemas() -> None:
    for fixture_name, schema_name in FIXTURE_SCHEMAS.items():
        validate(load_json(FIXTURES / fixture_name), schema(schema_name))


def test_context_capsule_fixture_checksum_uses_canonical_json() -> None:
    capsule = load_json(FIXTURES / "context_capsule.json")
    provided = capsule.pop("checksum")

    assert provided == hash_json(capsule)


def test_conformance_fixtures_link_memory_capsule_tool_and_evidence() -> None:
    capsule = load_json(FIXTURES / "context_capsule.json")
    memory = load_json(FIXTURES / "memory_record.json")
    evidence = load_json(FIXTURES / "evidence_ref.json")
    tool_result = load_json(FIXTURES / "tool_call_result.json")

    assert capsule["included_memories"] == [memory["id"]]
    assert capsule["evidence_refs"] == [evidence["id"]]
    assert memory["evidence_refs"] == [evidence["id"]]
    assert tool_result["evidence_ref"] == evidence["id"]


def test_negative_schema_fixture_rejects_unknown_memory_call_operation() -> None:
    negative = load_json(NEGATIVE / "memory_call_unknown_operation.json")

    with pytest.raises(ValidationError):
        validate(negative["payload"], schema(str(negative["schema"])))


def test_negative_semantic_fixture_rejects_bad_context_checksum() -> None:
    negative = load_json(NEGATIVE / "context_capsule_bad_checksum.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))
    provided = payload.pop("checksum")

    assert provided != hash_json(payload)


def test_negative_semantic_fixture_rejects_unlinked_tool_evidence() -> None:
    negative = load_json(NEGATIVE / "tool_call_result_unlinked_evidence.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))
    known_evidence = load_json(FIXTURES / "evidence_ref.json")

    assert payload["evidence_ref"] != known_evidence["id"]
