from __future__ import annotations

from copy import deepcopy

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from pydantic import BaseModel, ConfigDict, Field

from oacs.core.json import dumps
from oacs.loop.engine import MemoryLoopEngine, MemoryLoopResult


class ExecutionStateError(ValueError):
    """Raised when a state transition cannot be accepted atomically."""


class ExecutionState(BaseModel):
    """Experimental bounded working state kept outside the OACS v1 contract."""

    model_config = ConfigDict(frozen=True)

    task_id: str
    revision: int = Field(default=0, ge=0)
    values: dict[str, object] = Field(default_factory=dict)
    evidence_refs: tuple[str, ...] = ()


class PreparedExecutionTurn(BaseModel):
    """Typed model input and governed OACS trace for one stateful turn."""

    state: ExecutionState
    latest_observation: dict[str, object]
    model_prompt: str
    memory_loop_result: MemoryLoopResult


class ExecutionStateEngine:
    def __init__(self, schema: dict[str, object], max_bytes: int = 16_384):
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            raise ValueError(f"invalid execution state schema: {exc.message}") from None
        self.validator = Draft202012Validator(schema)
        self.max_bytes = max_bytes

    def apply_patch(
        self,
        state: ExecutionState,
        patch: dict[str, object],
        *,
        expected_revision: int,
    ) -> ExecutionState:
        if state.revision != expected_revision:
            raise ExecutionStateError(
                f"revision conflict: expected {expected_revision}, current {state.revision}"
            )
        if not isinstance(patch, dict):
            raise ExecutionStateError("state patch must be a JSON object")

        candidate = _merge_patch(state.values, patch)
        try:
            self.validator.validate(candidate)
        except ValidationError as exc:
            location = ".".join(str(part) for part in exc.absolute_path) or "<root>"
            raise ExecutionStateError(
                f"state patch violates schema at {location}: {exc.message}"
            ) from None
        try:
            encoded = dumps(candidate).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ExecutionStateError(f"state patch is not JSON serializable: {exc}") from None
        if len(encoded) > self.max_bytes:
            raise ExecutionStateError(
                f"state size {len(encoded)} bytes exceeds limit {self.max_bytes}"
            )

        return ExecutionState(
            task_id=state.task_id,
            revision=state.revision + 1,
            values=candidate,
            evidence_refs=state.evidence_refs,
        )


class StatefulMemoryLoopAdapter:
    """Prepare compact stateful turns without making OACS the tool orchestrator."""

    def __init__(self, loop: MemoryLoopEngine, state_engine: ExecutionStateEngine):
        self.loop = loop
        self.state_engine = state_engine

    def prepare_turn(
        self,
        task_spec: str,
        state: ExecutionState,
        latest_observation: dict[str, object],
        *,
        actor_id: str | None,
        agent_id: str | None = None,
        scope: list[str] | None = None,
        token_budget: int = 4000,
        allowed_tools: list[str] | None = None,
    ) -> PreparedExecutionTurn:
        loop_result = self.loop.run(
            task_spec,
            actor_id,
            agent_id,
            scope,
            token_budget,
            allowed_tools,
            {"memory_calls": True},
        )
        prompt_payload = {
            "task_spec": task_spec,
            "governed_context": {
                "context_capsule_id": loop_result.context_capsule_id,
                "intent": loop_result.intent,
                "memory_calls": loop_result.memory_calls,
                "evidence": loop_result.evidence,
                "rules_applied": loop_result.rules_applied,
            },
            "execution_state": state.model_dump(mode="json"),
            "latest_observation": latest_observation,
            "output_contract": {
                "reasoning": "string",
                "state_patch": "object",
                "action": "object",
            },
        }
        return PreparedExecutionTurn(
            state=state,
            latest_observation=latest_observation,
            model_prompt=dumps(prompt_payload),
            memory_loop_result=loop_result,
        )

    def commit_patch(
        self, prepared_turn: PreparedExecutionTurn, patch: dict[str, object]
    ) -> ExecutionState:
        return self.state_engine.apply_patch(
            prepared_turn.state,
            patch,
            expected_revision=prepared_turn.state.revision,
        )


def _merge_patch(target: dict[str, object], patch: dict[str, object]) -> dict[str, object]:
    result = deepcopy(target)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict):
            current = result.get(key)
            nested = current if isinstance(current, dict) else {}
            result[key] = _merge_patch(nested, value)
        else:
            result[key] = deepcopy(value)
    return result
