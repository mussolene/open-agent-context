from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from oacs.app import services
from oacs.cli.main import app
from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.integrations.claude.installer import (
    doctor as claude_doctor,
)
from oacs.integrations.claude.installer import (
    install as claude_install,
)
from oacs.integrations.claude.installer import (
    uninstall as claude_uninstall,
)
from oacs.integrations.codex.installer import doctor as codex_doctor
from oacs.integrations.codex.installer import install as codex_install
from oacs.integrations.cursor.installer import (
    doctor as cursor_doctor,
)
from oacs.integrations.cursor.installer import (
    install as cursor_install,
)
from oacs.integrations.cursor.installer import (
    uninstall as cursor_uninstall,
)
from oacs.integrations.runtime import run_cursor_hook, run_hook


def _store(db: Path, text: str | None, scope: str) -> None:
    service = services(str(db), require_key=False)
    service.key_provider.generate()
    service.store.set_metadata("encryption_mode", "local_unlocked")
    if text:
        memory = services(str(db)).memory.propose("fact", 2, text, None, [scope])
        services(str(db)).memory.commit(memory.id, None)


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    (root / ".git").mkdir()
    return root, root / ".agent" / "oacs" / "oacs.db"


def _checkpoint(db: Path) -> str:
    service = services(str(db), require_key=False)
    timestamp = now_iso()
    payload = {
        "kind": "checkpoint",
        "task": "client integration",
        "summary": "client files installed",
        "next": "verify lifecycle",
        "evidence_refs": [],
    }
    checkpoint_id = new_id("trace")
    service.store.put_json(
        "task_traces",
        {
            "id": checkpoint_id,
            "payload": payload,
            "created_at": timestamp,
            "updated_at": timestamp,
            "status": "active",
            "namespace": "default",
            "scope": ["project"],
            "owner_actor_id": None,
            "content_hash": hash_json(payload),
        },
    )
    return checkpoint_id


