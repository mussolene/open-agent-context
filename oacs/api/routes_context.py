from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from oacs.app import services
from oacs.core.errors import AccessDenied
from oacs.skills.runner import run_builtin_skill

router = APIRouter(prefix="/v1")


def _string_list(value: object) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return None


def _dict_payload(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


class ContextBuild(BaseModel):
    actor_id: str | None = None
    agent_id: str | None = None
    intent: str
    scope: list[str] = []
    token_budget: int = 4000


@router.post("/context/build")
def build(req: ContextBuild) -> dict[str, object]:
    svc = services()
    try:
        capsule = svc.context.build(
            req.intent, req.actor_id, req.agent_id, req.scope, req.token_budget
        )
    except AccessDenied as exc:
        svc.audit.record("context.build", req.actor_id, None, {"status": "denied"})
        raise exc
    svc.audit.record("context.build", req.actor_id, capsule.id)
    return capsule.model_dump()


@router.get("/context/{capsule_id}")
def get_context(capsule_id: str, actor_id: str | None = None) -> dict[str, object]:
    svc = services()
    try:
        capsule = svc.context.read(capsule_id, actor_id)
    except AccessDenied as exc:
        svc.audit.record("context.export", actor_id, capsule_id, {"status": "denied"})
        raise exc
    svc.audit.record("context.export", actor_id, capsule.id, {"status": "completed"})
    return capsule.model_dump()


@router.post("/context/{capsule_id}/export")
def export_context(capsule_id: str, req: dict[str, str | None]) -> dict[str, object]:
    svc = services()
    actor_id = req.get("actor_id")
    try:
        exported = svc.context.export_capsule(capsule_id, actor_id)
    except AccessDenied as exc:
        svc.audit.record("context.export", actor_id, capsule_id, {"status": "denied"})
        raise exc
    svc.audit.record("context.export", actor_id, capsule_id, {"status": "completed"})
    return exported.model_dump()


@router.post("/context/validate")
def validate_context(req: dict[str, object]) -> dict[str, object]:
    requires_key = req.get("export_type") == "context_capsule_export"
    return services(require_key=requires_key).context.validate_payload(req)


@router.post("/context/import")
def import_context(req: dict[str, object]) -> dict[str, object]:
    actor_id = req.pop("actor_id", None)
    svc = services()
    capsule = svc.context.import_capsule(req, actor_id if isinstance(actor_id, str) else None)
    svc.audit.record("context.import", actor_id if isinstance(actor_id, str) else None, capsule.id)
    return capsule.model_dump()


@router.post("/context/{capsule_id}/lock")
def lock_context(capsule_id: str, req: dict[str, str | None]) -> dict[str, object]:
    svc = services()
    result = svc.context.set_status(capsule_id, req.get("actor_id"), "locked")
    svc.audit.record("context.lock", req.get("actor_id"), capsule_id)
    return result


@router.post("/context/{capsule_id}/explain")
def explain(capsule_id: str, req: dict[str, str | None]) -> dict[str, object]:
    svc = services()
    result = svc.context.explain(capsule_id, req.get("actor_id"))
    svc.audit.record("context.explain", req.get("actor_id"), capsule_id)
    return result


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
        filters={"subject_actor_id": req["subject_actor_id"], "status": "active"},
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


@router.post("/capabilities/grant")
def grant_capability(req: dict[str, object]) -> dict[str, object]:
    allowed = req.get("allowed_operations", req.get("operations", []))
    if not isinstance(allowed, list) or not all(isinstance(item, str) for item in allowed):
        allowed = []
    grant_obj = services(require_key=False).capabilities.grant(
        str(req["subject_actor_id"]),
        str(req.get("issuer_actor_id", "system")),
        allowed,
        scope=_string_list(req.get("scope")),
        memory_depth_allowed=int(str(req.get("memory_depth_allowed", 2))),
        namespaces_allowed=_string_list(req.get("namespaces_allowed")),
        tools_allowed=_string_list(req.get("tools_allowed")),
        skills_allowed=_string_list(req.get("skills_allowed")),
        denied_operations=_string_list(req.get("denied_operations")),
    )
    return grant_obj.model_dump()


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


@router.post("/skills/{skill_id}/run")
def run_skill(skill_id: str, req: dict[str, object]) -> dict[str, object]:
    svc = services(require_key=False)
    raw_actor = req.get("actor_id")
    actor_id: str | None = raw_actor if isinstance(raw_actor, str) else None
    skill = svc.skills.inspect(skill_id)
    scope: list[str] = skill.scope or _string_list(req.get("scope")) or []
    if not (
        svc.policy.allows(
            actor_id, "skill.run", scope=scope, namespace=skill.namespace, skill=skill.id
        )
        or svc.policy.allows(
            actor_id, "skill.run", scope=scope, namespace=skill.namespace, skill=skill.name
        )
    ):
        svc.policy.require(
            actor_id, "skill.run", scope=scope, namespace=skill.namespace, skill=skill.id
        )
    payload = _dict_payload(req.get("payload"))
    result = run_builtin_skill(skill.name, payload)
    svc.audit.record("skill.run", actor_id, skill.id, {"status": "completed"})
    return result


@router.get("/tools")
def list_tools() -> list[dict[str, object]]:
    return [tool.model_dump() for tool in services(require_key=False).tools.list()]


@router.get("/tools/{tool_id}")
def inspect_tool(tool_id: str) -> dict[str, object]:
    return services(require_key=False).tools.inspect(tool_id).model_dump()


@router.post("/tools/{tool_id}/call")
def call_tool(tool_id: str, req: dict[str, object]) -> dict[str, object]:
    svc = services(require_key=False)
    raw_actor = req.get("actor_id")
    actor_id: str | None = raw_actor if isinstance(raw_actor, str) else None
    payload = _dict_payload(req.get("payload"))
    return svc.tool_runner.call(
        tool_id,
        payload,
        actor_id=actor_id,
        scope=_string_list(req.get("scope")),
        execute_mcp=bool(req.get("execute_mcp", False)),
    ).model_dump()


@router.post("/tools/results/ingest")
def ingest_tool_result(req: dict[str, object]) -> dict[str, object]:
    svc = services(require_key=False)
    raw_actor = req.get("actor_id")
    actor_id: str | None = raw_actor if isinstance(raw_actor, str) else None
    tool_id = req.get("tool_id")
    if not isinstance(tool_id, str) or not tool_id:
        return {"error": "tool_id is required"}
    tool_name = req.get("tool_name")
    tool_type = req.get("tool_type", "external")
    namespace = req.get("namespace", "default")
    source_uri = req.get("source_uri")
    status = req.get("status", "completed")
    return svc.evidence.ingest_tool_result(
        tool_id=tool_id,
        tool_name=tool_name if isinstance(tool_name, str) else None,
        tool_type=tool_type if isinstance(tool_type, str) else "external",
        output=_dict_payload(req.get("output")),
        input_payload=_dict_payload(req.get("input")),
        actor_id=actor_id,
        scope=_string_list(req.get("scope")) or [],
        namespace=namespace if isinstance(namespace, str) else "default",
        source_uri=source_uri if isinstance(source_uri, str) else None,
        status=status if isinstance(status, str) else "completed",
        executed=bool(req.get("executed", True)),
    ).model_dump()


@router.get("/mcp")
def list_mcp() -> list[dict[str, object]]:
    return [binding.model_dump() for binding in services(require_key=False).mcp.list()]


@router.get("/mcp/{binding_id}")
def inspect_mcp(binding_id: str) -> dict[str, object]:
    return services(require_key=False).mcp.inspect(binding_id).model_dump()


@router.post("/mcp/import")
def import_mcp(req: dict[str, object]) -> list[dict[str, object]]:
    path = req.get("file")
    if not isinstance(path, str):
        return [{"error": "file is required"}]
    svc = services(require_key=False)
    imported = svc.mcp.import_config(path)
    for binding in imported:
        svc.audit.record("mcp.import", None, binding.id)
    return [binding.model_dump() for binding in imported]


@router.post("/loop/run")
def loop_run(req: dict[str, object]) -> dict[str, object]:
    model_config = req.get("model_config")
    return (
        services()
        .loop.run(
            str(req["user_request"]),
            req.get("actor_id"),  # type: ignore[arg-type]
            req.get("agent_id"),  # type: ignore[arg-type]
            req.get("scope", []),  # type: ignore[arg-type]
            int(str(req.get("token_budget", 4000))),
            req.get("allowed_tools"),  # type: ignore[arg-type]
            model_config if isinstance(model_config, dict) else None,
        )
        .model_dump()
    )
