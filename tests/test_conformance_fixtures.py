from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

from oacs.conformance import validate_conformance

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "conformance" / "fixtures"
NEGATIVE = ROOT / "conformance" / "negative"
SCHEMAS = ROOT / "schemas"

FIXTURE_SCHEMAS = {
    "context_capsule.json": "context_capsule.schema.json",
    "memory_record.json": "memory_record.schema.json",
    "capability_grant.json": "capability_grant.schema.json",
    "evidence_ref.json": "evidence_ref.schema.json",
    "rule_manifest.json": "rule_manifest.schema.json",
    "skill_manifest.json": "skill_manifest.schema.json",
    "tool_binding.json": "tool_binding.schema.json",
    "mcp_binding.json": "mcp_binding.schema.json",
    "audit_event.json": "audit_event.schema.json",
    "protected_ref.json": "protected_ref.schema.json",
    "memory_call.json": "memory_call.schema.json",
    "memory_operation.json": "memory_operation.schema.json",
    "context_operation.json": "context_operation.schema.json",
    "memory_loop_run.json": "memory_loop_run.schema.json",
    "tool_call_result.json": "tool_call_result.schema.json",
    "storage_selector.json": "storage_selector.schema.json",
    "retrieval_query.json": "retrieval_query.schema.json",
    "retrieval_result.json": "retrieval_result.schema.json",
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
    if name == "retrieval_result.schema.json":
        payload = json.loads(json.dumps(payload))
        payload["properties"]["query"] = load_json(SCHEMAS / "retrieval_query.schema.json")
    return payload


def hash_json(payload: object) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def stable_candidate_schemas() -> set[str]:
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")
    return {
        f"{schema_name}.schema.json"
        for schema_name in re.findall(r"\| `([^`]+)` \| `stable_candidate` \|", manifest)
    }


def test_language_neutral_conformance_fixtures_validate_against_schemas() -> None:
    for fixture_name, schema_name in FIXTURE_SCHEMAS.items():
        validate(load_json(FIXTURES / fixture_name), schema(schema_name))


def test_stable_candidate_fixtures_reject_unknown_top_level_fields() -> None:
    stable_candidates = stable_candidate_schemas()

    assert stable_candidates
    for fixture_name, schema_name in FIXTURE_SCHEMAS.items():
        if schema_name not in stable_candidates:
            continue
        payload = load_json(FIXTURES / fixture_name)
        payload["x_oacs_unknown"] = True

        with pytest.raises(ValidationError):
            validate(payload, schema(schema_name))


def test_context_capsule_fixture_checksum_uses_canonical_json() -> None:
    capsule = load_json(FIXTURES / "context_capsule.json")
    provided = capsule.pop("checksum")

    assert provided == hash_json(capsule)


def test_conformance_fixtures_link_memory_capsule_tool_and_evidence() -> None:
    capsule = load_json(FIXTURES / "context_capsule.json")
    memory = load_json(FIXTURES / "memory_record.json")
    evidence = load_json(FIXTURES / "evidence_ref.json")
    tool_result = load_json(FIXTURES / "tool_call_result.json")
    tool_binding = load_json(FIXTURES / "tool_binding.json")
    skill = load_json(FIXTURES / "skill_manifest.json")
    rule = load_json(FIXTURES / "rule_manifest.json")

    assert capsule["included_memories"] == [memory["id"]]
    assert capsule["evidence_refs"] == [evidence["id"]]
    assert memory["evidence_refs"] == [evidence["id"]]
    assert tool_result["evidence_ref"] == evidence["id"]
    assert skill["required_tools"] == [tool_binding["id"]]
    assert skill["required_rules"] == [rule["id"]]


def test_rule_manifest_fixture_hash_uses_canonical_json() -> None:
    rule = load_json(FIXTURES / "rule_manifest.json")
    provided = rule.pop("content_hash")

    assert provided == hash_json(rule)


def test_audit_event_fixture_hash_uses_canonical_json() -> None:
    event = load_json(FIXTURES / "audit_event.json")
    provided = event.pop("content_hash")

    assert provided == hash_json(event)


def test_protected_value_fixture_projects_ref_not_plaintext() -> None:
    protected_ref = load_json(FIXTURES / "protected_ref.json")

    assert protected_ref["projection"] == "ref_only"
    assert "OACS_TEST_SECRET_VALUE" not in json.dumps(protected_ref)


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


def test_negative_schema_fixture_rejects_sql_storage_selector() -> None:
    negative = load_json(NEGATIVE / "storage_selector_sql_fragment.json")

    with pytest.raises(ValidationError):
        validate(negative["payload"], schema(str(negative["schema"])))


def test_negative_schema_fixture_rejects_depth_outside_d0_d5() -> None:
    negative = load_json(NEGATIVE / "capability_grant_depth_overflow.json")

    with pytest.raises(ValidationError):
        validate(negative["payload"], schema(str(negative["schema"])))


def test_negative_semantic_fixture_rejects_implicit_wildcards() -> None:
    negative = load_json(NEGATIVE / "capability_grant_glob_scope_without_star.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    wildcard_values = [*payload["scope"], *payload["namespaces_allowed"]]
    assert any(
        isinstance(value, str) and "*" in value and value != "*" for value in wildcard_values
    )


def test_negative_semantic_fixture_rejects_http_tool_without_network_opt_in() -> None:
    negative = load_json(NEGATIVE / "tool_binding_http_network_without_opt_in.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    assert payload["type"] == "http"
    assert payload["permissions"].get("allow_network") is not True


def test_negative_semantic_fixture_rejects_bad_audit_hash() -> None:
    negative = load_json(NEGATIVE / "audit_event_bad_hash.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))
    provided = payload.pop("content_hash")

    assert provided != hash_json(payload)


def test_negative_semantic_fixture_rejects_bad_rule_hash() -> None:
    negative = load_json(NEGATIVE / "rule_manifest_bad_hash.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))
    provided = payload.pop("content_hash")

    assert provided != hash_json(payload)


@pytest.mark.parametrize(
    "fixture_name",
    [
        "context_capsule_plaintext_protected_value.json",
        "tool_call_result_plaintext_secret.json",
        "audit_event_plaintext_secret.json",
        "evidence_ref_plaintext_secret.json",
        "mcp_binding_env_plaintext_secret.json",
        "context_capsule_masked_protected_value.json",
        "tool_call_result_masked_secret.json",
        "audit_event_masked_secret.json",
        "evidence_ref_masked_secret.json",
    ],
)
def test_negative_semantic_fixtures_reject_protected_value_leaks(
    fixture_name: str,
) -> None:
    negative = load_json(NEGATIVE / fixture_name)
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    serialized = json.dumps(payload)
    assert any(
        marker in serialized
        for marker in (
            "OACS_TEST_SECRET_VALUE",
            "****CRET",
            "***abcd",
            "[REDACTED:abcd]",
            "suffix=CRET",
        )
    )


def test_negative_schema_fixture_rejects_secret_ref_without_external_locator() -> None:
    negative = load_json(NEGATIVE / "protected_ref_secret_without_external_locator.json")

    with pytest.raises(ValidationError):
        validate(negative["payload"], schema(str(negative["schema"])))


def test_negative_semantic_fixture_rejects_d4_as_factual_retrieval_evidence() -> None:
    negative = load_json(NEGATIVE / "retrieval_result_d4_used_as_fact.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    hits = payload["hits"]
    assert isinstance(hits, list)
    invalid_hits = [
        hit
        for hit in hits
        if isinstance(hit, dict)
        and int(hit["depth"]) >= 3
        and hit.get("used_as_factual_evidence") is True
    ]
    assert invalid_hits


@pytest.mark.parametrize(
    "fixture_name",
    [
        "context_operation_completed_without_audit.json",
        "memory_operation_completed_without_audit.json",
    ],
)
def test_negative_semantic_fixtures_reject_completed_operations_without_audit(
    fixture_name: str,
) -> None:
    negative = load_json(NEGATIVE / fixture_name)
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    assert payload["status"] == "completed"
    assert payload["audit_event_id"] is None


def test_negative_semantic_fixture_rejects_committed_memory_without_proposal() -> None:
    negative = load_json(NEGATIVE / "memory_loop_run_committed_without_proposed.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    assert not set(payload["committed_memories"]).issubset(set(payload["proposed_memories"]))


def test_negative_semantic_fixture_rejects_deep_memory_record_as_fact() -> None:
    negative = load_json(NEGATIVE / "memory_record_d4_factual_evidence.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))

    evidence = payload["content"]["evidence"]
    assert any(item["depth"] >= 3 and item["evidence_kind"] == "factual" for item in evidence)


def test_negative_semantic_fixture_rejects_unlinked_skill_tool() -> None:
    negative = load_json(NEGATIVE / "skill_manifest_unlinked_required_tool.json")
    payload = negative["payload"]
    assert isinstance(payload, dict)
    validate(payload, schema(str(negative["schema"])))
    tool_binding = load_json(FIXTURES / "tool_binding.json")

    assert tool_binding["id"] not in payload["required_tools"]


def test_reference_conformance_checker_validates_bundled_fixtures() -> None:
    result = validate_conformance(ROOT / "conformance", ROOT / "schemas")

    assert result["valid"] is True
    assert result["positive_fixtures"] == len(FIXTURE_SCHEMAS)
    assert result["negative_fixtures"] == len(list(NEGATIVE.glob("*.json")))
    assert result["errors"] == []
