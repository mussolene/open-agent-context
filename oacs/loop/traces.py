from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from oacs.audit import AuditService
from oacs.core.errors import NotFound
from oacs.core.ids import new_id
from oacs.core.json import dumps, hash_json
from oacs.core.time import now_iso
from oacs.loop.execution_state import ExecutionState, ExecutionStateEngine, ExecutionStateError
from oacs.storage.sqlite import SQLiteStore

REPO_DEVELOPMENT_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": [
        "current_goal",
        "phase",
        "status",
        "completed",
        "next_steps",
        "blockers",
        "active_constraints",
        "last_observation",
    ],
    "properties": {
        "current_goal": {"type": "string", "minLength": 1},
        "phase": {"type": "string", "minLength": 1},
        "status": {"type": "string", "enum": ["running", "blocked", "complete"]},
        "completed": {"type": "array", "items": {"type": "string"}, "maxItems": 50},
        "next_steps": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
        "blockers": {"type": "array", "items": {"type": "string"}, "maxItems": 20},
        "active_constraints": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 30,
        },
        "last_observation": {"type": "object"},
    },
    "additionalProperties": False,
}


class TaskTrace(BaseModel):
    id: str = Field(default_factory=lambda: new_id("trace"))
    events: list[dict[str, object]] = Field(default_factory=list)


class ExecutionStateTraceStore:
    """SQLite-only experimental persistence and telemetry for task execution state."""

    def __init__(self, store: SQLiteStore, audit: AuditService):
        self.store = store
        self.audit = audit

    def initialize(
        self,
        task: str,
        *,
        goal: str | None = None,
        actor_id: str | None = None,
        scope: Sequence[str] | None = None,
        namespace: str = "default",
        max_bytes: int = 16_384,
        evidence_refs: Sequence[str] | None = None,
    ) -> dict[str, object]:
        state_id = _state_id(task)
        now = now_iso()
        state = ExecutionState(
            task_id=task,
            values={
                "current_goal": goal or task,
                "phase": "planning",
                "status": "running",
                "completed": [],
                "next_steps": [],
                "blockers": [],
                "active_constraints": [],
                "last_observation": {},
            },
            evidence_refs=tuple(evidence_refs or []),
        )
        payload: dict[str, object] = {
            "kind": "execution_state",
            "profile": "repo_development",
            "task": task,
            "schema": REPO_DEVELOPMENT_SCHEMA,
            "max_bytes": max_bytes,
            "state": state.model_dump(mode="json"),
            "telemetry": _empty_telemetry(),
        }
        record = _state_record(
            state_id,
            payload,
            now,
            now,
            actor_id,
            namespace,
            list(scope or []),
        )
        if not self.store.compare_and_swap_json("task_traces", record, None):
            raise ExecutionStateError(f"execution state already exists for task: {task}")
        self.audit.record(
            "state.init",
            actor_id,
            state_id,
            {"task_hash": hash_json(task), "profile": "repo_development"},
        )
        return record

    def get(self, task: str) -> dict[str, object]:
        record = self.store.get("task_traces", _state_id(task))
        if record is None or not _is_state_record(record):
            raise NotFound(f"execution state not found for task: {task}")
        return record

    def list(self) -> list[dict[str, object]]:
        rows = self.store.list(
            "task_traces",
            filters={"status": "active"},
            order_by=[("updated_at", "desc"), ("id", "desc")],
            limit=None,
        )
        return [row for row in rows if _is_state_record(row)]

    def patch(
        self,
        task: str,
        patch: dict[str, object],
        observation: dict[str, object],
        *,
        expected_revision: int,
        quality: str = "unknown",
        actor_id: str | None = None,
        evidence_refs: Sequence[str] | None = None,
    ) -> dict[str, object]:
        if quality not in {"pass", "fail", "unknown"}:
            raise ExecutionStateError("quality must be pass, fail, or unknown")
        record = self.get(task)
        payload = _state_payload(record)
        state = ExecutionState.model_validate(payload["state"])
        engine = ExecutionStateEngine(
            _object(payload, "schema"), max_bytes=_integer(payload, "max_bytes")
        )
        effective_patch = dict(patch)
        effective_patch["last_observation"] = observation
        try:
            updated_state = engine.apply_patch(
                state,
                effective_patch,
                expected_revision=expected_revision,
            )
        except ExecutionStateError as exc:
            operation = (
                "state.patch_conflict"
                if "revision conflict" in str(exc)
                else "state.patch_rejected"
            )
            self.audit.record(
                operation,
                actor_id,
                str(record["id"]),
                {"task_hash": hash_json(task), "reason": str(exc)},
            )
            raise
        if evidence_refs:
            updated_state = updated_state.model_copy(
                update={
                    "evidence_refs": tuple(
                        dict.fromkeys((*updated_state.evidence_refs, *evidence_refs))
                    )
                }
            )

        telemetry = _object(payload, "telemetry")
        observation_bytes = len(dumps(observation).encode("utf-8"))
        append_only_current = _integer(telemetry, "append_only_current_bytes") + observation_bytes
        state_turn_bytes = len(
            dumps(
                {
                    "state": updated_state.model_dump(mode="json"),
                    "latest_observation": observation,
                }
            ).encode("utf-8")
        )
        updated_telemetry = dict(telemetry)
        updated_telemetry.update(
            {
                "turns": _integer(telemetry, "turns") + 1,
                "append_only_current_bytes": append_only_current,
                "append_only_cumulative_bytes": _integer(telemetry, "append_only_cumulative_bytes")
                + append_only_current,
                "state_cumulative_bytes": _integer(telemetry, "state_cumulative_bytes")
                + state_turn_bytes,
                "last_state_bytes": len(
                    dumps(updated_state.model_dump(mode="json")).encode("utf-8")
                ),
                "quality_passes": _integer(telemetry, "quality_passes")
                + (1 if quality == "pass" else 0),
                "quality_failures": _integer(telemetry, "quality_failures")
                + (1 if quality == "fail" else 0),
                "last_patch_at": now_iso(),
            }
        )
        updated_payload = dict(payload)
        updated_payload["state"] = updated_state.model_dump(mode="json")
        updated_payload["telemetry"] = updated_telemetry
        updated_record = dict(record)
        updated_record["payload"] = updated_payload
        updated_record["updated_at"] = now_iso()
        updated_record["content_hash"] = hash_json(updated_payload)
        if not self.store.compare_and_swap_json(
            "task_traces", updated_record, str(record["content_hash"])
        ):
            self.audit.record(
                "state.patch_conflict",
                actor_id,
                str(record["id"]),
                {"task_hash": hash_json(task), "reason": "compare_and_swap_failed"},
            )
            raise ExecutionStateError("revision conflict: state changed during patch")
        self.audit.record(
            "state.patch",
            actor_id,
            str(record["id"]),
            {
                "task_hash": hash_json(task),
                "revision": updated_state.revision,
                "quality": quality,
                "observation_hash": hash_json(observation),
                "state_turn_bytes": state_turn_bytes,
                "append_only_current_bytes": append_only_current,
            },
        )
        return updated_record

    def remove(self, task: str, actor_id: str | None = None) -> dict[str, object]:
        record = self.get(task)
        self.store.delete("task_traces", str(record["id"]))
        self.audit.record(
            "state.remove",
            actor_id,
            str(record["id"]),
            {"task_hash": hash_json(task)},
        )
        return {"removed": True, "task": task, "id": record["id"]}

    def metrics(self) -> dict[str, object]:
        records = self.list()
        telemetry_rows = [_object(_state_payload(record), "telemetry") for record in records]
        eligible = [row for row in telemetry_rows if _integer(row, "turns") >= 10]
        append_bytes = sum(_integer(row, "append_only_cumulative_bytes") for row in eligible)
        state_bytes = sum(_integer(row, "state_cumulative_bytes") for row in eligible)
        quality_failures = sum(_integer(row, "quality_failures") for row in telemetry_rows)
        state_ids = {str(record["id"]) for record in records}
        rejected, conflicts = _failure_counts(self.audit.list(), state_ids)
        successful = sum(_integer(row, "turns") for row in telemetry_rows)
        attempts = successful + rejected + conflicts
        reduction_ratio = append_bytes / state_bytes if state_bytes else None
        if len(eligible) < 3:
            decision = "INSUFFICIENT_DATA"
        elif quality_failures or (attempts and (rejected + conflicts) / attempts > 0.05):
            decision = "REJECT"
        elif reduction_ratio is not None and reduction_ratio >= 2.0:
            decision = "KEEP"
        else:
            decision = "REJECT"
        return {
            "decision": decision,
            "states": len(records),
            "long_tasks": len(eligible),
            "turns": successful,
            "quality_passes": sum(_integer(row, "quality_passes") for row in telemetry_rows),
            "quality_failures": quality_failures,
            "patch_rejections": rejected,
            "revision_conflicts": conflicts,
            "append_only_cumulative_bytes": append_bytes,
            "state_cumulative_bytes": state_bytes,
            "reduction_ratio": round(reduction_ratio, 3) if reduction_ratio else None,
            "keep_thresholds": {
                "minimum_long_tasks": 3,
                "minimum_turns_per_long_task": 10,
                "minimum_reduction_ratio": 2.0,
                "maximum_rejection_and_conflict_rate": 0.05,
                "quality_failures": 0,
            },
        }


