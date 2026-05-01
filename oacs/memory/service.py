from __future__ import annotations

from typing import Any, cast

from oacs.core.errors import NotFound, ValidationFailure
from oacs.core.json import dumps, hash_json, loads
from oacs.core.time import now_iso
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes
from oacs.identity.policy import PolicyEngine
from oacs.memory.lifecycle import can_transition
from oacs.memory.models import EvidenceItem, MemoryContent, MemoryRecord
from oacs.memory.search import rank_memories
from oacs.storage.repositories import Repository


class MemoryService:
    def __init__(self, repo: Repository, policy: PolicyEngine, master_key: bytes):
        self.repo = repo
        self.policy = policy
        self.master_key = master_key

    def observe(
        self, text: str, actor_id: str | None, scope: list[str] | None = None
    ) -> MemoryRecord:
        self.policy.require(actor_id, "memory.observe", 0)
        return self._create("trace", 0, text, "observed", actor_id, scope or [])

    def propose(
        self,
        memory_type: str,
        depth: int,
        text: str,
        actor_id: str | None,
        scope: list[str] | None = None,
        evidence: list[EvidenceItem | dict[str, object]] | None = None,
    ) -> MemoryRecord:
        self.policy.require(actor_id, "memory.propose", depth)
        return self._create(
            memory_type, depth, text, "candidate", actor_id, scope or [], evidence=evidence
        )

    def commit(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.commit")
        mem = self.read(memory_id, actor_id)
        if mem.depth >= 3 and not mem.evidence_refs:
            raise ValidationFailure("D3-D5 memory requires sharpening evidence before commit")
        return self._transition(mem, "active")

    def query(
        self, query: str, actor_id: str | None, scope: list[str] | None = None
    ) -> list[MemoryRecord]:
        self.policy.require(actor_id, "memory.query")
        memories = [
            self._decrypt(row)
            for row in self.repo.list("WHERE status='active' AND lifecycle_status='active'")
        ]
        if scope:
            memories = [m for m in memories if set(scope) & set(m.scope)]
        return rank_memories(query, memories)

    def read(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        row = self.repo.get(memory_id)
        if row["lifecycle_status"] == "forgotten":
            raise NotFound(f"memory is forgotten: {memory_id}")
        mem = self._decrypt(row)
        self.policy.require(actor_id, "memory.read", mem.depth)
        return mem

    def correct(self, memory_id: str, text: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.correct")
        old = self.read(memory_id, actor_id)
        old = self._transition(old, "superseded")
        return self._create(old.memory_type, old.depth, text, "active", actor_id, old.scope, old.id)

    def deprecate(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.correct")
        return self._transition(self.read(memory_id, actor_id), "deprecated")

    def supersede(self, memory_id: str, replacement_id: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.correct")
        mem = self.read(memory_id, actor_id)
        mem.supersedes = replacement_id
        return self._transition(mem, "superseded")

    def forget(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.forget")
        return self._transition(self.read(memory_id, actor_id), "forgotten")

    def blur(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.correct")
        mem = self.read(memory_id, actor_id)
        mem.depth = min(5, mem.depth + 1)
        mem.content.confidence = min(mem.content.confidence, 0.5)
        return self._save(mem)

    def sharpen(self, memory_id: str, evidence_ref: str, actor_id: str | None) -> MemoryRecord:
        self.policy.require(actor_id, "memory.correct")
        mem = self.read(memory_id, actor_id)
        mem.depth = max(0, min(mem.depth, 2))
        if evidence_ref not in mem.evidence_refs:
            mem.evidence_refs.append(evidence_ref)
        mem.content.confidence = max(mem.content.confidence, 0.9)
        return self._save(mem)

    def export_all(self, actor_id: str | None) -> list[dict[str, object]]:
        self.policy.require(actor_id, "memory.export")
        return [m.model_dump() for m in self.query("", actor_id)]

    def _create(
        self,
        memory_type: str,
        depth: int,
        text: str,
        lifecycle_status: str,
        actor_id: str | None,
        scope: list[str],
        supersedes: str | None = None,
        evidence: list[EvidenceItem | dict[str, object]] | None = None,
    ) -> MemoryRecord:
        structured_evidence = [
            item if isinstance(item, EvidenceItem) else EvidenceItem(**cast(dict[str, Any], item))
            for item in (evidence or [])
        ]
        mem = MemoryRecord(
            memory_type=memory_type,
            depth=depth,
            lifecycle_status=lifecycle_status,  # type: ignore[arg-type]
            scope=scope,
            owner_actor_id=actor_id,
            content=MemoryContent(text=text, kind=memory_type, evidence=structured_evidence),
            supersedes=supersedes,
        )
        return self._save(mem)

    def _transition(self, mem: MemoryRecord, lifecycle_status: str) -> MemoryRecord:
        if not can_transition(mem.lifecycle_status, lifecycle_status):
            raise ValidationFailure(
                f"invalid memory transition {mem.lifecycle_status}->{lifecycle_status}"
            )
        mem.lifecycle_status = lifecycle_status  # type: ignore[assignment]
        return self._save(mem)

    def _save(self, mem: MemoryRecord) -> MemoryRecord:
        mem.updated_at = now_iso()
        content = mem.content.model_dump()
        mem.content_hash = hash_json(content)
        aad = f"memory:{mem.id}".encode()
        nonce, ciphertext = encrypt_json_bytes(self.master_key, dumps(content).encode("utf-8"), aad)
        self.repo.save(
            {
                "id": mem.id,
                "memory_type": mem.memory_type,
                "depth": mem.depth,
                "lifecycle_status": mem.lifecycle_status,
                "status": mem.status,
                "namespace": mem.namespace,
                "scope": mem.scope,
                "owner_actor_id": mem.owner_actor_id,
                "content_ciphertext": ciphertext,
                "content_nonce": nonce,
                "content_aad": aad.decode("utf-8"),
                "content_hash": mem.content_hash,
                "evidence_refs": mem.evidence_refs,
                "supersedes": mem.supersedes,
                "created_at": mem.created_at,
                "updated_at": mem.updated_at,
            }
        )
        return mem

    def _decrypt(self, row: dict[str, object]) -> MemoryRecord:
        content = loads(
            decrypt_json_bytes(
                self.master_key,
                row["content_nonce"],  # type: ignore[arg-type]
                row["content_ciphertext"],  # type: ignore[arg-type]
                str(row["content_aad"]).encode("utf-8"),
            )
        )
        return MemoryRecord(
            id=str(row["id"]),
            memory_type=str(row["memory_type"]),
            depth=int(str(row["depth"])),
            lifecycle_status=str(row["lifecycle_status"]),  # type: ignore[arg-type]
            status=str(row["status"]),
            namespace=str(row["namespace"]),
            scope=row["scope"],  # type: ignore[arg-type]
            owner_actor_id=row["owner_actor_id"],  # type: ignore[arg-type]
            content=MemoryContent(**content),
            evidence_refs=row["evidence_refs"],  # type: ignore[arg-type]
            supersedes=row["supersedes"],  # type: ignore[arg-type]
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            content_hash=str(row["content_hash"]),
        )
