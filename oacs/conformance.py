from __future__ import annotations

import copy
import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from jsonschema import ValidationError, validate

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

PROTECTED_VALUE_LEAK_FIXTURES = {
    "context_capsule_plaintext_protected_value.json",
    "tool_call_result_plaintext_secret.json",
    "audit_event_plaintext_secret.json",
    "evidence_ref_plaintext_secret.json",
    "mcp_binding_env_plaintext_secret.json",
    "context_capsule_masked_protected_value.json",
    "tool_call_result_masked_secret.json",
    "audit_event_masked_secret.json",
    "evidence_ref_masked_secret.json",
}

PROTECTED_VALUE_SENTINELS = ("OACS_TEST_SECRET_VALUE",)
MASKED_PROTECTED_VALUE_PATTERNS = (
    re.compile(r"\*{3,}[A-Za-z0-9_-]{3,}"),
    re.compile(r"\[REDACTED:[A-Za-z0-9_-]{3,}\]"),
    re.compile(r"\b(?:suffix|tail|last4|last_4)[=: ][A-Za-z0-9_-]{3,}\b", re.IGNORECASE),
)


def default_conformance_root() -> Path:
    return Path(__file__).resolve().parents[1] / "conformance"


def default_schema_root() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas"


def validate_conformance(
    conformance_root: Path | None = None,
    schema_root: Path | None = None,
) -> dict[str, object]:
    conformance = conformance_root or default_conformance_root()
    schemas = schema_root or default_schema_root()
    errors: list[dict[str, object]] = []
    positive_checked = 0
    negative_checked = 0

    for fixture_name, schema_name in FIXTURE_SCHEMAS.items():
        positive_checked += 1
        payload = _load_json(conformance / "fixtures" / fixture_name)
        schema = _schema(schemas, schema_name)
        try:
            validate(payload, schema)
            _validate_positive_semantics(fixture_name, payload)
        except Exception as exc:  # noqa: BLE001 - returned as validation data.
            errors.append(
                {"fixture": fixture_name, "schema": schema_name, "error": str(exc)}
            )

    evidence = _load_json(conformance / "fixtures" / "evidence_ref.json")
    tool_binding = _load_json(conformance / "fixtures" / "tool_binding.json")
    for path in sorted((conformance / "negative").glob("*.json")):
        negative_checked += 1
        fixture = _load_json(path)
        negative_payload: object = fixture.get("payload")
        schema_name = str(fixture.get("schema", ""))
        reason = str(fixture.get("reason", ""))
        try:
            schema = _schema(schemas, schema_name)
            rejected = _rejects_negative(
                path.name,
                negative_payload,
                schema,
                evidence,
                tool_binding,
            )
        except Exception as exc:  # noqa: BLE001 - returned as validation data.
            errors.append({"fixture": path.name, "schema": schema_name, "error": str(exc)})
            continue
        if not rejected:
            errors.append(
                {
                    "fixture": path.name,
                    "schema": schema_name,
                    "error": f"negative fixture unexpectedly accepted: {reason}",
                }
            )

    return {
        "valid": not errors,
        "positive_fixtures": positive_checked,
        "negative_fixtures": negative_checked,
        "errors": errors,
    }


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return cast(dict[str, object], payload)


def _schema(schema_root: Path, name: str) -> dict[str, object]:
    schema = _load_json(schema_root / name)
    return cast(dict[str, object], _inline_local_refs(schema_root, schema))


