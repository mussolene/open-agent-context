from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from oacs.skills.models import SkillManifest


def run_builtin_skill(name: str, payload: dict[str, object]) -> dict[str, object]:
    if name == "contradiction_resolver":
        return {"conflicts": [], "requires_sharpening": False}
    if name == "task_trace_distiller":
        return {"candidate_memory": str(payload.get("trace", ""))[:1000]}
    return {"result": payload}


def run_skill(skill: SkillManifest, payload: dict[str, object]) -> dict[str, object]:
    if skill.entrypoint.startswith("script:"):
        return _run_script_skill(skill, payload)
    return run_builtin_skill(skill.name, payload)


def _run_script_skill(skill: SkillManifest, payload: dict[str, object]) -> dict[str, object]:
    if not skill.source_path:
        raise ValueError(f"script skill has no source_path: {skill.name}")
    relative = skill.entrypoint.removeprefix("script:")
    script = (Path(skill.source_path) / relative).resolve()
    if not script.is_file():
        raise ValueError(f"script skill entrypoint not found: {script}")
    completed = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        timeout=int(str(payload.get("skill_timeout", 300))),
    )
    if completed.returncode != 0:
        raise RuntimeError(_script_error(script, completed.stderr))
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"script skill returned invalid JSON: {script}") from exc
    if not isinstance(result, dict):
        raise RuntimeError(f"script skill must return a JSON object: {script}")
    return result


def _script_error(script: Path, stderr: str) -> str:
    tail = stderr[-1000:] if stderr else "no stderr"
    return f"script skill failed: {script}: {tail}"
