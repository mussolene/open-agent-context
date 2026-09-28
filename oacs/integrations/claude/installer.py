from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from oacs.core.config import global_db_path
from oacs.integrations.common import (
    ASSET_ROOT,
    context_health_checks,
    ensure_global_storage,
    install_skills,
    load_json_object,
    merge_marked_block,
    remove_marked_block,
    remove_skills,
    skills_status,
    write_json,
)
from oacs.integrations.runtime import build_agent_context, resolve_project

BLOCK_START = "<!-- OACS CLAUDE INTEGRATION START -->"
BLOCK_END = "<!-- OACS CLAUDE INTEGRATION END -->"


def integration_paths(home: Path | None = None) -> dict[str, Path]:
    user_home = (home or Path.home()).expanduser().resolve()
    root = user_home / ".claude"
    return {
        "home": user_home,
        "root": root,
        "skills_root": root / "skills",
        "policy_file": root / "CLAUDE.md",
        "settings_file": root / "settings.json",
        "hook_script": root / "skills" / "oacs" / "scripts" / "oacs_hook.py",
    }


def install(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    install_skills(paths["skills_root"], "claude")
    policy_file = paths["policy_file"]
    policy_file.parent.mkdir(parents=True, exist_ok=True)
    existing = policy_file.read_text(encoding="utf-8") if policy_file.exists() else ""
    policy_file.write_text(
        merge_marked_block(
            existing,
            (ASSET_ROOT / "global_policy.md").read_text(encoding="utf-8"),
            BLOCK_START,
            BLOCK_END,
        ),
        encoding="utf-8",
    )
    settings = load_json_object(paths["settings_file"], {})
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"hooks field must contain an object: {paths['settings_file']}")
    _remove_hooks(hooks)
    command = f'{sys.executable} "{paths["hook_script"]}"'
    _add_hook(hooks, "SessionStart", command, "startup|resume|clear|compact|fork")
    _add_hook(hooks, "UserPromptSubmit", command)
    _add_hook(hooks, "PostCompact", command, "manual|auto")
    write_json(paths["settings_file"], settings)
    ensure_global_storage()
    return status(home)


def status(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    skills = skills_status(paths["skills_root"])
    policy = (
        paths["policy_file"].read_text(encoding="utf-8")
        if paths["policy_file"].exists()
        else ""
    )
    settings = load_json_object(paths["settings_file"], {})
    hooks = settings.get("hooks") if isinstance(settings.get("hooks"), dict) else {}
    project = resolve_project()
    hook_ok = _has_hooks(hooks)
    return {
        "installed": all(item["installed"] for item in skills.values())
        and BLOCK_START in policy
        and hook_ok,
        "skills": skills,
        "policy": {"path": str(paths["policy_file"]), "installed": BLOCK_START in policy},
        "hooks": {
            "path": str(paths["settings_file"]),
            "installed": hook_ok,
            "events": ["SessionStart", "UserPromptSubmit", "PostCompact"],
        },
        "cli": {"available": shutil.which("acs") is not None},
        "repository": {
            "detected": project is not None,
            "repository_id": project.repository_id if project else None,
            "project_db": str(project.db_path) if project else None,
            "project_storage_available": bool(project and project.db_path.exists()),
        },
        "global_storage": {"db": str(global_db_path()), "available": global_db_path().exists()},
    }


def doctor(home: Path | None = None, query: str = "OACS Claude integration") -> dict[str, object]:
    snapshot: dict[str, Any] = status(home)
    skills = snapshot["skills"]
    checks: list[dict[str, object]] = [
        {"name": "oacs_skill_discovered", "status": _pass(skills["oacs"]["installed"])},
        {"name": "proof_loop_skill_discovered", "status": _pass(skills["proof-loop"]["installed"])},
        {"name": "policy_contract", "status": _pass(snapshot["policy"]["installed"])},
        {"name": "hooks_installed", "status": _pass(snapshot["hooks"]["installed"])},
        {"name": "acs_cli_available", "status": _pass(snapshot["cli"]["available"])},
        {"name": "repository_detected", "status": _pass(snapshot["repository"]["detected"])},
        {
            "name": "project_storage",
            "status": _pass(snapshot["repository"]["project_storage_available"]),
        },
        {"name": "global_storage", "status": _pass(snapshot["global_storage"]["available"])},
    ]
    context = build_agent_context(query=query, current_user_prompt=query)
    checks.extend(context_health_checks(context))
    return {
        "status": "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL",
        "checks": checks,
        "context": context,
        "installation": snapshot,
    }


def uninstall(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    remove_skills(paths["skills_root"])
    if paths["policy_file"].exists():
        paths["policy_file"].write_text(
            remove_marked_block(
                paths["policy_file"].read_text(encoding="utf-8"), BLOCK_START, BLOCK_END
            ),
            encoding="utf-8",
        )
    if paths["settings_file"].exists():
        settings = load_json_object(paths["settings_file"], {})
        hooks = settings.get("hooks")
        if isinstance(hooks, dict):
            _remove_hooks(hooks)
        write_json(paths["settings_file"], settings)
    result = status(home)
    result["persistent_memory_preserved"] = True
    return result


def _pass(value: object) -> str:
    return "PASS" if bool(value) else "FAIL"


def _add_hook(hooks: dict[str, Any], event: str, command: str, matcher: str | None = None) -> None:
    group: dict[str, object] = {
        "hooks": [{"type": "command", "command": command, "timeout": 30}]
    }
    if matcher:
        group["matcher"] = matcher
    hooks.setdefault(event, []).append(group)


def _remove_hooks(hooks: dict[str, Any]) -> None:
    for event in ("SessionStart", "UserPromptSubmit", "PostCompact"):
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        kept = [group for group in groups if not _is_oacs_group(group)]
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event, None)


def _is_oacs_group(group: object) -> bool:
    handlers = group.get("hooks", []) if isinstance(group, dict) else []
    return any(
        "/oacs/scripts/oacs_hook.py" in str(handler.get("command", ""))
        for handler in handlers
        if isinstance(handler, dict)
    )


def _has_hooks(hooks: object) -> bool:
    if not isinstance(hooks, dict):
        return False
    return all(
        any(_is_oacs_group(group) for group in hooks.get(event, []))
        for event in ("SessionStart", "UserPromptSubmit", "PostCompact")
    )
