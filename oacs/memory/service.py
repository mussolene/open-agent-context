from __future__ import annotations

from typing import Any, cast

from cryptography.exceptions import InvalidTag

from oacs.core.errors import MemoryDecryptError, NotFound, ValidationFailure
from oacs.core.json import dumps, hash_json, loads
from oacs.core.time import now_iso
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes
from oacs.identity.policy import PolicyEngine
from oacs.memory.lifecycle import can_transition
from oacs.memory.models import EvidenceItem, MemoryContent, MemoryRecord
from oacs.memory.retrieval import HybridRetrievalProvider, RetrievalProvider, rank_memories
from oacs.storage.repositories import Repository


class MemoryService:
    def __init__(
        self,
        repo: Repository,
        policy: PolicyEngine,
        master_key: bytes,
        retrieval_provider: RetrievalProvider | None = None,
    ):
        self.repo = repo
        self.policy = policy
        self.master_key = master_key
        self.retrieval_provider = retrieval_provider or HybridRetrievalProvider()
        self.last_warnings: list[dict[str, object]] = []

    def observe(
        self, text: str, actor_id: str | None, scope: list[str] | None = None
    ) -> MemoryRecord:
        write_scope = scope or []
        self.policy.require(actor_id, "memory.observe", 0, write_scope, "default")
        return self._create("trace", 0, text, "observed", actor_id, write_scope)

    def propose(
        self,
        memory_type: str,
        depth: int,
        text: str,
        actor_id: str | None,
        scope: list[str] | None = None,
        evidence: list[EvidenceItem | dict[str, object]] | None = None,
    ) -> MemoryRecord:
        write_scope = scope or []
        self.policy.require(actor_id, "memory.propose", depth, write_scope, "default")
        return self._create(
            memory_type, depth, text, "candidate", actor_id, write_scope, evidence=evidence
        )

    def commit(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.commit", mem.depth, mem.scope, mem.namespace)
        if mem.depth >= 3 and not mem.evidence_refs:
            raise ValidationFailure("D3-D5 memory requires sharpening evidence before commit")
        return self._transition(mem, "active")

    def query(
        self,
        query: str,
        actor_id: str | None,
        scope: list[str] | None = None,
        strict: bool = False,
    ) -> list[MemoryRecord]:
        self.last_warnings = []
        requested_scope = scope or []
        self.policy.require(actor_id, "memory.query", scope=requested_scope, namespace="default")
        rows = self.repo.list(filters={"status": "active", "lifecycle_status": "active"})
        memories = []
        for row in rows:
            row_scope = row["scope"]
            row_namespace = str(row["namespace"])
            row_depth = int(str(row["depth"]))
            if requested_scope and not set(requested_scope).issubset(set(row_scope)):
                continue
            if not self.policy.allows(
                actor_id, "memory.read", row_depth, row_scope, row_namespace
            ):
                continue
            try:
                memories.append(self._decrypt(row))
            except MemoryDecryptError as exc:
                if strict:
                    raise
                self.last_warnings.append(
                    {"type": "UnreadableMemoryRecord", **exc.record}
                )
        return rank_memories(query, memories, provider=self.retrieval_provider)

    def read(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        row = self.repo.get(memory_id)
        if row["lifecycle_status"] == "forgotten":
            raise NotFound(f"memory is forgotten: {memory_id}")
        self.policy.require(
            actor_id,
            "memory.read",
            int(str(row["depth"])),
            row["scope"],
            str(row["namespace"]),
        )
        mem = self._decrypt(row)
        return mem

    def correct(self, memory_id: str, text: str, actor_id: str | None) -> MemoryRecord:
        old = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.correct", old.depth, old.scope, old.namespace)
        old = self._transition(old, "superseded")
        return self._create(old.memory_type, old.depth, text, "active", actor_id, old.scope, old.id)

    def deprecate(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.correct", mem.depth, mem.scope, mem.namespace)
        return self._transition(mem, "deprecated")

    def supersede(self, memory_id: str, replacement_id: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.correct", mem.depth, mem.scope, mem.namespace)
        mem.supersedes = replacement_id
        return self._transition(mem, "superseded")

    def forget(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.forget", mem.depth, mem.scope, mem.namespace)
        return self._transition(mem, "forgotten")

    def blur(self, memory_id: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.correct", mem.depth, mem.scope, mem.namespace)
        mem.depth = min(5, mem.depth + 1)
        mem.content.confidence = min(mem.content.confidence, 0.5)
        return self._save(mem)

    def sharpen(self, memory_id: str, evidence_ref: str, actor_id: str | None) -> MemoryRecord:
        mem = self.read(memory_id, actor_id)
        self.policy.require(actor_id, "memory.correct", mem.depth, mem.scope, mem.namespace)
        mem.depth = max(0, min(mem.depth, 2))
        if evidence_ref not in mem.evidence_refs:
            mem.evidence_refs.append(evidence_ref)
        mem.content.confidence = max(mem.content.confidence, 0.9)
        return self._save(mem)

    def export_all(self, actor_id: str | None) -> list[dict[str, object]]:
        self.policy.require(actor_id, "memory.export")
        return [m.model_dump() for m in self.query("", actor_id)]

    def decrypt_health(self, actor_id: str | None = None) -> dict[str, object]:
        self.policy.require(actor_id, "memory.query", scope=[], namespace="default")
        rows = self.repo.list(filters={"status": "active"})
        unreadable: list[dict[str, object]] = []
        checked = 0
        for row in rows:
            if row.get("lifecycle_status") == "forgotten":
                continue
            checked += 1
            try:
                self._decrypt(row)
            except MemoryDecryptError as exc:
                unreadable.append({"type": "UnreadableMemoryRecord", **exc.record})
        status = "PASS" if not unreadable else "FAIL"
        return {
            "status": status,
            "checked_records": checked,
            "unreadable_records": len(unreadable),
            "warnings": unreadable,
        }

    def quarantine(self, memory_id: str, actor_id: str | None = None) -> dict[str, object]:
        row = self.repo.get(memory_id)
        self.policy.require(
            actor_id,
            "memory.forget",
            int(str(row["depth"])),
            row["scope"],
            str(row["namespace"]),
        )
        row["status"] = "quarantined"
        row["updated_at"] = now_iso()
        self.repo.save(row)
        return {"id": memory_id, "status": "quarantined"}

    def unreadable_records(self, actor_id: str | None = None) -> list[dict[str, object]]:
        warnings = self.decrypt_health(actor_id)["warnings"]
        return warnings if isinstance(warnings, list) else []

    def purge_unreadable(
        self, actor_id: str | None = None, dry_run: bool = True
    ) -> dict[str, object]:
        records = self.unreadable_records(actor_id)
        ids = [str(item["record_id"]) for item in records]
        if not dry_run:
            for memory_id in ids:
                self.repo.delete(memory_id)
        return {
            "status": "dry_run" if dry_run else "purged",
            "count": len(ids),
            "record_ids": ids,
        }

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
        try:
            content = loads(
                decrypt_json_bytes(
                    self.master_key,
                    row["content_nonce"],  # type: ignore[arg-type]
                    row["content_ciphertext"],  # type: ignore[arg-type]
                    str(row["content_aad"]).encode("utf-8"),
                )
            )
        except (InvalidTag, ValueError, TypeError, KeyError) as exc:
            raise MemoryDecryptError("memory record is unreadable", _safe_row_error(row)) from exc
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


def _safe_row_error(row: dict[str, object]) -> dict[str, object]:
    return {
        "record_id": str(row.get("id", "")),
        "scope": row.get("scope", []),
        "namespace": str(row.get("namespace", "")),
        "memory_type": str(row.get("memory_type", "")),
        "created_at": row.get("created_at"),
    }
