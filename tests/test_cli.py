from __future__ import annotations

from typer.testing import CliRunner

from oacs.cli.main import app
from oacs.context.capsule import ContextCapsule


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
