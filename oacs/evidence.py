from __future__ import annotations

from oacs.audit import AuditService
from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.identity.policy import PolicyEngine
from oacs.storage.repositories import Repository
from oacs.tools.models import ToolCallResult


class EvidenceService:
    def __init__(self, repo: Repository, policy: PolicyEngine, audit: AuditService):
        self.repo = repo
        self.policy = policy
        self.audit = audit

    def get(self, evidence_ref: str) -> dict[str, object]:
        return self.repo.get(evidence_ref)

    def list_refs(
        self,
        *,
        kind: str | None = None,
        namespace: str | None = None,
        limit: int | None = 50,
    ) -> list[dict[str, object]]:
        filters: dict[str, object] = {}
        if kind:
            filters["kind"] = kind
        if namespace:
            filters["namespace"] = namespace
        return self.repo.list(
            filters=filters or None,
            order_by=[("created_at", "desc"), ("id", "desc")],
            limit=limit,
        )

    def ingest_tool_result(
        self,
        *,
        tool_id: str,
        tool_name: str | None = None,
        tool_type: str = "external",
        output: dict[str, object],
        input_payload: dict[str, object] | None = None,
        actor_id: str | None = None,
        scope: list[str] | None = None,
        namespace: str = "default",
        source_uri: str | None = None,
        status: str = "completed",
        executed: bool = True,
    ) -> ToolCallResult:
        ingest_scope = scope or []
        resolved_name = tool_name or tool_id
        self.policy.require(
            actor_id,
            "evidence.ingest",
            scope=ingest_scope,
            namespace=namespace,
            tool=tool_id,
        )
        evidence_ref = self.record_tool_result(
            tool_id=tool_id,
            tool_name=resolved_name,
            tool_type=tool_type,
            actor_id=actor_id,
            scope=ingest_scope,
            namespace=namespace,
            input_payload=input_payload or {},
            output=output,
            source_uri=source_uri,
        )
        result = ToolCallResult(
            tool_id=tool_id,
            tool_name=resolved_name,
            tool_type=tool_type,
            actor_id=actor_id,
            scope=ingest_scope,
            input=input_payload or {},
            output=output,
            evidence_ref=evidence_ref,
            executed=executed,
            status=status,
        )
        self.audit.record(
            "evidence.ingest_tool_result",
            actor_id,
            evidence_ref,
            {
                "status": status,
                "tool_id": tool_id,
                "tool_type": tool_type,
                "tool_call_id": result.id,
                "source_uri": source_uri,
            },
        )
        return result

    def record_tool_result(
        self,
        *,
        tool_id: str,
        tool_name: str,
        tool_type: str,
        actor_id: str | None,
        scope: list[str],
        namespace: str,
        input_payload: dict[str, object],
        output: dict[str, object],
        source_uri: str | None = None,
    ) -> str:
        evidence_id = new_id("ev")
        public_payload = {
            "tool_id": tool_id,
            "tool_name": tool_name,
            "tool_type": tool_type,
            "input_hash": hash_json(input_payload),
            "output": output,
        }
        if source_uri:
            public_payload["source_uri"] = source_uri
        now = now_iso()
        record: dict[str, object] = {
            "id": evidence_id,
            "kind": "tool_result",
            "uri": f"oacs://tools/{tool_id}/results/{evidence_id}",
            "public_payload": public_payload,
            "sensitive_ciphertext": None,
            "sensitive_nonce": None,
            "content_hash": hash_json(public_payload),
            "status": "active",
            "namespace": namespace,
            "scope": scope,
            "owner_actor_id": actor_id,
            "created_at": now,
            "updated_at": now,
        }
        self.repo.save(record)
        return evidence_id
