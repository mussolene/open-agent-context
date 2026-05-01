from __future__ import annotations

from pydantic import BaseModel, Field

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository


class CapabilityDefinition(BaseModel):
    id: str = Field(default_factory=lambda: new_id("capdef"))
    name: str
    operation: str
    description: str
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    owner_actor_id: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    content_hash: str = ""

    def to_record(self) -> dict[str, object]:
        definition = self.model_dump()
        definition["content_hash"] = hash_json(
            {k: v for k, v in definition.items() if k != "content_hash"}
        )
        return {
            "id": self.id,
            "name": self.name,
            "operation": self.operation,
            "description": self.description,
            "definition": definition,
            "status": self.status,
            "namespace": self.namespace,
            "scope": self.scope,
            "owner_actor_id": self.owner_actor_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "content_hash": definition["content_hash"],
        }


class CapabilityGrant(BaseModel):
    id: str = Field(default_factory=lambda: new_id("cap"))
    subject_actor_id: str
    issuer_actor_id: str
    scope: list[str] = Field(default_factory=list)
    allowed_operations: list[str] = Field(default_factory=list)
    denied_operations: list[str] = Field(default_factory=list)
    memory_depth_allowed: int = 2
    namespaces_allowed: list[str] = Field(default_factory=lambda: ["default"])
    tools_allowed: list[str] = Field(default_factory=list)
    skills_allowed: list[str] = Field(default_factory=list)
    expires_at: str | None = None
    signature: str | None = None
    status: str = "active"
    namespace: str = "default"
    owner_actor_id: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    content_hash: str = ""

    def to_record(self) -> dict[str, object]:
        data = self.model_dump()
        data["content_hash"] = hash_json({k: v for k, v in data.items() if k != "content_hash"})
        return data


class CapabilityService:
    def __init__(self, repo: Repository, definitions_repo: Repository | None = None):
        self.repo = repo
        self.definitions_repo = definitions_repo

    def grant(
        self,
        subject_actor_id: str,
        issuer_actor_id: str,
        allowed_operations: list[str],
        scope: list[str] | None = None,
        memory_depth_allowed: int = 2,
        namespaces_allowed: list[str] | None = None,
        denied_operations: list[str] | None = None,
        expires_at: str | None = None,
    ) -> CapabilityGrant:
        grant = CapabilityGrant(
            subject_actor_id=subject_actor_id,
            issuer_actor_id=issuer_actor_id,
            allowed_operations=allowed_operations,
            denied_operations=denied_operations or [],
            scope=scope if scope is not None else ["*"],
            memory_depth_allowed=memory_depth_allowed,
            namespaces_allowed=namespaces_allowed or ["default"],
            expires_at=expires_at,
        )
        self.repo.save(grant.to_record())
        return grant

    def grant_shared_memory(
        self,
        subject_actor_id: str,
        issuer_actor_id: str,
        scope: list[str],
        memory_depth_allowed: int = 2,
        namespaces_allowed: list[str] | None = None,
        expires_at: str | None = None,
        allowed_operations: list[str] | None = None,
    ) -> CapabilityGrant:
        return self.grant(
            subject_actor_id=subject_actor_id,
            issuer_actor_id=issuer_actor_id,
            allowed_operations=allowed_operations
            or [
                "memory.observe",
                "memory.propose",
                "memory.query",
                "memory.read",
                "context.build",
                "context.export",
            ],
            scope=scope,
            memory_depth_allowed=memory_depth_allowed,
            namespaces_allowed=namespaces_allowed or ["default"],
            expires_at=expires_at,
        )

    def for_actor(self, actor_id: str) -> list[CapabilityGrant]:
        rows = self.repo.list(filters={"subject_actor_id": actor_id, "status": "active"})
        return [CapabilityGrant(**row) for row in rows]

    def ensure_builtin_definitions(self) -> None:
        if self.definitions_repo is None:
            return
        existing = {row["id"] for row in self.definitions_repo.list()}
        for definition in builtin_capabilities():
            if definition.id not in existing:
                self.definitions_repo.save(definition.to_record())

    def list_definitions(self) -> list[CapabilityDefinition]:
        self.ensure_builtin_definitions()
        if self.definitions_repo is None:
            return builtin_capabilities()
        return [
            CapabilityDefinition(**row["definition"])
            for row in self.definitions_repo.list(
                filters={"status": "active"}, order_by=[("operation", "asc")]
            )
        ]

    def inspect_definition(self, capability_id: str) -> CapabilityDefinition:
        for definition in self.list_definitions():
            if definition.id == capability_id or definition.name == capability_id:
                return definition
        raise KeyError(f"capability definition not found: {capability_id}")


def builtin_capabilities() -> list[CapabilityDefinition]:
    return [
        CapabilityDefinition(
            id="cap_memory_observe",
            name="memory_observe",
            operation="memory.observe",
            description="Allows writing raw trace observations into granted memory scopes.",
        ),
        CapabilityDefinition(
            id="cap_memory_propose",
            name="memory_propose",
            operation="memory.propose",
            description="Allows proposing candidate memory inside granted scopes.",
        ),
        CapabilityDefinition(
            id="cap_memory_commit",
            name="memory_commit",
            operation="memory.commit",
            description="Allows committing candidate memory inside granted scopes.",
        ),
        CapabilityDefinition(
            id="cap_memory_query",
            name="memory_query",
            operation="memory.query",
            description="Allows querying active memory inside granted scopes.",
        ),
        CapabilityDefinition(
            id="cap_memory_read",
            name="memory_read",
            operation="memory.read",
            description="Allows reading confirmed memory up to the granted depth.",
        ),
        CapabilityDefinition(
            id="cap_memory_correct",
            name="memory_correct",
            operation="memory.correct",
            description="Allows correcting, blurring, sharpening, or deprecating granted memory.",
        ),
        CapabilityDefinition(
            id="cap_memory_forget",
            name="memory_forget",
            operation="memory.forget",
            description="Allows forgetting memory inside granted scopes.",
        ),
        CapabilityDefinition(
            id="cap_context_build",
            name="context_build",
            operation="context.build",
            description="Allows building context capsules from allowed memory and registries.",
        ),
        CapabilityDefinition(
            id="cap_context_export",
            name="context_export",
            operation="context.export",
            description="Allows exporting a context capsule after policy checks.",
        ),
        CapabilityDefinition(
            id="cap_shared_memory",
            name="shared_memory",
            operation="memory.query,memory.read,context.build,context.export",
            description="Allows scoped subagent memory and context access.",
        ),
    ]
