from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from oacs.app import services
from oacs.core.config import global_db_path

ASSET_ROOT = Path(__file__).resolve().parent / "shared_assets"
SKILL_MARKER = ".managed-by-oacs"
SKILL_NAMES = ("oacs", "proof-loop")


def install_skills(skills_root: Path, client: str) -> dict[str, Path]:
    targets = {name: skills_root / name for name in SKILL_NAMES}
    for target in targets.values():
        if target.exists() and not (target / SKILL_MARKER).is_file():
            raise ValueError(f"refusing to replace unmanaged {client} Skill directory: {target}")
    for name, target in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ASSET_ROOT / name, target)
        (target / SKILL_MARKER).write_text(
            f"managed by acs integrations {client}\n", encoding="utf-8"
        )
    return targets


def remove_skills(skills_root: Path) -> None:
    for name in SKILL_NAMES:
        target = skills_root / name
        if (target / SKILL_MARKER).is_file():
            shutil.rmtree(target)


def skills_status(skills_root: Path) -> dict[str, dict[str, object]]:
    return {
        name: {
            "path": str(skills_root / name / "SKILL.md"),
            "installed": (skills_root / name / "SKILL.md").is_file(),
            "managed": (skills_root / name / SKILL_MARKER).is_file(),
        }
        for name in SKILL_NAMES
    }


def merge_marked_block(existing: str, block: str, start: str, end: str) -> str:
    without = remove_marked_block(existing, start, end).rstrip()
    managed = f"{start}\n{block.strip()}\n{end}"
    return f"{without}\n\n{managed}\n" if without else f"{managed}\n"


def remove_marked_block(text: str, start: str, end: str) -> str:
    start_at = text.find(start)
    end_at = text.find(end)
    if start_at == -1 or end_at == -1 or end_at < start_at:
        return text
    before = text[:start_at].rstrip()
    after = text[end_at + len(end) :].lstrip()
    joined = f"{before}\n\n{after}".strip()
    return f"{joined}\n" if joined else ""


def load_json_object(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"cannot merge invalid JSON file: {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return parsed


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_global_storage() -> Path:
    path = global_db_path()
    service = services(str(path), require_key=False)
    if not service.key_provider.status().available:
        metadata = service.key_provider.generate()
        service.store.set_metadata("encryption_mode", str(metadata["provider"]))
    return path


def context_health_checks(context: dict[str, object]) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for store_name in ("project", "global"):
        checks.append(
            {
                "name": f"{store_name}_context_access",
                "status": "PASS" if isinstance(context.get(store_name), dict) else "FAIL",
            }
        )

    prompt = str(context.get("prompt") or "")
    stores = [
        store
        for store_name in ("project", "global")
        if isinstance((store := context.get(store_name)), dict)
    ]
    selected = sum(int(store.get("memory_count", 0)) for store in stores)
    rendered_ok = "# OACS Agent Context" in prompt and (
        selected == 0
        or any(
            memory_id in prompt
            for store in stores
            for memory_id in store.get("memory_ids", [])
        )
    )
    checks.append(
        {
            "name": "rendered_context",
            "status": "PASS" if rendered_ok else "FAIL",
            "selected_memories": selected,
        }
    )

    warnings = context.get("warnings")
    warning_items = warnings if isinstance(warnings, list) else []
    for name, reason in (
        ("memory_readability", "UnreadableMemoryRecord"),
        ("project_memory_visibility", "shadowed_legacy_storage"),
    ):
        count = sum(
            1
            for item in warning_items
            if isinstance(item, dict) and item.get("reason") == reason
        )
        checks.append({"name": name, "status": "FAIL" if count else "PASS", "count": count})

    state = context.get("current_task_state")
    provenance = state.get("checkpoint_provenance") if isinstance(state, dict) else None
    checks.append(
        {
            "name": "latest_checkpoint",
            "status": "PASS" if isinstance(provenance, dict) else "FAIL",
            "available": bool(isinstance(provenance, dict) and provenance.get("id")),
        }
    )
    return checks
