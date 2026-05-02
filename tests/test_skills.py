from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from oacs.cli.main import app


def test_builtin_skills_and_scan(svc, tmp_path):
    assert any(s.name == "memory_critical_solver" for s in svc.skills.list())
    folder = tmp_path / ".skills" / "demo"
    folder.mkdir(parents=True)
    (folder / "skill.json").write_text(
        json.dumps({"name": "demo", "version": "0.1", "entrypoint": "builtin"})
    )
    scanned = svc.skills.scan(str(tmp_path / ".skills"))
    assert scanned[0].name == "demo"


def test_repo_development_memory_skill_scans_with_source_path(svc):
    folder = Path("examples/skills")
    scanned = svc.skills.scan(str(folder))
    repo_skill = next(skill for skill in scanned if skill.name == "repo_development_memory")
    assert repo_skill.entrypoint == "script:scripts/repo_memory.py"
    assert repo_skill.source_path


def test_cli_skill_run_repo_development_memory_context(tmp_path):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    scan = runner.invoke(app, ["skill", "scan", "examples/skills", "--db", str(db), "--json"])
    assert scan.exit_code == 0, scan.output
    result = runner.invoke(
        app,
        [
            "skill",
            "run",
            "repo_development_memory",
            "--db",
            str(db),
            "--payload",
            json.dumps({"action": "context", "task": "skill context", "cwd": str(tmp_path)}),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "capsule" in result.output
