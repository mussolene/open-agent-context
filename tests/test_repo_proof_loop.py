from __future__ import annotations

import json

from typer.testing import CliRunner

from oacs.app import services
from oacs.cli.main import app
from oacs.repo.proof_loop import (
    RepoProofCaptureRequest,
    RepoProofContextRequest,
    RepoProofLoopAdapter,
    RepoProofStatusRequest,
)


def test_repo_proof_loop_adapter_capture_context_status(tmp_path):
    svc = services(str(tmp_path / "oacs.db"), require_key=False)
    task_dir = tmp_path / ".agent" / "tasks" / "adapter-task"
    task_dir.mkdir(parents=True)
    (task_dir / "spec.md").write_text("# Spec\n\nAC1 proof.\n", encoding="utf-8")
    (task_dir / "verdict.json").write_text('{"overall": "PASS"}', encoding="utf-8")
    adapter = RepoProofLoopAdapter(svc)

    captured = adapter.capture(
        RepoProofCaptureRequest(
            task_id="adapter-task",
            phase="spec",
            summary="frozen spec",
            cwd=tmp_path,
            artifacts=[task_dir / "spec.md"],
        )
    )
    context = adapter.context(
        RepoProofContextRequest(task_id="adapter-task", intent="continue adapter", cwd=tmp_path)
    )
    status = adapter.status(RepoProofStatusRequest(task_id="adapter-task", cwd=tmp_path))

    assert captured["memory_id"] in context["capsule"]["included_memories"]
    assert context["capsule"]["task_id"] == "adapter-task"
    assert captured["memory_id"] in status["memory_ids"]
    assert status["artifacts"]["verdict"]["json"]["overall"] == "PASS"


def test_repo_proof_loop_adapter_isolates_repo_and_task_scope(tmp_path):
    svc = services(str(tmp_path / "oacs.db"), require_key=False)
    adapter = RepoProofLoopAdapter(svc)
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    repo_a.mkdir()
    repo_b.mkdir()

    repo_a_same = adapter.capture(
        RepoProofCaptureRequest(
            task_id="same-task", phase="build", summary="repo a same task", cwd=repo_a
        )
    )["memory_id"]
    repo_b_same = adapter.capture(
        RepoProofCaptureRequest(
            task_id="same-task", phase="build", summary="repo b same task", cwd=repo_b
        )
    )["memory_id"]
    repo_a_other = adapter.capture(
        RepoProofCaptureRequest(
            task_id="other-task", phase="build", summary="repo a other task", cwd=repo_a
        )
    )["memory_id"]

    context = adapter.context(
        RepoProofContextRequest(task_id="same-task", intent="continue same task", cwd=repo_a)
    )
    status = adapter.status(RepoProofStatusRequest(task_id="same-task", cwd=repo_a))

    assert repo_a_same in context["capsule"]["included_memories"]
    assert repo_b_same not in context["capsule"]["included_memories"]
    assert repo_a_other not in context["capsule"]["included_memories"]
    assert repo_a_same in status["memory_ids"]
    assert repo_b_same not in status["memory_ids"]
    assert repo_a_other not in status["memory_ids"]


def test_cli_repo_proof_commands_emit_json(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    task_dir = tmp_path / ".agent" / "tasks" / "cli-task"
    task_dir.mkdir(parents=True)
    (task_dir / "spec.md").write_text("# CLI Spec\n", encoding="utf-8")

    capture = runner.invoke(
        app,
        [
            "repo",
            "proof-capture",
            "--db",
            str(db),
            "--cwd",
            str(tmp_path),
            "--task-id",
            "cli-task",
            "--phase",
            "spec",
            "--summary",
            "captured via cli",
            "--artifact",
            str(task_dir / "spec.md"),
            "--json",
        ],
    )
    assert capture.exit_code == 0, capture.output
    memory_id = json.loads(capture.output)["memory_id"]

    context = runner.invoke(
        app,
        [
            "repo",
            "proof-context",
            "--db",
            str(db),
            "--cwd",
            str(tmp_path),
            "--task-id",
            "cli-task",
            "--json",
        ],
    )
    assert context.exit_code == 0, context.output
    assert memory_id in context.output

    status = runner.invoke(
        app,
        [
            "repo",
            "proof-status",
            "--db",
            str(db),
            "--cwd",
            str(tmp_path),
            "--task-id",
            "cli-task",
            "--json",
        ],
    )
    assert status.exit_code == 0, status.output
    assert memory_id in json.loads(status.output)["memory_ids"]


def test_cli_grant_shared_memory_enforces_scope(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    actor = runner.invoke(
        app,
        ["actor", "create", "--db", str(db), "--type", "agent", "--name", "Subagent", "--json"],
    )
    actor_id = json.loads(actor.output)["id"]
    grant = runner.invoke(
        app,
        [
            "capability",
            "grant-shared-memory",
            "--db",
            str(db),
            "--subject",
            actor_id,
            "--scope",
            "task:allowed",
            "--json",
        ],
    )
    assert grant.exit_code == 0, grant.output
    assert json.loads(grant.output)["grant"]["scope"] == ["task:allowed"]

    allowed = runner.invoke(
        app,
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--type",
            "fact",
            "--depth",
            "2",
            "--scope",
            "task:allowed",
            "--text",
            "allowed cli memory",
            "--json",
        ],
    )
    other = runner.invoke(
        app,
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--type",
            "fact",
            "--depth",
            "2",
            "--scope",
            "task:other",
            "--text",
            "other cli memory",
            "--json",
        ],
    )
    allowed_id = json.loads(allowed.output)["id"]
    other_id = json.loads(other.output)["id"]
    assert (
        runner.invoke(app, ["memory", "commit", allowed_id, "--db", str(db), "--json"]).exit_code
        == 0
    )
    assert (
        runner.invoke(app, ["memory", "commit", other_id, "--db", str(db), "--json"]).exit_code
        == 0
    )

    query = runner.invoke(
        app,
        [
            "memory",
            "query",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--scope",
            "task:allowed",
            "--query",
            "cli memory",
            "--json",
        ],
    )
    assert query.exit_code == 0, query.output
    assert allowed_id in query.output
    assert other_id not in query.output

    denied_read = runner.invoke(
        app,
        ["memory", "read", other_id, "--db", str(db), "--actor", actor_id, "--json"],
    )
    assert denied_read.exit_code != 0
