from __future__ import annotations

import hmac
from hashlib import sha256

from pydantic import BaseModel, Field, model_validator

from oacs.core.errors import ValidationFailure
from oacs.core.ids import new_id
from oacs.core.json import dumps, hash_json
from oacs.core.time import now_iso


class ContextCapsule(BaseModel):
    id: str = Field(default_factory=lambda: new_id("ctx"))
    version: str = "0.1"
    capsule_type: str = "context_capsule"
    purpose: str
    task_id: str | None = None
    actor_id: str | None = None
    agent_id: str | None = None
    scope: list[str] = Field(default_factory=list)
    token_budget: int = 4000
    included_memories: list[str] = Field(default_factory=list)
    included_rules: list[str] = Field(default_factory=list)
    included_skills: list[str] = Field(default_factory=list)
    included_tools: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    forbidden_assumptions: list[str] = Field(default_factory=list)
    permissions: dict[str, bool] = Field(default_factory=dict)
    expires_at: str | None = None
    audit_refs: list[str] = Field(default_factory=list)
    checksum: str = ""

    def seal(self) -> ContextCapsule:
        data = self.model_dump()
        data.pop("checksum", None)
        self.checksum = hash_json(data)
        return self

    def validate_checksum(self) -> None:
        expected = self.model_copy(deep=True)
        provided = expected.checksum
        expected.checksum = ""
        expected.seal()
        if provided != expected.checksum:
            raise ValidationFailure("context capsule checksum mismatch")
        if self.version != "0.1" or self.capsule_type != "context_capsule":
            raise ValidationFailure("unsupported context capsule version or type")


class CapsuleIntegrity(BaseModel):
    schema_version: str = "0.1"
    algorithm: str = "HMAC-SHA256"
    payload_checksum: str
    mac: str | None = None
    signature: str | None = None
    signed_at: str = Field(default_factory=now_iso)
    key_ref: str = "local-master-key"

    @model_validator(mode="after")
    def sync_deprecated_signature_alias(self) -> CapsuleIntegrity:
        if self.mac is None and self.signature is not None:
            self.mac = self.signature
        if self.signature is None and self.mac is not None:
            self.signature = self.mac
        if self.mac is None:
            raise ValidationFailure("context capsule export integrity mac is required")
        return self


class ContextCapsuleExport(BaseModel):
    export_type: str = "context_capsule_export"
    version: str = "0.1"
    capsule: ContextCapsule
    integrity: CapsuleIntegrity

    @classmethod
    def create(cls, capsule: ContextCapsule, signing_key: bytes) -> ContextCapsuleExport:
        capsule.validate_checksum()
        payload = capsule.model_dump()
        payload_checksum = hash_json(payload)
        mac = mac_capsule_payload(payload, signing_key)
        return cls(
            capsule=capsule,
            integrity=CapsuleIntegrity(
                payload_checksum=payload_checksum,
                mac=mac,
                signature=mac,
            ),
        )

    def validate_integrity(self, signing_key: bytes) -> None:
        if self.export_type != "context_capsule_export" or self.version != "0.1":
            raise ValidationFailure("unsupported context capsule export version or type")
        self.capsule.validate_checksum()
        payload = self.capsule.model_dump()
        if self.integrity.payload_checksum != hash_json(payload):
            raise ValidationFailure("context capsule export payload checksum mismatch")
        if self.integrity.algorithm != "HMAC-SHA256":
            raise ValidationFailure("unsupported context capsule export integrity algorithm")
        expected = mac_capsule_payload(payload, signing_key)
        if not hmac.compare_digest(self.integrity.mac or "", expected):
            raise ValidationFailure("context capsule export mac mismatch")


def mac_capsule_payload(payload: dict[str, object], signing_key: bytes) -> str:
    return hmac.new(signing_key, dumps(payload).encode("utf-8"), sha256).hexdigest()


def sign_capsule_payload(payload: dict[str, object], signing_key: bytes) -> str:
    return mac_capsule_payload(payload, signing_key)
