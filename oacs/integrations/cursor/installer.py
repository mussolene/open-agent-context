from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from oacs.core.config import global_db_path
from oacs.integrations.common import (
    context_health_checks,
    ensure_global_storage,
    install_skills,
    load_json_object,
    remove_skills,
    skills_status,
    write_json,
)
from oacs.integrations.runtime import build_agent_context, resolve_project


def integration_paths(home: Path | None = None) -> dict[str, Path]:
    user_home = (home or Path.home()).expanduser().resolve()
    root = user_home / ".cursor"
    return {
        "home": user_home,
        "root": root,
        "skills_root": root / "skills",
        "hooks_file": root / "hooks.json",
        "hook_script": root / "skills" / "oacs" / "scripts" / "oacs_hook.py",
    }


def install(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    install_skills(paths["skills_root"], "cursor")
    payload = load_json_object(paths["hooks_file"], {"version": 1, "hooks": {}})
    payload.setdefault("version", 1)
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"hooks field must contain an object: {paths['hooks_file']}")
    _remove_hooks(hooks)
    command = f'{sys.executable} "{paths["hook_script"]}"'
    hooks.setdefault("sessionStart", []).append({"command": command})
    write_json(paths["hooks_file"], payload)
    ensure_global_storage()
    return status(home)


def status(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    skills = skills_status(paths["skills_root"])
    payload = load_json_object(paths["hooks_file"], {"version": 1, "hooks": {}})
    hooks = payload.get("hooks") if isinstance(payload.get("hooks"), dict) else {}
    project = resolve_project()
    hook_ok = _has_hook(hooks)
    return {
        "installed": all(item["installed"] for item in skills.values()) and hook_ok,
        "skills": skills,
        "policy": {
            "delivery": "skills",
            "installed": all(item["installed"] for item in skills.values()),
            "reason": "Cursor has no merge-safe global policy file contract.",
        },
        "hooks": {
            "path": str(paths["hooks_file"]),
            "installed": hook_ok,
            "events": ["sessionStart"],
            "semantic_prompt_retrieval": "skill_driven",
            "post_compaction_recovery": "skill_driven",
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


def doctor(home: Path | None = None, query: str = "OACS Cursor integration") -> dict[str, object]:
    snapshot: dict[str, Any] = status(home)
    skills = snapshot["skills"]
    checks: list[dict[str, object]] = [
        {"name": "oacs_skill_discovered", "status": _pass(skills["oacs"]["installed"])},
        {"name": "proof_loop_skill_discovered", "status": _pass(skills["proof-loop"]["installed"])},
        {"name": "policy_contract", "status": _pass(snapshot["policy"]["installed"])},
        {"name": "session_start_hook", "status": _pass(snapshot["hooks"]["installed"])},
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
        "limitations": [
            "Cursor beforeSubmitPrompt cannot inject additional context.",
            "Cursor preCompact cannot modify compaction or inject post-compaction context.",
            "User-level Cursor hooks are unavailable to Cloud Agents.",
        ],
        "context": context,
        "installation": snapshot,
    }


def uninstall(home: Path | None = None) -> dict[str, Any]:
    paths = integration_paths(home)
    remove_skills(paths["skills_root"])
    if paths["hooks_file"].exists():
        payload = load_json_object(paths["hooks_file"], {"version": 1, "hooks": {}})
        hooks = payload.get("hooks")
        if isinstance(hooks, dict):
            _remove_hooks(hooks)
        write_json(paths["hooks_file"], payload)
    result = status(home)
    result["persistent_memory_preserved"] = True
    return result


def _pass(value: object) -> str:
    return "PASS" if bool(value) else "FAIL"


def _is_oacs_hook(item: object) -> bool:
    return isinstance(item, dict) and "/oacs/scripts/oacs_hook.py" in str(
        item.get("command", "")
    )


def _remove_hooks(hooks: dict[str, Any]) -> None:
    items = hooks.get("sessionStart")
    if not isinstance(items, list):
        return
    kept = [item for item in items if not _is_oacs_hook(item)]
    if kept:
        hooks["sessionStart"] = kept
    else:
        hooks.pop("sessionStart", None)


def _has_hook(hooks: object) -> bool:
    return isinstance(hooks, dict) and any(
        _is_oacs_hook(item) for item in hooks.get("sessionStart", [])
    )
