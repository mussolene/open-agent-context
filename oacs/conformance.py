from __future__ import annotations

import copy
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

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
    "storage_selector.json": "storage_selector.schema.json",
    "retrieval_query.json": "retrieval_query.schema.json",
    "retrieval_result.json": "retrieval_result.schema.json",
}


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
    for path in sorted((conformance / "negative").glob("*.json")):
        negative_checked += 1
        fixture = _load_json(path)
        payload = fixture.get("payload")
        schema_name = str(fixture.get("schema", ""))
        reason = str(fixture.get("reason", ""))
        try:
            schema = _schema(schemas, schema_name)
            rejected = _rejects_negative(path.name, payload, schema, evidence)
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
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(schema_root: Path, name: str) -> dict[str, object]:
    schema = _load_json(schema_root / name)
    return _inline_local_refs(schema_root, schema)


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
    if fixture_name == "retrieval_result.json":
        for hit in _list(payload.get("hits")):
            if int(hit.get("depth", 0)) >= 3 and hit.get("used_as_factual_evidence") is True:
                raise ValueError("D3-D5 retrieval hit used as factual evidence")


def _rejects_negative(
    fixture_name: str,
    payload: object,
    schema: dict[str, object],
    evidence: dict[str, object],
) -> bool:
    try:
        validate(payload, schema)
    except ValidationError:
        return True
    if not isinstance(payload, dict):
        return True
    if fixture_name == "context_capsule_bad_checksum.json":
        capsule = copy.deepcopy(payload)
        checksum = capsule.pop("checksum", None)
        return checksum != _hash_json(capsule)
    if fixture_name == "tool_call_result_unlinked_evidence.json":
        return payload.get("evidence_ref") != evidence.get("id")
    if fixture_name == "retrieval_result_d4_used_as_fact.json":
        return any(
            int(hit.get("depth", 0)) >= 3 and hit.get("used_as_factual_evidence") is True
            for hit in _list(payload.get("hits"))
        )
    return False


def _list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]
