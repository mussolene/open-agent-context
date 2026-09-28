from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

from oacs.core.config import global_db_path
from oacs.integrations.codex.runtime import build_codex_context, resolve_project
from oacs.integrations.common import (
    ASSET_ROOT,
    SKILL_MARKER,
    context_health_checks,
    ensure_global_storage,
    install_skills,
    merge_marked_block,
    remove_marked_block,
    remove_skills,
)

BLOCK_START = "<!-- OACS CODEX INTEGRATION START -->"
BLOCK_END = "<!-- OACS CODEX INTEGRATION END -->"


def integration_paths(home: Path | None = None) -> dict[str, Path]:
    user_home = (home or Path.home()).expanduser().resolve()
    skill_dir = user_home / ".agents" / "skills" / "oacs"
    proof_loop_skill_dir = user_home / ".agents" / "skills" / "proof-loop"
    return {
        "home": user_home,
        "skill_dir": skill_dir,
        "skill_file": skill_dir / "SKILL.md",
        "proof_loop_skill_dir": proof_loop_skill_dir,
        "proof_loop_skill_file": proof_loop_skill_dir / "SKILL.md",
        "agents_file": user_home / ".codex" / "AGENTS.md",
        "hooks_file": user_home / ".codex" / "hooks.json",
        "hook_script": skill_dir / "scripts" / "oacs_hook.py",
    }


