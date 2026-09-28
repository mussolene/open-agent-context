from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from typer.testing import CliRunner

from oacs.app import services
from oacs.cli.main import app
from oacs.core.config import discover_project_db, project_db_path
from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.integrations.codex.installer import doctor, install, status, uninstall
from oacs.integrations.codex.runtime import build_codex_context, run_hook


def _init_store(db: Path, text: str | None, scope: str) -> None:
    svc = services(str(db), require_key=False)
    svc.key_provider.generate()
    svc.store.set_metadata("encryption_mode", "local_unlocked")
    if text is None:
        return
    writable = services(str(db))
    memory = writable.memory.propose("fact", 2, text, None, [scope])
    writable.memory.commit(memory.id, None)


def _project(tmp_path: Path, name: str) -> tuple[Path, Path]:
    root = tmp_path / name
    root.mkdir()
    (root / ".git").mkdir()
    db = root / ".agent" / "oacs" / "oacs.db"
    return root, db


def _checkpoint(db: Path, task: str, summary: str, next_step: str) -> str:
    svc = services(str(db), require_key=False)
    now = now_iso()
    payload = {
        "kind": "checkpoint",
        "task": task,
        "summary": summary,
        "next": next_step,
        "evidence_refs": [],
    }
    checkpoint_id = new_id("trace")
    svc.store.put_json(
        "task_traces",
        {
            "id": checkpoint_id,
            "payload": payload,
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "namespace": "default",
            "scope": ["project"],
            "owner_actor_id": None,
            "content_hash": hash_json(payload),
        },
    )
    return checkpoint_id


