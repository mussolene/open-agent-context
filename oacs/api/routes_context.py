from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from oacs.app import services

router = APIRouter(prefix="/v1")


class ContextBuild(BaseModel):
    actor_id: str | None = None
    agent_id: str | None = None
    intent: str
    scope: list[str] = []
    token_budget: int = 4000


@router.post("/context/build")
def build(req: ContextBuild) -> dict[str, object]:
    return (
        services()
        .context.build(req.intent, req.actor_id, req.agent_id, req.scope, req.token_budget)
        .model_dump()
    )


@router.get("/context/{capsule_id}")
def get_context(capsule_id: str, actor_id: str | None = None) -> dict[str, object]:
    return services().context.read(capsule_id, actor_id).model_dump()


@router.post("/context/validate")
def validate_context(req: dict[str, object]) -> dict[str, object]:
    return services(require_key=False).context.validate_payload(req)


@router.post("/context/import")
def import_context(req: dict[str, object]) -> dict[str, object]:
    actor_id = req.pop("actor_id", None)
    return (
        services()
        .context.import_capsule(req, actor_id if isinstance(actor_id, str) else None)
        .model_dump()
    )


@router.post("/context/{capsule_id}/lock")
def lock_context(capsule_id: str, req: dict[str, str | None]) -> dict[str, object]:
    return services().context.set_status(capsule_id, req.get("actor_id"), "locked")


@router.post("/context/{capsule_id}/explain")
def explain(capsule_id: str, req: dict[str, str | None]) -> dict[str, object]:
    return services().context.explain(capsule_id, req.get("actor_id"))


@router.post("/capsules/{capsule_id}/grant")
def grant(capsule_id: str, req: dict[str, str]) -> dict[str, object]:
    grant_obj = services(require_key=False).capabilities.grant(
        req["subject_actor_id"], "system", ["context.export"]
    )
    return {"capsule_id": capsule_id, "grant": grant_obj.model_dump()}


@router.post("/capsules/{capsule_id}/revoke")
def revoke(capsule_id: str, req: dict[str, str]) -> dict[str, object]:
    svc = services()
    svc.context.read(capsule_id, req.get("actor_id"))
    revoked = 0
    for grant in svc.store.list(
        "capability_grants",
        "WHERE subject_actor_id=? AND status='active'",
        (req["subject_actor_id"],),
    ):
        if "context.export" in grant["allowed_operations"] or "*" in grant["allowed_operations"]:
            grant["status"] = "revoked"
            svc.store.put_json("capability_grants", grant)
            revoked += 1
    return {
        "capsule_id": capsule_id,
        "subject_actor_id": req["subject_actor_id"],
        "revoked": revoked,
    }


@router.post("/rules/check")
def rules_check(req: dict[str, str]) -> list[dict[str, object]]:
    return [
        r.model_dump()
        for r in services(require_key=False).rules.check(req.get("operation", "context.build"))
    ]


@router.get("/capabilities")
def list_capabilities() -> list[dict[str, object]]:
    return [
        capability.model_dump()
        for capability in services(require_key=False).capabilities.list_definitions()
    ]


@router.get("/capabilities/{capability_id}")
def inspect_capability(capability_id: str) -> dict[str, object]:
    return services(require_key=False).capabilities.inspect_definition(capability_id).model_dump()


@router.get("/rules")
def list_rules() -> list[dict[str, object]]:
    return [rule.model_dump() for rule in services(require_key=False).rules.list()]


@router.get("/rules/{rule_id}")
def inspect_rule(rule_id: str) -> dict[str, object]:
    for rule in services(require_key=False).rules.list():
        if rule.id == rule_id or rule.name == rule_id:
            return rule.model_dump()
    return {"error": "not found"}


@router.get("/skills")
def list_skills() -> list[dict[str, object]]:
    return [skill.model_dump() for skill in services(require_key=False).skills.list()]


@router.get("/skills/{skill_id}")
def inspect_skill(skill_id: str) -> dict[str, object]:
    return services(require_key=False).skills.inspect(skill_id).model_dump()


@router.get("/tools")
def list_tools() -> list[dict[str, object]]:
    return [tool.model_dump() for tool in services(require_key=False).tools.list()]


@router.get("/tools/{tool_id}")
def inspect_tool(tool_id: str) -> dict[str, object]:
    return services(require_key=False).tools.inspect(tool_id).model_dump()


@router.get("/mcp")
def list_mcp() -> list[dict[str, object]]:
    return [binding.model_dump() for binding in services(require_key=False).mcp.list()]


@router.get("/mcp/{binding_id}")
def inspect_mcp(binding_id: str) -> dict[str, object]:
    return services(require_key=False).mcp.inspect(binding_id).model_dump()


@router.post("/loop/run")
def loop_run(req: dict[str, object]) -> dict[str, object]:
    return (
        services()
        .loop.run(
            str(req["user_request"]),
            req.get("actor_id"),  # type: ignore[arg-type]
            req.get("agent_id"),  # type: ignore[arg-type]
            req.get("scope", []),  # type: ignore[arg-type]
        )
        .model_dump()
    )