def _inline_local_refs(schema_root: Path, payload: Any) -> Any:
    if isinstance(payload, dict):
        ref = payload.get("$ref")
        if isinstance(ref, str) and ref.endswith(".schema.json"):
            return _schema(schema_root, ref)
        return {key: _inline_local_refs(schema_root, value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_inline_local_refs(schema_root, item) for item in payload]
    return payload


def _hash_json(payload: object) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _validate_positive_semantics(fixture_name: str, payload: dict[str, object]) -> None:
    if fixture_name == "context_capsule.json":
        capsule = copy.deepcopy(payload)
        checksum = capsule.pop("checksum")
        if checksum != _hash_json(capsule):
            raise ValueError("context capsule checksum mismatch")
    if (
        fixture_name == "audit_event.json"
        and payload.get("content_hash") != _hash_without(payload, "content_hash")
    ):
        raise ValueError("audit event content_hash mismatch")
    if (
        fixture_name == "rule_manifest.json"
        and payload.get("content_hash") != _hash_without(payload, "content_hash")
    ):
        raise ValueError("rule manifest content_hash mismatch")
    if fixture_name == "tool_binding.json":
        _validate_tool_binding_semantics(payload)
    if fixture_name == "capability_grant.json":
        _validate_capability_grant_semantics(payload)
    if fixture_name == "retrieval_result.json":
        for hit in _list(payload.get("hits")):
            if _depth(hit) >= 3 and hit.get("used_as_factual_evidence") is True:
                raise ValueError("D3-D5 retrieval hit used as factual evidence")


def _rejects_negative(
    fixture_name: str,
    payload: object,
    schema: dict[str, object],
    evidence: dict[str, object],
    tool_binding: dict[str, object],
) -> bool:
    try:
        validate(payload, schema)
    except ValidationError:
        return True
    if not isinstance(payload, dict):
        return True
    payload_dict = cast(dict[str, object], payload)
    if fixture_name == "context_capsule_bad_checksum.json":
        capsule = cast(dict[str, object], copy.deepcopy(payload_dict))
        checksum = capsule.pop("checksum", None)
        return bool(checksum != _hash_json(capsule))
    if fixture_name == "audit_event_bad_hash.json":
        return bool(payload_dict.get("content_hash") != _hash_without(payload_dict, "content_hash"))
    if fixture_name == "rule_manifest_bad_hash.json":
        return bool(payload_dict.get("content_hash") != _hash_without(payload_dict, "content_hash"))
    if fixture_name in PROTECTED_VALUE_LEAK_FIXTURES:
        return _contains_protected_value_leak(payload_dict)
    if fixture_name == "capability_grant_glob_scope_without_star.json":
        return _has_implicit_wildcard(payload_dict, "scope") or _has_implicit_wildcard(
            payload_dict, "namespaces_allowed"
        )
    if fixture_name == "tool_call_result_unlinked_evidence.json":
        return bool(payload_dict.get("evidence_ref") != evidence.get("id"))
    if fixture_name == "tool_binding_http_network_without_opt_in.json":
        try:
            _validate_tool_binding_semantics(payload_dict)
        except ValueError:
            return True
        return False
    if fixture_name in {
        "context_operation_completed_without_audit.json",
        "memory_operation_completed_without_audit.json",
    }:
        return _is_completed_without_audit(payload_dict)
    if fixture_name == "memory_loop_run_committed_without_proposed.json":
        return not set(_strings(payload_dict.get("committed_memories"))).issubset(
            set(_strings(payload_dict.get("proposed_memories")))
        )
    if fixture_name == "memory_record_d4_factual_evidence.json":
        return _memory_record_embeds_deep_factual_evidence(payload_dict)
    if fixture_name == "memory_record_d4_low_confidence_evidence.json":
        return not _deep_memory_has_commit_evidence(payload_dict)
    if fixture_name == "skill_manifest_unlinked_required_tool.json":
        return tool_binding.get("id") not in _strings(payload_dict.get("required_tools"))
    if fixture_name == "retrieval_result_d4_used_as_fact.json":
        return any(
            _depth(hit) >= 3 and hit.get("used_as_factual_evidence") is True
            for hit in _list(payload_dict.get("hits"))
        )
    return False


def _hash_without(payload: dict[str, object], field: str) -> str:
    return _hash_json({key: value for key, value in payload.items() if key != field})


def _validate_tool_binding_semantics(payload: dict[str, object]) -> None:
    if payload.get("type") != "http":
        return
    permissions = payload.get("permissions")
    if not isinstance(permissions, dict) or permissions.get("allow_network") is not True:
        raise ValueError("http ToolBinding requires permissions.allow_network=true")


def _validate_capability_grant_semantics(payload: dict[str, object]) -> None:
    for field in ("scope", "namespaces_allowed", "tools_allowed", "skills_allowed"):
        if _has_implicit_wildcard(payload, field):
            raise ValueError(f"{field} wildcard access requires explicit '*'")


def _has_implicit_wildcard(payload: dict[str, object], field: str) -> bool:
    value = payload.get(field)
    if not isinstance(value, list):
        return False
    return any(isinstance(item, str) and "*" in item and item != "*" for item in value)


def _contains_protected_value_leak(payload: object) -> bool:
    if isinstance(payload, str):
        return any(sentinel in payload for sentinel in PROTECTED_VALUE_SENTINELS) or any(
            pattern.search(payload) for pattern in MASKED_PROTECTED_VALUE_PATTERNS
        )
    if isinstance(payload, dict):
        return any(_contains_protected_value_leak(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_contains_protected_value_leak(item) for item in payload)
    return False


def _is_completed_without_audit(payload: dict[str, object]) -> bool:
    return payload.get("status") == "completed" and payload.get("audit_event_id") is None


def _memory_record_embeds_deep_factual_evidence(payload: dict[str, object]) -> bool:
    if _depth(payload) < 3:
        return False
    content = payload.get("content")
    if not isinstance(content, dict):
        return False
    return any(
        _depth(item) >= 3 and item.get("evidence_kind") == "factual"
        for item in _list(content.get("evidence"))
    )


def _deep_memory_has_commit_evidence(payload: dict[str, object]) -> bool:
    depth = _depth(payload)
    if depth < 3:
        return True
    if _strings(payload.get("evidence_refs")):
        return True
    content = payload.get("content")
    if not isinstance(content, dict):
        return False
    threshold = _deep_memory_evidence_threshold(depth)
    for item in _list(content.get("evidence")):
        if _confidence(item) >= threshold and (depth < 5 or item.get("source_ref")):
            return True
    return False


def _deep_memory_evidence_threshold(depth: int) -> float:
    if depth <= 3:
        return 0.5
    if depth == 4:
        return 0.7
    return 0.8


def _list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _depth(hit: dict[str, object]) -> int:
    value = hit.get("depth", 0)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    return 0


def _confidence(hit: dict[str, object]) -> float:
    value = hit.get("confidence", 0)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return 0.0