def install(home: Path | None = None) -> dict[str, object]:
    paths = integration_paths(home)
    install_skills(paths["skill_dir"].parent, "Codex")

    agents_file = paths["agents_file"]
    agents_file.parent.mkdir(parents=True, exist_ok=True)
    existing_agents = agents_file.read_text(encoding="utf-8") if agents_file.exists() else ""
    agents_file.write_text(
        merge_marked_block(
            existing_agents,
            (ASSET_ROOT / "global_policy.md").read_text(),
            BLOCK_START,
            BLOCK_END,
        ),
        encoding="utf-8",
    )

    hooks_file = paths["hooks_file"]
    hooks_file.parent.mkdir(parents=True, exist_ok=True)
    hooks = _load_hooks(hooks_file)
    command = f'{sys.executable} "{paths["hook_script"]}"'
    _remove_oacs_hooks(hooks)
    _add_hook(hooks, "SessionStart", command, matcher="startup|resume|compact")
    _add_hook(hooks, "UserPromptSubmit", command)
    hooks_file.write_text(json.dumps(hooks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    ensure_global_storage()

    return status(home)


def status(home: Path | None = None) -> dict[str, object]:
    paths = integration_paths(home)
    agents_text = (
        paths["agents_file"].read_text(encoding="utf-8")
        if paths["agents_file"].exists()
        else ""
    )
    hooks = _load_hooks(paths["hooks_file"])
    project = resolve_project()
    return {
        "installed": (
            paths["skill_file"].is_file()
            and paths["proof_loop_skill_file"].is_file()
            and BLOCK_START in agents_text
            and _has_oacs_hooks(hooks)
        ),
        "skill": {
            "path": str(paths["skill_file"]),
            "installed": paths["skill_file"].is_file(),
            "managed": (paths["skill_dir"] / SKILL_MARKER).is_file(),
        },
        "proof_loop_skill": {
            "path": str(paths["proof_loop_skill_file"]),
            "installed": paths["proof_loop_skill_file"].is_file(),
            "managed": (paths["proof_loop_skill_dir"] / SKILL_MARKER).is_file(),
        },
        "agents": {
            "path": str(paths["agents_file"]),
            "installed": BLOCK_START in agents_text and BLOCK_END in agents_text,
        },
        "hooks": {
            "path": str(paths["hooks_file"]),
            "installed": _has_oacs_hooks(hooks),
            "trust": "review_required_in_codex_for_new_or_changed_hooks",
        },
        "cli": {"available": shutil.which("acs") is not None},
        "repository": {
            "detected": project is not None,
            "repository_id": project.repository_id if project else None,
            "project_db": str(project.db_path) if project else None,
            "project_storage_available": bool(project and project.db_path.exists()),
        },
        "global_storage": {
            "db": str(global_db_path()),
            "available": global_db_path().exists(),
        },
    }


def doctor(home: Path | None = None, query: str = "OACS Codex integration") -> dict[str, object]:
    snapshot = status(home)
    checks: list[dict[str, object]] = []
    for name, passed in (
        ("skill_discovered", bool(snapshot["skill"]["installed"])),  # type: ignore[index]
        (
            "proof_loop_skill_discovered",
            bool(snapshot["proof_loop_skill"]["installed"]),  # type: ignore[index]
        ),
        ("agents_contract", bool(snapshot["agents"]["installed"])),  # type: ignore[index]
        ("hooks_installed", bool(snapshot["hooks"]["installed"])),  # type: ignore[index]
        ("acs_cli_available", bool(snapshot["cli"]["available"])),  # type: ignore[index]
        ("repository_detected", bool(snapshot["repository"]["detected"])),  # type: ignore[index]
        (
            "project_storage",
            bool(snapshot["repository"]["project_storage_available"]),  # type: ignore[index]
        ),
        ("global_storage", bool(snapshot["global_storage"]["available"])),  # type: ignore[index]
    ):
        checks.append({"name": name, "status": "PASS" if passed else "FAIL"})

    context = build_codex_context(query=query, current_user_prompt=query)
    checks.extend(context_health_checks(context))
    overall = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    return {"status": overall, "checks": checks, "context": context, "installation": snapshot}


def uninstall(home: Path | None = None) -> dict[str, object]:
    paths = integration_paths(home)
    remove_skills(paths["skill_dir"].parent)
    if paths["agents_file"].exists():
        text = paths["agents_file"].read_text(encoding="utf-8")
        paths["agents_file"].write_text(
            remove_marked_block(text, BLOCK_START, BLOCK_END), encoding="utf-8"
        )
    if paths["hooks_file"].exists():
        hooks = _load_hooks(paths["hooks_file"])
        _remove_oacs_hooks(hooks)
        paths["hooks_file"].write_text(
            json.dumps(hooks, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    result = status(home)
    result["persistent_memory_preserved"] = True
    return result


def _load_hooks(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"description": "User lifecycle hooks.", "hooks": {}}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot merge invalid hooks file: {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"hooks file must contain a JSON object: {path}")
    parsed.setdefault("hooks", {})
    if not isinstance(parsed["hooks"], dict):
        raise ValueError(f"hooks field must contain a JSON object: {path}")
    return parsed


def _add_hook(
    payload: dict[str, Any], event: str, command: str, matcher: str | None = None
) -> None:
    group: dict[str, object] = {
        "hooks": [
            {
                "type": "command",
                "command": command,
                "timeout": 30,
                "additionalContextLimit": 4000,
                "statusMessage": "Restoring OACS context",
            }
        ]
    }
    if matcher:
        group["matcher"] = matcher
    payload["hooks"].setdefault(event, []).append(group)


def _remove_oacs_hooks(payload: dict[str, Any]) -> None:
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        return
    for event in ("SessionStart", "UserPromptSubmit", "PostCompact"):
        groups = hooks.get(event)
        if not isinstance(groups, list):
            continue
        retained = []
        for group in groups:
            handlers = group.get("hooks", []) if isinstance(group, dict) else []
            commands = [
                str(handler.get("command", ""))
                for handler in handlers
                if isinstance(handler, dict)
            ]
            if any("/oacs/scripts/oacs_hook.py" in command for command in commands):
                continue
            retained.append(group)
        if retained:
            hooks[event] = retained
        else:
            hooks.pop(event, None)


def _has_oacs_hooks(payload: dict[str, Any]) -> bool:
    hooks = payload.get("hooks")
    if not isinstance(hooks, dict):
        return False
    found: set[str] = set()
    for event in ("SessionStart", "UserPromptSubmit"):
        groups = hooks.get(event, [])
        for group in groups if isinstance(groups, list) else []:
            handlers = group.get("hooks", []) if isinstance(group, dict) else []
            if any(
                "/oacs/scripts/oacs_hook.py" in str(handler.get("command", ""))
                for handler in handlers
                if isinstance(handler, dict)
            ):
                found.add(event)
    return found == {"SessionStart", "UserPromptSubmit"}