def test_project_memory_retrieval_and_subject_query(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Alpha deploys with make release-safe.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    result = build_codex_context(query="How does Alpha deploy?", cwd=root)

    assert result["intent"] == "repo_development"
    assert result["query"] == "How does Alpha deploy?"
    assert result["project"]["memory_count"] == 1  # type: ignore[index]
    assert "Alpha deploys with make release-safe." in result["prompt"]


def test_global_memory_retrieval(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, None, "project")
    _init_store(global_db, "Across projects, prefer reproducible checks.", "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    result = build_codex_context(query="Which reproducible checks should I prefer?", cwd=root)

    assert result["global"]["memory_count"] == 1  # type: ignore[index]
    assert "Across projects, prefer reproducible checks." in result["prompt"]


def test_project_and_global_merge_prioritizes_project_budget(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Alpha uses project-specific verification.", "project")
    _init_store(global_db, "Verification should be reproducible.", "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    result = build_codex_context(query="Alpha verification", cwd=root, budget=400)

    assert result["project"]["capsule"]["token_budget"] == 300  # type: ignore[index]
    assert result["global"]["capsule"]["token_budget"] == 100  # type: ignore[index]
    assert "Alpha uses project-specific verification." in result["prompt"]
    assert "Verification should be reproducible." in result["prompt"]


def test_cross_project_memory_does_not_leak(tmp_path, monkeypatch) -> None:
    project_a, db_a = _project(tmp_path, "alpha")
    project_b, db_b = _project(tmp_path, "beta")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(db_a, "Alpha private architecture finding.", "project")
    _init_store(db_b, "Beta architecture finding.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    result = build_codex_context(query="architecture finding", cwd=project_b)

    assert project_a != project_b
    assert "Beta architecture finding." in result["prompt"]
    assert "Alpha private architecture finding." not in result["prompt"]


def test_nested_repository_does_not_use_parent_project_memory(tmp_path, monkeypatch) -> None:
    parent, parent_db = _project(tmp_path, "parent")
    child = parent / "child"
    child.mkdir()
    (child / ".git").mkdir()
    _init_store(parent_db, "Parent-only private memory.", "project")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    assert discover_project_db(child) is None
    assert project_db_path(child) == child / ".agent" / "oacs" / "oacs.db"
    result = build_codex_context(query="private memory", cwd=child)

    assert result["project"] is None
    assert {item["reason"] for item in result["warnings"]} == {"storage_unavailable"}
    assert "Parent-only private memory." not in result["prompt"]


def test_doctor_rejects_unreadable_and_shadowed_project_memory(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Current project memory.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    install(home)

    memory_id = services(str(project_db)).memory.query("Current project", None, ["project"])[0].id
    with sqlite3.connect(project_db) as connection:
        connection.execute(
            "UPDATE memory_records SET content_ciphertext = ? WHERE id = ?",
            (b"invalid ciphertext", memory_id),
        )
    legacy_db = root / ".oacs" / "oacs.db"
    _init_store(legacy_db, "Older project memory.", "project")

    diagnosis = doctor(home, query="project memory")
    checks = {item["name"]: item for item in diagnosis["checks"]}

    assert diagnosis["status"] == "FAIL"
    assert checks["memory_readability"]["count"] == 1
    assert checks["project_memory_visibility"]["count"] == 1
    assert "shadowed_legacy_storage" in {
        item["reason"] for item in diagnosis["context"]["warnings"]
    }


def test_doctor_rejects_locked_project_store(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Project memory requiring a key.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    install(home)
    (project_db.parent / "unlocked.key").unlink()

    diagnosis = doctor(home, query="project memory")
    checks = {item["name"]: item for item in diagnosis["checks"]}

    assert diagnosis["status"] == "FAIL"
    assert checks["project_context_access"]["status"] == "FAIL"
    assert checks["global_context_access"]["status"] == "PASS"


def test_rendered_content_and_empty_retrieval(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Unrelated memory topic.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    result = build_codex_context(query="No lexical overlap whatsoever", cwd=root)

    assert result["project"]["memory_count"] == 0  # type: ignore[index]
    assert "## D0-D2 Facts, Preferences, And Procedures" in result["prompt"]
    assert "Unrelated memory topic." not in result["prompt"]


def test_unavailable_stores_are_reported_without_fallback(tmp_path, monkeypatch) -> None:
    root, _ = _project(tmp_path, "alpha")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(tmp_path / "missing" / "oacs.db"))

    result = build_codex_context(query="Alpha task", cwd=root)

    assert result["project"] is None
    assert result["global"] is None
    assert {item["store"] for item in result["warnings"]} == {"project", "global"}
    assert not (root / ".agent" / "oacs" / "oacs.db").exists()


def test_checkpoint_restoration_and_compaction_hook(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Integration tests use a compaction recovery procedure.", "project")
    _init_store(global_db, None, "global")
    checkpoint_id = _checkpoint(project_db, "finish integration", "code changed", "run tests")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    output = run_hook(
        {"hook_event_name": "SessionStart", "source": "compact", "cwd": str(root)}
    )

    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
    assert checkpoint_id in context
    assert "finish integration" in context
    assert "run tests" in context
    assert "Project Historical Context" not in context


def test_checkpoint_restores_when_historical_store_is_locked(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "missing-global" / "oacs.db"
    _init_store(project_db, None, "project")
    checkpoint_id = _checkpoint(project_db, "recover locked task", "state saved", "continue")
    (project_db.parent / "unlocked.key").unlink()
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    output = run_hook(
        {"hook_event_name": "SessionStart", "source": "compact", "cwd": str(root)}
    )

    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
    assert checkpoint_id in context
    assert "recover locked task" in context
    assert "Historical Context" not in context


def test_new_user_instruction_overrides_stale_checkpoint(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Migration context for the new architecture.", "project")
    _init_store(global_db, None, "global")
    _checkpoint(project_db, "old objective", "old work", "continue old objective")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    prompt = (
        "Implement the new architecture and ignore the previous objective "
        "because scope changed."
    )

    output = run_hook(
        {"hook_event_name": "UserPromptSubmit", "prompt": prompt, "cwd": str(root)}
    )

    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
    assert prompt in context
    assert "current explicit user instruction is authoritative" in context.lower()
    assert "old objective" in context


def test_short_prompt_skips_semantic_retrieval(tmp_path) -> None:
    root, _ = _project(tmp_path, "alpha")

    assert run_hook(
        {"hook_event_name": "UserPromptSubmit", "prompt": "Спасибо", "cwd": str(root)}
    ) is None


def test_short_but_substantial_audit_prompt_runs_retrieval(tmp_path, monkeypatch) -> None:
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Architecture audit procedure.", "project")
    _init_store(global_db, None, "global")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))

    output = run_hook(
        {
            "hook_event_name": "UserPromptSubmit",
            "prompt": "Проведи аудит архитектуры и проверь восстановление состояния",
            "cwd": str(root),
        }
    )

    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
    assert "Проведи аудит архитектуры" in context
    assert "current explicit user instruction is authoritative" in context.lower()


def test_install_status_doctor_uninstall_and_idempotence(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "Doctor verifies rendered memory text.", "project")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "AGENTS.md").write_text("User policy.\n", encoding="utf-8")
    (home / ".codex" / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {"type": "command", "command": "python3 keep_user_hook.py"}
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    first = install(home)
    second = install(home)
    hooks = json.loads((home / ".codex" / "hooks.json").read_text(encoding="utf-8"))

    assert first["installed"] is True
    assert second["installed"] is True
    assert len(hooks["hooks"]["SessionStart"]) == 1
    assert len(hooks["hooks"]["UserPromptSubmit"]) == 1
    assert hooks["hooks"]["Stop"][0]["hooks"][0]["command"] == "python3 keep_user_hook.py"
    proof_loop = home / ".agents" / "skills" / "proof-loop" / "SKILL.md"
    assert proof_loop.is_file()
    assert "Use OACS as the durable state" in proof_loop.read_text(encoding="utf-8")
    agents = (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.count("OACS CODEX INTEGRATION START") == 1
    assert "User policy." in agents
    assert status(home)["installed"] is True

    diagnosis = doctor(home, query="Doctor rendered memory")
    assert diagnosis["status"] == "PASS"
    assert "Doctor verifies rendered memory text." in diagnosis["context"]["prompt"]

    removed = uninstall(home)
    assert removed["installed"] is False
    assert removed["persistent_memory_preserved"] is True
    assert not proof_loop.exists()
    assert global_db.exists()
    assert "User policy." in (home / ".codex" / "AGENTS.md").read_text(encoding="utf-8")
    hooks_after = json.loads((home / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    assert "Stop" in hooks_after["hooks"]


def test_cli_install_status_doctor_and_uninstall(tmp_path, monkeypatch) -> None:
    home = tmp_path / "home"
    root, project_db = _project(tmp_path, "alpha")
    global_db = tmp_path / "global" / "oacs.db"
    _init_store(project_db, "CLI doctor memory.", "project")
    monkeypatch.setenv("OACS_GLOBAL_DB", str(global_db))
    monkeypatch.chdir(root)
    runner = CliRunner()

    installed = runner.invoke(
        app, ["integrations", "codex", "install", "--home", str(home), "--json"]
    )
    checked = runner.invoke(
        app,
        [
            "integrations",
            "codex",
            "doctor",
            "--home",
            str(home),
            "--query",
            "CLI doctor",
            "--json",
        ],
    )
    removed = runner.invoke(
        app, ["integrations", "codex", "uninstall", "--home", str(home), "--json"]
    )

    assert installed.exit_code == 0, installed.output
    assert checked.exit_code == 0, checked.output
    assert json.loads(checked.output)["status"] == "PASS"
    assert removed.exit_code == 0, removed.output


def test_install_does_not_overwrite_unmanaged_skill(tmp_path) -> None:
    home = tmp_path / "home"
    skill = home / ".agents" / "skills" / "oacs"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("user-owned skill\n", encoding="utf-8")

    try:
        install(home)
    except ValueError as exc:
        assert "unmanaged Codex Skill" in str(exc)
    else:
        raise AssertionError("install unexpectedly replaced an unmanaged skill")

    assert (skill / "SKILL.md").read_text(encoding="utf-8") == "user-owned skill\n"


def test_install_preflight_does_not_partially_replace_skills(tmp_path: Path) -> None:
    home = tmp_path / "home"
    oacs_skill = home / ".agents" / "skills" / "oacs"
    proof_loop_skill = home / ".agents" / "skills" / "proof-loop"
    oacs_skill.mkdir(parents=True)
    proof_loop_skill.mkdir(parents=True)
    (oacs_skill / ".managed-by-oacs").write_text("managed\n", encoding="utf-8")
    (oacs_skill / "SKILL.md").write_text("old managed copy\n", encoding="utf-8")
    (proof_loop_skill / "SKILL.md").write_text("user-owned proof loop\n", encoding="utf-8")

    try:
        install(home)
    except ValueError as exc:
        assert "proof-loop" in str(exc)
    else:
        raise AssertionError("install unexpectedly replaced an unmanaged skill")

    assert (oacs_skill / "SKILL.md").read_text(encoding="utf-8") == "old managed copy\n"
    assert (proof_loop_skill / "SKILL.md").read_text(encoding="utf-8") == (
        "user-owned proof loop\n"
    )


def test_packaged_proof_loop_uses_oacs_without_parallel_task_tree() -> None:
    root = Path(__file__).resolve().parents[1]
    skill_root = root / "oacs" / "integrations" / "shared_assets" / "proof-loop"
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    protocol = (skill_root / "references" / "protocol.md").read_text(encoding="utf-8")

    assert "name: proof-loop" in skill
    assert "only durable task-state" in skill
    assert "Do not create `.agent/tasks/`" in skill
    assert "task-spec-freezer" in skill
    assert (skill_root / "agents" / "openai.yaml").is_file()
    assert "every acceptance criterion is `PASS`" in protocol
    assert ".agent/tasks/<TASK_ID>" not in protocol
