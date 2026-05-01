from __future__ import annotations

from oacs.core.errors import AccessDenied
from oacs.identity.capabilities import CapabilityService

DEFAULT_BOOTSTRAP_ACTOR = "system"


class PolicyEngine:
    def __init__(self, capabilities: CapabilityService):
        self.capabilities = capabilities

    def check(self, actor_id: str | None, operation: str, depth: int | None = None) -> bool:
        if actor_id in (None, "", DEFAULT_BOOTSTRAP_ACTOR):
            return True
        grants = self.capabilities.for_actor(str(actor_id))
        for grant in grants:
            if operation in grant.denied_operations:
                raise AccessDenied(f"operation denied by capability: {operation}")
            if (operation in grant.allowed_operations or "*" in grant.allowed_operations) and (
                depth is None or depth <= grant.memory_depth_allowed
            ):
                return True
        raise AccessDenied(f"operation requires capability: {operation}")

    def require(self, actor_id: str | None, operation: str, depth: int | None = None) -> None:
        self.check(actor_id, operation, depth)
