from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import httpx
from jsonschema import validate

from oacs.benchmark.models import BenchmarkTask
from oacs.core.errors import ValidationFailure
from oacs.core.json import hash_json, loads

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"
TASK_SCHEMA = loads((SCHEMA_DIR / "benchmark_task.schema.json").read_text(encoding="utf-8"))
PACK_SCHEMA = loads((SCHEMA_DIR / "benchmark_task_pack.schema.json").read_text(encoding="utf-8"))
PACK_SCHEMA["properties"]["tasks"]["items"] = TASK_SCHEMA


def load_task_pack(path: Path) -> dict[str, Any]:
    pack = cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    validate_task_pack(pack)
    return pack


def validate_task_pack(pack: dict[str, Any]) -> None:
    validate(pack, PACK_SCHEMA)
    tasks = pack.get("tasks")
    if not isinstance(tasks, list):
        raise ValidationFailure("task pack tasks must be a list")
    if pack["task_count"] != len(tasks):
        raise ValidationFailure("task pack task_count does not match tasks length")
    task_ids: set[str] = set()
    for task in tasks:
        validate(task, TASK_SCHEMA)
        task_id = str(task["id"])
        if task_id in task_ids:
            raise ValidationFailure(f"duplicate benchmark task id: {task_id}")
        task_ids.add(task_id)
    expected = str(pack["integrity"]["sha256"])
    actual = pack_integrity_hash(pack)
    if actual != expected:
        raise ValidationFailure("task pack checksum mismatch")


def pack_integrity_hash(pack: dict[str, Any]) -> str:
    payload = dict(pack)
    payload["integrity"] = {}
    return hash_json(payload)


def tasks_from_pack(pack: dict[str, Any]) -> list[BenchmarkTask]:
    validate_task_pack(pack)
    return [BenchmarkTask(**task) for task in pack["tasks"]]


def make_task_pack(
    tasks: list[BenchmarkTask],
    pack_id: str,
    name: str,
    source: str,
    native_harness: dict[str, object] | None = None,
    native_suite: str | None = None,
    adapter_version: str | None = None,
) -> dict[str, Any]:
    pack: dict[str, Any] = {
        "schema_version": "0.1",
        "id": pack_id,
        "name": name,
        "source": source,
        "license": None,
        "created_at": None,
        "task_count": len(tasks),
        "tasks": [task.model_dump() for task in tasks],
        "integrity": {},
        "native_harness": native_harness,
        "native_suite": native_suite,
        "adapter_version": adapter_version,
    }
    pack["integrity"] = {"sha256": pack_integrity_hash(pack)}
    validate_task_pack(pack)
    return pack


def verify_file_checksum(path: Path, expected_sha256: str) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ValidationFailure("downloaded task pack checksum mismatch")
    return digest


def download_task_pack(
    url: str,
    expected_sha256: str,
    output: Path,
    allow_network: bool,
    timeout_sec: int = 60,
    max_bytes: int = 20_000_000,
) -> dict[str, Any]:
    if not allow_network:
        raise ValidationFailure("network disabled; rerun with explicit allow-network")
    response = httpx.get(url, timeout=timeout_sec, follow_redirects=True)
    response.raise_for_status()
    body = response.content
    if len(body) > max_bytes:
        raise ValidationFailure("downloaded task pack exceeds size limit")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(body)
    verify_file_checksum(output, expected_sha256)
    return load_task_pack(output)
