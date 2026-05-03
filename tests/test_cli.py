from __future__ import annotations

import json
import sys

from typer.testing import CliRunner

from oacs.cli.main import app
from oacs.context.capsule import ContextCapsule


def test_cli_version():
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == "acs 1.0.3"


def test_cli_init_key_actor_memory(tmp_path):
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
        app, ["actor", "create", "--db", str(db), "--type", "human", "--name", "User", "--json"]
    )
    assert actor.exit_code == 0
    proposed = runner.invoke(
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
            "--text",
            "CLI memory",
            "--json",
        ],
    )
    assert proposed.exit_code == 0, proposed.output


def test_cli_capability_and_capsule_round_trip(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    caps = runner.invoke(app, ["capability", "list", "--db", str(db), "--json"])
    assert caps.exit_code == 0
    assert "memory.read" in caps.output
    capsule = ContextCapsule(purpose="manual", token_budget=1, permissions={}).seal()
    file = tmp_path / "capsule.json"
    file.write_text(capsule.model_dump_json(), encoding="utf-8")
    validate = runner.invoke(
        app, ["context", "validate", "--db", str(db), "--file", str(file), "--json"]
    )
    assert validate.exit_code == 0, validate.output
    imported = runner.invoke(
        app, ["context", "import", "--db", str(db), "--file", str(file), "--json"]
    )
    assert imported.exit_code == 0, imported.output
    exported = runner.invoke(app, ["capsule", "export", capsule.id, "--db", str(db), "--json"])
    assert exported.exit_code == 0
    assert capsule.id in exported.output
    missing = runner.invoke(app, ["context", "lock", "ctx_missing", "--db", str(db), "--json"])
    assert missing.exit_code != 0


def test_cli_repo_is_not_core_surface():
    result = CliRunner().invoke(app, ["repo", "--help"])
    assert result.exit_code != 0


def test_cli_vault_is_not_core_surface():
    result = CliRunner().invoke(app, ["vault", "--help"])
    assert result.exit_code != 0


def test_cli_conformance_validate_json():
    result = CliRunner().invoke(app, ["conformance", "validate", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["valid"] is True
    assert payload["positive_fixtures"] >= 1
    assert payload["negative_fixtures"] >= 1


def test_cli_loop_run_emits_memory_calls(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    proposed = runner.invoke(
        app,
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--type",
            "procedure",
            "--depth",
            "2",
            "--scope",
            "project",
            "--text",
            "Alpha reports use make report-safe.",
            "--json",
        ],
    )
    assert proposed.exit_code == 0, proposed.output
    memory_id = json.loads(proposed.output)["id"]
    committed = runner.invoke(
        app, ["memory", "commit", memory_id, "--db", str(db), "--json"]
    )
    assert committed.exit_code == 0, committed.output

    result = runner.invoke(
        app,
        [
            "loop",
            "run",
            "--db",
            str(db),
            "--request",
            "How do I generate the Alpha report?",
            "--scope",
            "project",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "memory_calls" in result.output
    assert "memory.read" in result.output


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


def test_cli_project_status_and_discovery(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OACS_DB", raising=False)

    initialized = runner.invoke(app, ["init", "--project", "--json"])
    assert initialized.exit_code == 0, initialized.output
    assert json.loads(initialized.output)["db"].endswith(".agent/oacs/oacs.db")

    status = runner.invoke(app, ["status", "--json"])
    assert status.exit_code == 0, status.output
    payload = json.loads(status.output)
    assert payload["db"].endswith(".agent/oacs/oacs.db")
    assert payload["counts"]["evidence_refs"] == 0


def test_cli_checkpoint_resume_and_run(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0

    checkpoint = runner.invoke(
        app,
        [
            "checkpoint",
            "add",
            "--db",
            str(db),
            "--task",
            "agent workflow ux",
            "--summary",
            "status implemented",
            "--next",
            "run verification",
            "--json",
        ],
    )
    assert checkpoint.exit_code == 0, checkpoint.output
    trace_id = json.loads(checkpoint.output)["id"]

    latest = runner.invoke(
        app,
        [
            "checkpoint",
            "latest",
            "--db",
            str(db),
            "--task",
            "agent workflow ux",
            "--json",
        ],
    )
    assert latest.exit_code == 0, latest.output
    assert json.loads(latest.output)["id"] == trace_id

    run = runner.invoke(
        app,
        [
            "run",
            "--db",
            str(db),
            "--label",
            "python smoke",
            "--json",
            "--",
            sys.executable,
            "-c",
            "print('workflow-ok')",
        ],
    )
    assert run.exit_code == 0, run.output
    run_payload = json.loads(run.output)
    assert run_payload["output"]["exit_code"] == 0
    assert "workflow-ok" in run_payload["output"]["stdout"]
    assert run_payload["evidence_ref"].startswith("ev_")

    resume = runner.invoke(app, ["resume", "--db", str(db), "--json"])
    assert resume.exit_code == 0, resume.output
    resume_payload = json.loads(resume.output)
    assert resume_payload["latest_checkpoint"]["summary"] == "status implemented"
    assert resume_payload["recent_tool_results"][0]["payload"]["output"]["label"] == "python smoke"


def test_cli_policy_deny_pattern_blocks_memory_and_ingest(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )

    rule = runner.invoke(
        app,
        [
            "policy",
            "add-deny-pattern",
            "--db",
            str(db),
            "secret-token",
            "--json",
        ],
    )
    assert rule.exit_code == 0, rule.output

    blocked_memory = runner.invoke(
        app,
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--type",
            "fact",
            "--depth",
            "1",
            "--text",
            "contains secret-token",
            "--json",
        ],
    )
    assert blocked_memory.exit_code == 2
    assert json.loads(blocked_memory.output)["status"] == "blocked"

    blocked_ingest = runner.invoke(
        app,
        [
            "tool",
            "ingest-result",
            "--db",
            str(db),
            "--tool-id",
            "external",
            "--output",
            '{"value":"secret-token"}',
            "--json",
        ],
    )
    assert blocked_ingest.exit_code == 2
