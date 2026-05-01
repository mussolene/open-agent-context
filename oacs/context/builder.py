from __future__ import annotations

from oacs.context.capsule import ContextCapsule, ContextCapsuleExport
from oacs.core.errors import NotFound
from oacs.core.json import dumps, hash_json, loads
from oacs.core.time import now_iso
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes
from oacs.identity.policy import PolicyEngine
from oacs.memory.service import MemoryService
from oacs.rules.engine import RuleEngine
from oacs.skills.registry import SkillRegistry
from oacs.storage.repositories import Repository
from oacs.tools.registry import ToolRegistry


class ContextBuilder:
    def __init__(
        self,
        repo: Repository,
        memory: MemoryService,
        rules: RuleEngine,
        skills: SkillRegistry,
        tools: ToolRegistry,
        policy: PolicyEngine,
        master_key: bytes,
    ):
        self.repo = repo
        self.memory = memory
        self.rules = rules
        self.skills = skills
        self.tools = tools
        self.policy = policy
        self.master_key = master_key

    def build(
        self,
        intent: str,
        actor_id: str | None,
        agent_id: str | None = None,
        scope: list[str] | None = None,
        token_budget: int = 4000,
        task_id: str | None = None,
    ) -> ContextCapsule:
        requested_scope = scope or []
        self.policy.require(actor_id, "context.build", scope=requested_scope, namespace="default")
        memories = self.memory.query(intent, actor_id, requested_scope)
        rules = self.rules.check("context.build", {"memories": [m.model_dump() for m in memories]})
        skills = [
            skill
            for skill in self.skills.list()
            if self.policy.allows(
                actor_id,
                "skill.run",
                scope=skill.scope or requested_scope,
                namespace=skill.namespace,
                skill=skill.id,
            )
            or self.policy.allows(
                actor_id,
                "skill.run",
                scope=skill.scope or requested_scope,
                namespace=skill.namespace,
                skill=skill.name,
            )
        ]
        tools = [
            tool
            for tool in self.tools.list()
            if self.policy.allows(
                actor_id,
                "tool.call",
                scope=tool.scope or requested_scope,
                namespace=tool.namespace,
                tool=tool.id,
            )
            or self.policy.allows(
                actor_id,
                "tool.call",
                scope=tool.scope or requested_scope,
                namespace=tool.namespace,
                tool=tool.name,
            )
        ]
        capsule = ContextCapsule(
            purpose=intent,
            task_id=task_id,
            actor_id=actor_id,
            agent_id=agent_id,
            scope=requested_scope,
            token_budget=token_budget,
            included_memories=[m.id for m in memories],
            included_rules=[r.rule_id for r in rules],
            included_skills=[s.id for s in skills[:4]],
            included_tools=[t.id for t in tools],
            evidence_refs=sorted({ref for m in memories for ref in m.evidence_refs}),
            forbidden_assumptions=["D3-D5 memory is not factual evidence"],
            permissions={
                "memory.query": True,
                "memory.commit": False,
                "tool.execute.read": True,
                "tool.execute.write": False,
            },
        ).seal()
        self._save(capsule)
        return capsule

    def read(self, capsule_id: str, actor_id: str | None) -> ContextCapsule:
        self.policy.require(actor_id, "context.export")
        row = self.repo.get(capsule_id)
        payload = loads(
            decrypt_json_bytes(
                self.master_key,
                row["payload_nonce"],
                row["payload_ciphertext"],
                str(row["payload_aad"]).encode("utf-8"),
            )
        )
        return ContextCapsule(**payload)

    def export_capsule(self, capsule_id: str, actor_id: str | None) -> ContextCapsuleExport:
        capsule = self.read(capsule_id, actor_id)
        return ContextCapsuleExport.create(capsule, self.master_key)

    def explain(self, capsule_id: str, actor_id: str | None) -> dict[str, object]:
        capsule = self.read(capsule_id, actor_id)
        return {
            "capsule_id": capsule.id,
            "purpose": capsule.purpose,
            "included_memories": capsule.included_memories,
            "included_rules": capsule.included_rules,
            "included_skills": capsule.included_skills,
            "included_tools": capsule.included_tools,
            "forbidden_assumptions": capsule.forbidden_assumptions,
        }

    def import_capsule(self, payload: dict[str, object], actor_id: str | None) -> ContextCapsule:
        self.policy.require(actor_id, "context.export")
        if payload.get("export_type") == "context_capsule_export":
            export = ContextCapsuleExport.model_validate(payload)
            export.validate_integrity(self.master_key)
            capsule = export.capsule
        else:
            capsule = ContextCapsule.model_validate(payload)
            capsule.validate_checksum()
        self._save(capsule)
        return capsule

    def validate_payload(self, payload: dict[str, object]) -> dict[str, object]:
        if payload.get("export_type") == "context_capsule_export":
            export = ContextCapsuleExport.model_validate(payload)
            export.validate_integrity(self.master_key)
            return {
                "valid": True,
                "id": export.capsule.id,
                "version": export.version,
                "export_type": export.export_type,
                "integrity": export.integrity.model_dump(),
            }
        capsule = ContextCapsule.model_validate(payload)
        capsule.validate_checksum()
        return {
            "valid": True,
            "id": capsule.id,
            "version": capsule.version,
            "export_type": "context_capsule",
        }

    def set_status(self, capsule_id: str, actor_id: str | None, status: str) -> dict[str, object]:
        self.policy.require(actor_id, "context.export")
        row = self.repo.get(capsule_id)
        if not row:
            raise NotFound(f"context capsule not found: {capsule_id}")
        row["status"] = status
        row["updated_at"] = now_iso()
        self.repo.save(row)
        return {"id": capsule_id, "status": status}

    def _save(self, capsule: ContextCapsule) -> None:
        payload = capsule.model_dump()
        aad = f"context:{capsule.id}".encode()
        nonce, ciphertext = encrypt_json_bytes(self.master_key, dumps(payload).encode("utf-8"), aad)
        now = now_iso()
        self.repo.save(
            {
                "id": capsule.id,
                "purpose": capsule.purpose,
                "task_id": capsule.task_id,
                "actor_id": capsule.actor_id,
                "agent_id": capsule.agent_id,
                "scope": capsule.scope,
                "token_budget": capsule.token_budget,
                "payload_ciphertext": ciphertext,
                "payload_nonce": nonce,
                "payload_aad": aad.decode("utf-8"),
                "checksum": capsule.checksum,
                "status": "active",
                "namespace": "default",
                "owner_actor_id": capsule.actor_id,
                "created_at": now,
                "updated_at": now,
                "content_hash": hash_json(payload),
            }
        )
