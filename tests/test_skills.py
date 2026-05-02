from __future__ import annotations

import json

from typer.testing import CliRunner

from oacs.cli.main import app


def _write_echo_script_skill(tmp_path):
    skill_dir = tmp_path / ".skills" / "echo_script"
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    (skill_dir / "skill.json").write_text(
        json.dumps(
            {
                "id": "skill_echo_script",
                "name": "echo_script",
                "version": "0.1",
                "entrypoint": "script:scripts/echo.py",
            }
        ),
        encoding="utf-8",
    )
    (scripts_dir / "echo.py").write_text(
        "import json, sys\n"
        "payload = json.loads(sys.stdin.read() or '{}')\n"
        "print(json.dumps({'seen': payload.get('value')}))\n",
        encoding="utf-8",
    )
    return skill_dir


def test_builtin_skills_and_scan(svc, tmp_path):
    assert any(s.name == "memory_critical_solver" for s in svc.skills.list())
    folder = tmp_path / ".skills" / "demo"
    folder.mkdir(parents=True)
    (folder / "skill.json").write_text(
        json.dumps({"name": "demo", "version": "0.1", "entrypoint": "builtin"})
    )
    scanned = svc.skills.scan(str(tmp_path / ".skills"))
    assert scanned[0].name == "demo"


def test_cli_skill_run_script_skill_from_scanned_source_path(tmp_path):
    db = tmp_path / "oacs.db"
    skill_dir = _write_echo_script_skill(tmp_path)

    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    scan = runner.invoke(
        app, ["skill", "scan", str(tmp_path / ".skills"), "--db", str(db), "--json"]
    )
    assert scan.exit_code == 0, scan.output
    scanned = json.loads(scan.output)
    assert scanned[0]["source_path"] == str(skill_dir)
    result = runner.invoke(
        app,
        [
            "skill",
            "run",
            "echo_script",
            "--db",
            str(db),
            "--payload",
            json.dumps({"value": "ok"}),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["seen"] == "ok"


def test_cli_script_skill_requires_skill_run_capability_for_actor(tmp_path):
    db = tmp_path / "oacs.db"
    _write_echo_script_skill(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    scan = runner.invoke(
        app, ["skill", "scan", str(tmp_path / ".skills"), "--db", str(db), "--json"]
    )
    assert scan.exit_code == 0, scan.output
    actor = runner.invoke(
        app,
        ["actor", "create", "--db", str(db), "--type", "agent", "--name", "Runner", "--json"],
    )
    actor_id = json.loads(actor.output)["id"]

    denied = runner.invoke(
        app,
        [
            "skill",
            "run",
            "echo_script",
            "--actor",
            actor_id,
            "--db",
            str(db),
            "--payload",
            json.dumps({"value": "denied"}),
            "--json",
        ],
    )
    assert denied.exit_code != 0

    grant = runner.invoke(
        app,
        [
            "capability",
            "grant",
            "--db",
            str(db),
            "--subject",
            actor_id,
            "--operation",
            "skill.run",
            "--skill",
            "echo_script",
            "--json",
        ],
    )
    assert grant.exit_code == 0, grant.output

    allowed = runner.invoke(
        app,
        [
            "skill",
            "run",
            "echo_script",
            "--actor",
            actor_id,
            "--db",
            str(db),
            "--payload",
            json.dumps({"value": "allowed"}),
            "--json",
        ],
    )
    assert allowed.exit_code == 0, allowed.output
    assert json.loads(allowed.output)["seen"] == "allowed"
