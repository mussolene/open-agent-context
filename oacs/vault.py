from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from oacs.core.errors import NotFound, ValidationFailure
from oacs.core.ids import new_id
from oacs.core.json import dumps, hash_json, loads
from oacs.core.time import now_iso
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes
from oacs.identity.policy import PolicyEngine
from oacs.storage.repositories import Repository

ProtectedType = Literal["secret", "sensitive_fact"]


class ProtectedRef(BaseModel):
    id: str
    protected_type: ProtectedType
    label: str
    sensitivity: str = "restricted"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    projection: str = "ref_only"
    status: str = "active"


class ProtectedValueRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("sec"))
    protected_type: ProtectedType = "secret"
    value_kind: str
    label: str
    sensitivity: str = "restricted"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None
    key_ref: str = "local-master-key"
    metadata: dict[str, object] = Field(default_factory=dict)
    content_hash: str = ""
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    rotated_at: str | None = None
    expires_at: str | None = None
    status: str = "active"

    def protected_ref(self) -> ProtectedRef:
        return ProtectedRef(
            id=self.id,
            protected_type=self.protected_type,
            label=self.label,
            sensitivity=self.sensitivity,
            namespace=self.namespace,
            scope=self.scope,
            status=self.status,
        )


class VaultService:
    def __init__(
        self,
        repo: Repository,
        policy: PolicyEngine,
        master_key: bytes,
    ):
        self.repo = repo
        self.policy = policy
        self.master_key = master_key

    def put(
        self,
        value: str,
        value_kind: str,
        label: str,
        actor_id: str | None,
        scope: list[str] | None = None,
        namespace: str = "default",
        protected_type: ProtectedType = "secret",
        sensitivity: str = "restricted",
        metadata: dict[str, object] | None = None,
        expires_at: str | None = None,
    ) -> ProtectedValueRecord:
        write_scope = scope or []
        operation = "secret.create" if protected_type == "secret" else "protected.create"
        self.policy.require(actor_id, operation, scope=write_scope, namespace=namespace)
        record = ProtectedValueRecord(
            protected_type=protected_type,
            value_kind=value_kind,
            label=label,
            sensitivity=sensitivity,
            namespace=namespace,
            scope=write_scope,
            owner_actor_id=actor_id,
            metadata=metadata or {},
            expires_at=expires_at,
        )
        return self._save(record, value)

    def list_refs(
        self,
        actor_id: str | None,
        scope: list[str] | None = None,
        namespace: str | None = None,
    ) -> list[ProtectedRef]:
        requested_scope = scope or []
        self.policy.require(actor_id, "protected.list", scope=requested_scope, namespace=namespace)
        refs: list[ProtectedRef] = []
        for row in self.repo.list(filters={"status": "active"}):
            record = self._record_from_row(row)
            if namespace is not None and record.namespace != namespace:
                continue
            if requested_scope and not set(requested_scope).issubset(set(record.scope)):
                continue
            if self.policy.allows(
                actor_id, "protected.use", scope=record.scope, namespace=record.namespace
            ):
                refs.append(record.protected_ref())
        return refs

    def use(
        self,
        protected_id: str,
        actor_id: str | None,
        reveal: bool = False,
    ) -> dict[str, object]:
        row = self.repo.get(protected_id)
        record = self._record_from_row(row)
        if record.status != "active":
            raise NotFound(f"protected value is not active: {protected_id}")
        if record.expires_at and record.expires_at <= now_iso():
            raise ValidationFailure(f"protected value is expired: {protected_id}")
        self.policy.require(
            actor_id,
            "protected.use",
            scope=record.scope,
            namespace=record.namespace,
        )
        output: dict[str, object] = {
            "protected_ref": record.protected_ref().model_dump(),
            "revealed": False,
            "value": None,
        }
        if reveal:
            read_operation = (
                "secret.read" if record.protected_type == "secret" else "protected.read"
            )
            self.policy.require(
                actor_id,
                read_operation,
                scope=record.scope,
                namespace=record.namespace,
            )
            output["revealed"] = True
            output["value"] = self._decrypt(row)
        return output

    def revoke(self, protected_id: str, actor_id: str | None) -> ProtectedValueRecord:
        row = self.repo.get(protected_id)
        record = self._record_from_row(row)
        operation = "secret.revoke" if record.protected_type == "secret" else "protected.revoke"
        self.policy.require(actor_id, operation, scope=record.scope, namespace=record.namespace)
        row["status"] = "revoked"
        row["updated_at"] = now_iso()
        self.repo.save(row)
        return self._record_from_row(row)

    def _save(self, record: ProtectedValueRecord, value: str) -> ProtectedValueRecord:
        record.updated_at = now_iso()
        aad = f"protected:{record.id}".encode()
        plaintext = dumps({"value": value}).encode("utf-8")
        nonce, ciphertext = encrypt_json_bytes(self.master_key, plaintext, aad)
        public_payload = record.model_dump()
        record.content_hash = hash_json(
            {
                key: value
                for key, value in public_payload.items()
                if key not in {"content_hash", "created_at", "updated_at"}
            }
        )
        self.repo.save(
            {
                "id": record.id,
                "protected_type": record.protected_type,
                "value_kind": record.value_kind,
                "label": record.label,
                "sensitivity": record.sensitivity,
                "namespace": record.namespace,
                "scope": record.scope,
                "owner_actor_id": record.owner_actor_id,
                "key_ref": record.key_ref,
                "metadata": record.metadata,
                "value_ciphertext": ciphertext,
                "value_nonce": nonce,
                "value_aad": aad.decode("utf-8"),
                "content_hash": record.content_hash,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
                "rotated_at": record.rotated_at,
                "expires_at": record.expires_at,
                "status": record.status,
            }
        )
        return record

    def _decrypt(self, row: dict[str, Any]) -> str:
        payload = loads(
            decrypt_json_bytes(
                self.master_key,
                row["value_nonce"],
                row["value_ciphertext"],
                str(row["value_aad"]).encode("utf-8"),
            )
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("value"), str):
            raise ValidationFailure("invalid protected value payload")
        return str(payload["value"])

    @staticmethod
    def _record_from_row(row: dict[str, Any]) -> ProtectedValueRecord:
        return ProtectedValueRecord(
            id=str(row["id"]),
            protected_type=row["protected_type"],
            value_kind=str(row["value_kind"]),
            label=str(row["label"]),
            sensitivity=str(row["sensitivity"]),
            namespace=str(row["namespace"]),
            scope=row["scope"],
            owner_actor_id=row["owner_actor_id"],
            key_ref=str(row["key_ref"]),
            metadata=row["metadata"],
            content_hash=str(row["content_hash"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            rotated_at=row["rotated_at"],
            expires_at=row["expires_at"],
            status=str(row["status"]),
        )
