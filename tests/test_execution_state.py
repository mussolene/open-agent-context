from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from oacs.benchmark.execution_state import ExecutionStateBenchmark
from oacs.cli.main import app
from oacs.loop.execution_state import (
    ExecutionState,
    ExecutionStateEngine,
    ExecutionStateError,
    StatefulMemoryLoopAdapter,
)

SCHEMA: dict[str, object] = {
    "type": "object",
    "required": ["step", "status", "nested"],
    "properties": {
        "step": {"type": "integer", "minimum": 0},
        "status": {"type": "string", "enum": ["running", "complete"]},
        "nested": {
            "type": "object",
            "properties": {
                "keep": {"type": "string"},
                "remove": {"type": "string"},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}


def test_execution_state_applies_atomic_merge_patch() -> None:
    original = ExecutionState(
        task_id="task-alpha",
        values={
            "step": 0,
            "status": "running",
            "nested": {"keep": "yes", "remove": "obsolete"},
        },
        evidence_refs=("ev_00000000000000000000000000000001",),
    )

    updated = ExecutionStateEngine(SCHEMA).apply_patch(
        original,
        {
            "step": 1,
            "nested": {"remove": None},
        },
        expected_revision=0,
    )

    assert original.revision == 0
    assert original.values["nested"] == {"keep": "yes", "remove": "obsolete"}
    assert updated.revision == 1
    assert updated.values["nested"] == {"keep": "yes"}
    assert updated.evidence_refs == original.evidence_refs


def test_execution_state_rejects_conflicts_schema_errors_and_oversize() -> None:
    original = ExecutionState(
        task_id="task-alpha",
        values={"step": 0, "status": "running", "nested": {"keep": "yes"}},
    )
    engine = ExecutionStateEngine(SCHEMA, max_bytes=120)

    with pytest.raises(ExecutionStateError, match="revision conflict"):
        engine.apply_patch(original, {"step": 1}, expected_revision=1)
    with pytest.raises(ExecutionStateError, match="violates schema"):
        engine.apply_patch(original, {"step": "one"}, expected_revision=0)
    with pytest.raises(ExecutionStateError, match="exceeds limit"):
        engine.apply_patch(
            original,
            {"nested": {"keep": "x" * 200}},
            expected_revision=0,
        )

    assert original.revision == 0
    assert original.values["step"] == 0


def test_execution_state_benchmark_reduces_prompt_growth() -> None:
    rows = ExecutionStateBenchmark().run()

    assert [row["horizon"] for row in rows] == [10, 25, 50, 100]
    for row in rows:
        assert row["state_cumulative_bytes"] < row["append_only_cumulative_bytes"]
        assert row["state_max_prompt_bytes"] < row["append_only_final_prompt_bytes"]
        assert row["final_revision"] == row["horizon"]
    assert rows[-1]["cumulative_reduction_ratio"] > rows[0]["cumulative_reduction_ratio"]


def test_execution_state_benchmark_rejects_invalid_horizons() -> None:
    with pytest.raises(ValueError, match="positive integers"):
        ExecutionStateBenchmark().run((0,))


def test_execution_state_decision_suite_passes_gates() -> None:
    sequences = [
        [{"task": "alpha", "summary": f"step {step}", "next": "continue"} for step in range(1, 26)],
        [{"task": "beta", "summary": f"step {step}", "next": "continue"} for step in range(1, 11)],
    ]

    report = ExecutionStateBenchmark().run_decision_suite(sequences, latency_iterations=100)

    assert report["decision"] == "KEEP"
    assert all(report["gates"].values())
    assert report["replay"]["fidelity"] == 1.0
    assert report["replay"]["task_isolation"] is True


def test_execution_state_model_case_scoring_is_exact() -> None:
    benchmark = ExecutionStateBenchmark()
    case = benchmark.build_model_cases()[0]
    expected = case["expected"]
    assert isinstance(expected, dict)

    exact = benchmark.score_model_answer(json.dumps(expected), expected)
    invalid = benchmark.score_model_answer("not-json", expected)

    assert exact == {"score": 1.0, "exact": True, "valid_json": True}
    assert invalid == {"score": 0.0, "exact": False, "valid_json": False}


def test_stateful_memory_loop_adapter_prepares_and_commits_turn(svc) -> None:
    memory = svc.memory.propose(
        "procedure",
        2,
        "Repository verification must preserve evidence provenance.",
        None,
        ["project"],
        evidence=[
            {
                "evidence_kind": "procedure",
                "claim": "Verification rule",
                "value": "preserve evidence provenance",
                "slot": "constraint",
                "confidence": 1.0,
            }
        ],
    )
    svc.memory.commit(memory.id, None)
    state = ExecutionState(
        task_id="stateful-loop",
        values={"step": 0, "status": "running", "nested": {"keep": "yes"}},
    )
    adapter = StatefulMemoryLoopAdapter(svc.loop, ExecutionStateEngine(SCHEMA))

    prepared = adapter.prepare_turn(
        "Verify the repository",
        state,
        {"tool": "pytest", "status": "PASS"},
        actor_id=None,
        scope=["project"],
    )
    prompt = json.loads(prepared.model_prompt)
    updated = adapter.commit_patch(
        prepared,
        {"step": 1, "status": "complete"},
    )

    assert prompt["task_spec"] == "Verify the repository"
    assert prompt["execution_state"]["revision"] == 0
    assert prompt["latest_observation"]["status"] == "PASS"
    assert prompt["governed_context"]["evidence"][0]["value"] == ("preserve evidence provenance")
    assert prompt["output_contract"]["state_patch"] == "object"
    assert state.revision == 0
    assert updated.revision == 1
    assert updated.values["status"] == "complete"


def test_execution_state_cli_lifecycle_and_revision_conflict(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0

    initialized = runner.invoke(
        app,
        [
            "state",
            "init",
            "--task",
            "release-alpha",
            "--goal",
            "verify bounded state",
            "--db",
            str(db),
            "--json",
        ],
    )
    assert initialized.exit_code == 0, initialized.output
    assert json.loads(initialized.output)["payload"]["state"]["revision"] == 0

    patched = runner.invoke(
        app,
        [
            "state",
            "patch",
            "--task",
            "release-alpha",
            "--expected-revision",
            "0",
            "--patch",
            '{"phase":"verification","completed":["tests"]}',
            "--observation",
            '{"command":"pytest","status":"PASS"}',
            "--quality",
            "pass",
            "--db",
            str(db),
            "--json",
        ],
    )
    assert patched.exit_code == 0, patched.output
    patched_payload = json.loads(patched.output)["payload"]
    assert patched_payload["state"]["revision"] == 1
    assert patched_payload["state"]["values"]["last_observation"] == {
        "command": "pytest",
        "status": "PASS",
    }
    assert patched_payload["telemetry"]["turns"] == 1

    stale = runner.invoke(
        app,
        [
            "state",
            "patch",
            "--task",
            "release-alpha",
            "--expected-revision",
            "0",
            "--patch",
            '{"phase":"release"}',
            "--observation",
            '{"status":"PASS"}',
            "--db",
            str(db),
        ],
    )
    assert stale.exit_code != 0
    assert "revision conflict" in stale.output

    metrics = runner.invoke(app, ["state", "metrics", "--db", str(db), "--json"])
    assert metrics.exit_code == 0, metrics.output
    metrics_payload = json.loads(metrics.output)
    assert metrics_payload["decision"] == "INSUFFICIENT_DATA"
    assert metrics_payload["revision_conflicts"] == 1

    removed = runner.invoke(
        app,
        [
            "state",
            "remove",
            "--task",
            "release-alpha",
            "--confirm",
            "--db",
            str(db),
            "--json",
        ],
    )
    assert removed.exit_code == 0, removed.output
    assert json.loads(removed.output)["removed"] is True


def test_execution_state_benchmark_cli_replays_checkpoints(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    for step in range(3):
        checkpoint = runner.invoke(
            app,
            [
                "checkpoint",
                "add",
                "--task",
                "benchmark-task",
                "--summary",
                f"step {step}",
                "--next",
                "continue",
                "--db",
                str(db),
                "--json",
            ],
        )
        assert checkpoint.exit_code == 0, checkpoint.output

    result = runner.invoke(
        app,
        [
            "benchmark",
            "execution-state",
            "--latency-iterations",
            "20",
            "--db",
            str(db),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["decision"] == "KEEP"
    assert payload["replay"]["checkpoints"] == 3
    assert payload["replay"]["fidelity"] == 1.0
