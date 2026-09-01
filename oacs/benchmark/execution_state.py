from __future__ import annotations

import json
import time

from oacs.core.json import dumps
from oacs.loop.execution_state import ExecutionState, ExecutionStateEngine, ExecutionStateError


class ExecutionStateBenchmark:
    """Deterministic prompt-growth comparison for the experimental state adapter."""

    def run(self, horizons: tuple[int, ...] = (10, 25, 50, 100)) -> list[dict[str, object]]:
        if not horizons or any(horizon < 1 for horizon in horizons):
            raise ValueError("horizons must contain positive integers")
        return [self._run_horizon(horizon) for horizon in horizons]

    def run_decision_suite(
        self,
        checkpoint_sequences: list[list[dict[str, object]]],
        *,
        latency_iterations: int = 2000,
    ) -> dict[str, object]:
        growth = self.run()
        replay = self.run_checkpoint_replay(checkpoint_sequences)
        latency = self.run_latency(latency_iterations)
        safety = self.run_safety_probes()
        by_horizon = {int(_metric(row, "horizon")): row for row in growth}
        gates = {
            "safety": all(safety.values()),
            "replay_fidelity": replay["fidelity"] == 1.0,
            "task_isolation": replay["task_isolation"] is True,
            "growth_25": _metric(by_horizon[25], "cumulative_reduction_ratio") >= 2.0,
            "growth_100": _metric(by_horizon[100], "cumulative_reduction_ratio") >= 5.0,
            "bounded_prompt": _metric(by_horizon[100], "state_max_prompt_bytes")
            <= _metric(by_horizon[25], "state_max_prompt_bytes") * 1.2,
            "latency_p95": _metric(latency, "p95_ms") < 1.0,
        }
        return {
            "decision": "KEEP" if all(gates.values()) else "REJECT",
            "gates": gates,
            "growth": growth,
            "replay": replay,
            "latency": latency,
            "safety": safety,
        }

    def run_checkpoint_replay(
        self, checkpoint_sequences: list[list[dict[str, object]]]
    ) -> dict[str, object]:
        non_empty = [sequence for sequence in checkpoint_sequences if sequence]
        if not non_empty:
            raise ValueError("checkpoint_sequences must contain at least one non-empty sequence")
        schema: dict[str, object] = {
            "type": "object",
            "required": ["checkpoint_count", "current_checkpoint"],
            "properties": {
                "checkpoint_count": {"type": "integer", "minimum": 0},
                "current_checkpoint": {"type": "object"},
            },
            "additionalProperties": False,
        }
        engine = ExecutionStateEngine(schema, max_bytes=65_536)
        append_only_cumulative_bytes = 0
        state_cumulative_bytes = 0
        exact_final_states = 0
        final_states: list[ExecutionState] = []

        for sequence_index, sequence in enumerate(non_empty):
            state = ExecutionState(
                task_id=f"replay-{sequence_index}",
                values={"checkpoint_count": 0, "current_checkpoint": {}},
            )
            history: list[dict[str, object]] = []
            for step, checkpoint in enumerate(sequence, start=1):
                history.append(checkpoint)
                append_only_cumulative_bytes += len(dumps({"history": history}).encode("utf-8"))
                state_cumulative_bytes += len(
                    dumps({"state": state.values, "latest_checkpoint": checkpoint}).encode("utf-8")
                )
                state = engine.apply_patch(
                    state,
                    {"checkpoint_count": step, "current_checkpoint": checkpoint},
                    expected_revision=step - 1,
                )
            final_states.append(state)
            if state.values["current_checkpoint"] == sequence[-1]:
                exact_final_states += 1

        unique_task_ids = len({state.task_id for state in final_states}) == len(final_states)
        return {
            "sequences": len(non_empty),
            "checkpoints": sum(len(sequence) for sequence in non_empty),
            "fidelity": exact_final_states / len(non_empty),
            "task_isolation": unique_task_ids,
            "append_only_cumulative_bytes": append_only_cumulative_bytes,
            "state_cumulative_bytes": state_cumulative_bytes,
            "cumulative_reduction_ratio": round(
                append_only_cumulative_bytes / state_cumulative_bytes, 3
            ),
        }

    def run_latency(self, iterations: int = 2000) -> dict[str, object]:
        if iterations < 1:
            raise ValueError("iterations must be positive")
        schema: dict[str, object] = {
            "type": "object",
            "required": ["step", "status"],
            "properties": {
                "step": {"type": "integer", "minimum": 0},
                "status": {"type": "string"},
            },
            "additionalProperties": False,
        }
        engine = ExecutionStateEngine(schema, max_bytes=1024)
        state = ExecutionState(task_id="latency", values={"step": 0, "status": "running"})
        samples_ns: list[int] = []
        for step in range(1, iterations + 1):
            started = time.perf_counter_ns()
            state = engine.apply_patch(
                state,
                {"step": step, "status": "running"},
                expected_revision=step - 1,
            )
            samples_ns.append(time.perf_counter_ns() - started)
        ordered = sorted(samples_ns)
        return {
            "iterations": iterations,
            "median_ms": round(ordered[len(ordered) // 2] / 1_000_000, 6),
            "p95_ms": round(ordered[max(0, int(iterations * 0.95) - 1)] / 1_000_000, 6),
            "max_ms": round(ordered[-1] / 1_000_000, 6),
        }

    def run_safety_probes(self) -> dict[str, bool]:
        schema: dict[str, object] = {
            "type": "object",
            "required": ["step"],
            "properties": {
                "step": {"type": "integer", "minimum": 0},
                "blob": {"type": "string"},
            },
            "additionalProperties": False,
        }
        engine = ExecutionStateEngine(schema, max_bytes=128)
        evidence_ref = "ev_00000000000000000000000000000001"
        original = ExecutionState(
            task_id="safety",
            values={"step": 0},
            evidence_refs=(evidence_ref,),
        )
        schema_rejected = _transition_rejected(
            engine, original, {"step": "invalid"}, expected_revision=0
        )
        stale_revision_rejected = _transition_rejected(
            engine, original, {"step": 1}, expected_revision=1
        )
        oversized_rejected = _transition_rejected(
            engine,
            original,
            {"step": 1, "blob": "x" * 256},
            expected_revision=0,
        )
        return {
            "schema_rejected": schema_rejected,
            "stale_revision_rejected": stale_revision_rejected,
            "oversized_rejected": oversized_rejected,
            "rollback_preserved": original.values == {"step": 0} and original.revision == 0,
            "evidence_preserved": original.evidence_refs == (evidence_ref,),
        }

    def build_model_cases(self) -> list[dict[str, object]]:
        cases = (
            (25, "Never use fallback", "publish evidence"),
            (50, "Do not mix repository state", "run leak review"),
            (100, "Preserve audit provenance", "record checkpoint"),
        )
        return [self._build_model_case(*case) for case in cases]

    def score_model_answer(
        self, answer: str, expected: dict[str, object]
    ) -> dict[str, object]:
        try:
            parsed = json.loads(answer)
        except json.JSONDecodeError:
            return {"score": 0.0, "exact": False, "valid_json": False}
        if not isinstance(parsed, dict):
            return {"score": 0.0, "exact": False, "valid_json": True}
        matches = sum(parsed.get(key) == value for key, value in expected.items())
        return {
            "score": matches / len(expected),
            "exact": parsed == expected,
            "valid_json": True,
        }

    def _run_horizon(self, horizon: int) -> dict[str, object]:
        schema: dict[str, object] = {
            "type": "object",
            "required": ["current_step", "remaining_steps", "passed_checks", "status"],
            "properties": {
                "current_step": {"type": "integer", "minimum": 0},
                "remaining_steps": {"type": "integer", "minimum": 0},
                "passed_checks": {"type": "integer", "minimum": 0},
                "status": {"type": "string"},
                "last_result": {"type": "object"},
            },
            "additionalProperties": False,
        }
        engine = ExecutionStateEngine(schema, max_bytes=4096)
        state = ExecutionState(
            task_id=f"benchmark-{horizon}",
            values={
                "current_step": 0,
                "remaining_steps": horizon,
                "passed_checks": 0,
                "status": "running",
            },
        )
        task_spec = "Verify the repository and preserve complete evidence outside the prompt."
        history: list[dict[str, object]] = []
        append_only_cumulative_bytes = 0
        state_cumulative_bytes = 0
        state_max_prompt_bytes = 0

        for step in range(1, horizon + 1):
            observation: dict[str, object] = {
                "step": step,
                "tool": "repository-check",
                "status": "PASS",
                "detail": "Deterministic verification result retained as external evidence.",
            }
            history.append(observation)
            append_prompt = {"task": task_spec, "history": history}
            state_prompt = {
                "task": task_spec,
                "state": state.values,
                "latest_observation": observation,
            }
            append_only_cumulative_bytes += len(dumps(append_prompt).encode("utf-8"))
            state_prompt_bytes = len(dumps(state_prompt).encode("utf-8"))
            state_cumulative_bytes += state_prompt_bytes
            state_max_prompt_bytes = max(state_max_prompt_bytes, state_prompt_bytes)
            state = engine.apply_patch(
                state,
                {
                    "current_step": step,
                    "remaining_steps": horizon - step,
                    "passed_checks": step,
                    "status": "complete" if step == horizon else "running",
                    "last_result": observation,
                },
                expected_revision=step - 1,
            )

        append_only_final_prompt_bytes = len(
            dumps({"task": task_spec, "history": history}).encode("utf-8")
        )
        return {
            "horizon": horizon,
            "append_only_cumulative_bytes": append_only_cumulative_bytes,
            "state_cumulative_bytes": state_cumulative_bytes,
            "append_only_final_prompt_bytes": append_only_final_prompt_bytes,
            "state_max_prompt_bytes": state_max_prompt_bytes,
            "cumulative_reduction_ratio": round(
                append_only_cumulative_bytes / state_cumulative_bytes, 3
            ),
            "final_revision": state.revision,
        }

    def _build_model_case(self, horizon: int, constraint: str, next_step: str) -> dict[str, object]:
        history: list[dict[str, object]] = []
        for step in range(1, horizon + 1):
            event: dict[str, object] = {"step": step, "status": "PASS"}
            if step == 1:
                event["constraint_added"] = constraint
            if step == 7:
                event["error_added"] = "temporary schema mismatch"
            if step == 15:
                event["error_resolved"] = "temporary schema mismatch"
            if step == horizon:
                event["next"] = next_step
                event["task_status"] = "complete"
            history.append(event)

        expected: dict[str, object] = {
            "current_step": horizon,
            "status": "complete",
            "constraint": constraint,
            "active_error_count": 0,
            "next": next_step,
        }
        instruction = (
            "Return exactly one JSON object with current_step, status, constraint, "
            "active_error_count, and next. Do not add markdown or explanation."
        )
        state = {
            "current_step": horizon,
            "status": "complete",
            "constraints": [constraint],
            "active_errors": [],
            "next": next_step,
        }
        return {
            "horizon": horizon,
            "expected": expected,
            "append_prompt": f"{instruction}\nHISTORY:\n{dumps(history)}",
            "state_prompt": f"{instruction}\nEXECUTION_STATE:\n{dumps(state)}",
        }


def _transition_rejected(
    engine: ExecutionStateEngine,
    state: ExecutionState,
    patch: dict[str, object],
    *,
    expected_revision: int,
) -> bool:
    try:
        engine.apply_patch(state, patch, expected_revision=expected_revision)
    except ExecutionStateError:
        return True
    return False


def _metric(row: dict[str, object], key: str) -> float:
    value = row.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RuntimeError(f"benchmark metric {key!r} is not numeric")
    return float(value)