def _state_id(task: str) -> str:
    return f"state_{hash_json(task)[:32]}"


def _empty_telemetry() -> dict[str, object]:
    return {
        "turns": 0,
        "append_only_current_bytes": 0,
        "append_only_cumulative_bytes": 0,
        "state_cumulative_bytes": 0,
        "last_state_bytes": 0,
        "quality_passes": 0,
        "quality_failures": 0,
        "last_patch_at": None,
    }


def _state_record(
    state_id: str,
    payload: dict[str, object],
    created_at: str,
    updated_at: str,
    actor_id: str | None,
    namespace: str,
    scope: list[str],
) -> dict[str, object]:
    return {
        "id": state_id,
        "payload": payload,
        "created_at": created_at,
        "updated_at": updated_at,
        "status": "active",
        "namespace": namespace,
        "scope": scope,
        "owner_actor_id": actor_id,
        "content_hash": hash_json(payload),
    }


def _is_state_record(record: dict[str, object]) -> bool:
    payload = record.get("payload")
    return isinstance(payload, dict) and payload.get("kind") == "execution_state"


def _state_payload(record: dict[str, object]) -> dict[str, object]:
    payload = record.get("payload")
    if not isinstance(payload, dict) or payload.get("kind") != "execution_state":
        raise ExecutionStateError("invalid execution state record")
    return payload


def _object(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ExecutionStateError(f"execution state field {key!r} must be an object")
    return value


def _integer(payload: dict[str, object], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ExecutionStateError(f"execution state field {key!r} must be an integer")
    return value


def _failure_counts(audit_events: list[dict[str, object]], state_ids: set[str]) -> tuple[int, int]:
    rejected = 0
    conflicts = 0
    for event in audit_events:
        if str(event.get("target_id")) not in state_ids:
            continue
        if event.get("operation") == "state.patch_rejected":
            rejected += 1
        elif event.get("operation") == "state.patch_conflict":
            conflicts += 1
    return rejected, conflicts
