from __future__ import annotations

import json


def test_builtin_skills_and_scan(svc, tmp_path):
    assert any(s.name == "memory_critical_solver" for s in svc.skills.list())
    folder = tmp_path / ".skills" / "demo"
    folder.mkdir(parents=True)
    (folder / "skill.json").write_text(
        json.dumps({"name": "demo", "version": "0.1", "entrypoint": "builtin"})
    )
    scanned = svc.skills.scan(str(tmp_path / ".skills"))
    assert scanned[0].name == "demo"
