from __future__ import annotations

from collections.abc import Sequence

from oacs.core.errors import AccessDenied
from oacs.core.time import now_iso
from oacs.identity.capabilities import CapabilityService

DEFAULT_BOOTSTRAP_ACTOR = "system"


class PolicyEngine:
    def __init__(self, capabilities: CapabilityService):
        self.capabilities = capabilities

    def check(
        self,
        actor_id: str | None,
        operation: str,
        depth: int | None = None,
        scope: Sequence[str] | None = None,
        namespace: str | None = None,
    ) -> bool:
        if actor_id in (None, "", DEFAULT_BOOTSTRAP_ACTOR):
            return True
        grants = self.capabilities.for_actor(str(actor_id))
        for grant in grants:
            if grant.expires_at and grant.expires_at <= now_iso():
                continue
            if operation in grant.denied_operations:
                raise AccessDenied(f"operation denied by capability: {operation}")
            operation_allowed = (
                operation in grant.allowed_operations or "*" in grant.allowed_operations
            )
            depth_allowed = depth is None or depth <= grant.memory_depth_allowed
            namespace_allowed = self._namespace_matches(namespace, grant.namespaces_allowed)
            scope_allowed = self._scope_matches(scope, grant.scope)
            if operation_allowed and depth_allowed and namespace_allowed and scope_allowed:
                return True
        raise AccessDenied(f"operation requires capability: {operation}")

    def require(
        self,
        actor_id: str | None,
        operation: str,
        depth: int | None = None,
        scope: Sequence[str] | None = None,
        namespace: str | None = None,
    ) -> None:
        self.check(actor_id, operation, depth, scope, namespace)

    def allows(
        self,
        actor_id: str | None,
        operation: str,
        depth: int | None = None,
        scope: Sequence[str] | None = None,
        namespace: str | None = None,
    ) -> bool:
        try:
            return self.check(actor_id, operation, depth, scope, namespace)
        except AccessDenied:
            return False

    @staticmethod
    def _namespace_matches(namespace: str | None, allowed: Sequence[str]) -> bool:
        if namespace is None:
            return True
        return "*" in allowed or namespace in allowed

    @staticmethod
    def _scope_matches(scope: Sequence[str] | None, grant_scope: Sequence[str]) -> bool:
        if not grant_scope or "*" in grant_scope:
            return True
        if not scope:
            return False
        return set(scope).issubset(set(grant_scope))
