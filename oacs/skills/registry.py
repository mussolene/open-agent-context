from __future__ import annotations

import json
from pathlib import Path

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.skills.models import SkillManifest
from oacs.storage.repositories import Repository


def builtin_skills() -> list[SkillManifest]:
    return [
        SkillManifest(id="skill_memory_critical_solver", name="memory_critical_solver"),
        SkillManifest(id="skill_contradiction_resolver", name="contradiction_resolver"),
        SkillManifest(id="skill_task_trace_distiller", name="task_trace_distiller"),
    ]


class SkillRegistry:
    def __init__(self, repo: Repository):
        self.repo = repo

    def ensure_builtin(self) -> None:
        existing = {row["id"] for row in self.repo.list()}
        for skill in builtin_skills():
            if skill.id not in existing:
                self.add(skill)

    def add(self, skill: SkillManifest) -> SkillManifest:
        now = now_iso()
        manifest = skill.model_dump()
        self.repo.save(
            {
                "id": skill.id or new_id("skill"),
                "name": skill.name,
                "version": skill.version,
                "manifest": manifest,
                "status": skill.status,
                "namespace": skill.namespace,
                "scope": skill.scope,
                "owner_actor_id": skill.owner_actor_id,
                "created_at": now,
                "updated_at": now,
                "content_hash": hash_json(manifest),
            }
        )
        return skill

    def scan(self, folder: str) -> list[SkillManifest]:
        found: list[SkillManifest] = []
        base = Path(folder)
        for manifest_file in base.glob("*/skill.json"):
            payload = json.loads(manifest_file.read_text())
            payload.setdefault("source_path", str(manifest_file.parent))
            found.append(self.add(SkillManifest(**payload)))
        return found

    def list(self) -> list[SkillManifest]:
        self.ensure_builtin()
        return [
            SkillManifest(**row["manifest"])
            for row in self.repo.list(filters={"status": "active"})
        ]

    def inspect(self, skill_id: str) -> SkillManifest:
        for skill in self.list():
            if skill.id == skill_id or skill.name == skill_id:
                return skill
        raise KeyError(f"skill not found: {skill_id}")

    def activate(self, skill_id: str) -> SkillManifest:
        row_matches = [
            row for row in self.repo.list() if row["id"] == skill_id or row["name"] == skill_id
        ]
        if not row_matches:
            raise KeyError(f"skill not found: {skill_id}")
        row = row_matches[0]
        row["status"] = "active"
        manifest = dict(row["manifest"])
        manifest["status"] = "active"
        row["manifest"] = manifest
        row["updated_at"] = now_iso()
        self.repo.save(row)
        return SkillManifest(**manifest)