def test_claude_install_lifecycle_and_uninstall_are_merge_safe(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    global_db = tmp_path / "global" / "oacs.db"
    _store(project_db, "Claude receives rendered project memory.", "project")
    _store(global_db, None, "global")
    checkpoint_id = _checkpoint(project_db)
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "CLAUDE.md").write_text("User policy.\n", encoding="utf-8")
    (home / ".claude" / "settings.json").write_text(
        json.dumps({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "keep"}]}]}}),
        encoding="utf-8",
    )

    first = claude_install(home)
    second = claude_install(home)
    settings = json.loads((home / ".claude" / "settings.json").read_text(encoding="utf-8"))

    assert first["installed"] is True
    assert second["installed"] is True
    events = ("SessionStart", "UserPromptSubmit", "PostCompact")
    assert all(len(settings["hooks"][event]) == 1 for event in events)
    assert settings["hooks"]["Stop"][0]["hooks"][0]["command"] == "keep"
    assert "User policy." in (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
    restored = run_hook({"hook_event_name": "PostCompact", "cwd": str(root)})
    assert restored is not None
    assert checkpoint_id in restored["hookSpecificOutput"]["additionalContext"]
    assert claude_doctor(home, "Claude rendered memory")["status"] == "PASS"

    removed = claude_uninstall(home)
    assert removed["installed"] is False
    assert removed["persistent_memory_preserved"] is True
    assert global_db.exists()
    assert "User policy." in (home / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")


def test_cursor_install_session_recovery_and_uninstall_are_merge_safe(
    tmp_path, monkeypatch
) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    global_db = tmp_path / "global" / "oacs.db"
    _store(project_db, "Cursor receives rendered project memory.", "project")
    _store(global_db, None, "global")
    checkpoint_id = _checkpoint(project_db)
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    (home / ".cursor").mkdir(parents=True)
    (home / ".cursor" / "hooks.json").write_text(
        json.dumps({"version": 1, "hooks": {"stop": [{"command": "keep"}]}}),
        encoding="utf-8",
    )

    first = cursor_install(home)
    second = cursor_install(home)
    hooks = json.loads((home / ".cursor" / "hooks.json").read_text(encoding="utf-8"))

    assert first["installed"] is True
    assert second["installed"] is True
    assert len(hooks["hooks"]["sessionStart"]) == 1
    assert hooks["hooks"]["stop"][0]["command"] == "keep"
    restored = run_cursor_hook(
        {"hook_event_name": "sessionStart", "workspace_roots": [str(root)]}
    )
    assert restored is not None
    assert checkpoint_id in restored["additional_context"]
    diagnosis = cursor_doctor(home, "Cursor rendered memory")
    assert diagnosis["status"] == "PASS"
    assert diagnosis["limitations"]

    removed = cursor_uninstall(home)
    assert removed["installed"] is False
    assert removed["persistent_memory_preserved"] is True
    assert global_db.exists()
    remaining = json.loads((home / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    assert remaining["hooks"]["stop"][0]["command"] == "keep"


def test_claude_and_cursor_cli_lifecycle(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    global_db = tmp_path / "global" / "oacs.db"
    _store(project_db, "CLI integration memory.", "project")
    _store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    runner = CliRunner()

    for client in ("claude", "cursor"):
        installed = runner.invoke(
            app, ["integrations", client, "install", "--home", str(home), "--json"]
        )
        diagnosed = runner.invoke(
            app,
            [
                "integrations",
                client,
                "doctor",
                "--home",
                str(home),
                "--query",
                "CLI integration",
                "--json",
            ],
        )
        removed = runner.invoke(
            app, ["integrations", client, "uninstall", "--home", str(home), "--json"]
        )
        assert installed.exit_code == 0, installed.output
        assert diagnosed.exit_code == 0, diagnosed.output
        assert json.loads(diagnosed.output)["status"] == "PASS"
        assert removed.exit_code == 0, removed.output


@pytest.mark.parametrize(
    ("client", "skills_root", "install_fn"),
    [
        ("Claude", ".claude/skills", claude_install),
        ("Cursor", ".cursor/skills", cursor_install),
    ],
)
def test_install_refuses_unmanaged_client_skill(
    tmp_path, client, skills_root, install_fn
) -> None:
    home = tmp_path / "home"
    skill = home / skills_root / "oacs"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("user-owned\n", encoding="utf-8")

    with pytest.raises(ValueError, match=f"unmanaged {client.lower()} Skill"):
        install_fn(home)

    assert (skill / "SKILL.md").read_text(encoding="utf-8") == "user-owned\n"


def test_cursor_does_not_claim_unsupported_prompt_or_compaction_injection() -> None:
    assert run_cursor_hook({"hook_event_name": "beforeSubmitPrompt"}) is None
    assert run_cursor_hook({"hook_event_name": "preCompact"}) is None


@pytest.mark.parametrize(
    ("install_fn", "doctor_fn"),
    [
        (claude_install, claude_doctor),
        (cursor_install, cursor_doctor),
    ],
)
def test_client_doctor_rejects_unreadable_and_shadowed_project_memory(
    tmp_path, monkeypatch, install_fn, doctor_fn
) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    global_db = tmp_path / "global" / "oacs.db"
    _store(project_db, "Current project memory.", "project")
    _store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    install_fn(home)

    memory_id = services(str(project_db)).memory.query(
        "Current project", None, ["project"]
    )[0].id
    with sqlite3.connect(project_db) as connection:
        connection.execute(
            "UPDATE memory_records SET content_ciphertext = ? WHERE id = ?",
            (b"invalid ciphertext", memory_id),
        )
    _store(root / ".oacs" / "oacs.db", "Older project memory.", "project")

    diagnosis = doctor_fn(home, "project memory")
    checks = {item["name"]: item for item in diagnosis["checks"]}

    assert diagnosis["status"] == "FAIL"
    assert checks["memory_readability"]["count"] == 1
    assert checks["project_memory_visibility"]["count"] == 1


@pytest.mark.parametrize(
    ("install_fn", "doctor_fn"),
    [
        (claude_install, claude_doctor),
        (cursor_install, cursor_doctor),
    ],
)
def test_client_doctor_rejects_locked_project_store(
    tmp_path, monkeypatch, install_fn, doctor_fn
) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    global_db = tmp_path / "global" / "oacs.db"
    _store(project_db, "Project memory requiring a key.", "project")
    _store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    install_fn(home)
    (project_db.parent / "unlocked.key").unlink()

    diagnosis = doctor_fn(home, "project memory")
    checks = {item["name"]: item for item in diagnosis["checks"]}

    assert diagnosis["status"] == "FAIL"
    assert checks["project_context_access"]["status"] == "FAIL"
    assert checks["global_context_access"]["status"] == "PASS"


@pytest.mark.parametrize(
    ("install_fn", "doctor_fn"),
    [
        (codex_install, codex_doctor),
        (claude_install, claude_doctor),
        (cursor_install, cursor_doctor),
    ],
)
def test_client_doctor_rejects_corrupt_project_database(
    tmp_path, monkeypatch, install_fn, doctor_fn
) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path)
    project_db.parent.mkdir(parents=True)
    project_db.write_bytes(b"not a sqlite database")
    global_db = tmp_path / "global" / "oacs.db"
    _store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    install_fn(home)

    diagnosis = doctor_fn(home, "project memory")
    checks = {item["name"]: item for item in diagnosis["checks"]}

    assert diagnosis["status"] == "FAIL"
    assert checks["project_context_access"]["status"] == "FAIL"
    assert checks["global_context_access"]["status"] == "PASS"
    assert {item["reason"] for item in diagnosis["context"]["warnings"]} == {
        "DatabaseError"
    }
