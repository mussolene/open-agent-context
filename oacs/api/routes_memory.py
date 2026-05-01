from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from oacs.app import services

router = APIRouter(prefix="/v1")


class ActorCreate(BaseModel):
    actor_id: str | None = None
    type: str
    name: str


class MemoryWrite(BaseModel):
    actor_id: str | None = None
    memory_type: str = "fact"
    depth: int = 2
    text: str
    scope: list[str] = []


class MemoryQuery(BaseModel):
    actor_id: str | None = None
    query: str = ""
    scope: list[str] = []


@router.post("/actors")
def create_actor(req: ActorCreate) -> dict[str, object]:
    svc = services(require_key=False)
    actor = svc.actors.create(req.type, req.name)  # type: ignore[arg-type]
    if req.type == "human":
        svc.capabilities.grant(actor.id, "system", ["*"], memory_depth_allowed=5)
    return actor.model_dump()


@router.get("/actors")
def list_actors() -> list[dict[str, object]]:
    return [a.model_dump() for a in services(require_key=False).actors.list()]


@router.post("/memory/observe")
def observe(req: MemoryWrite) -> dict[str, object]:
    svc = services()
    mem = svc.memory.observe(req.text, req.actor_id, req.scope)
    svc.audit.record("memory.observe", req.actor_id, mem.id)
    return mem.model_dump()


@router.post("/memory/propose")
def propose(req: MemoryWrite) -> dict[str, object]:
    svc = services()
    mem = svc.memory.propose(req.memory_type, req.depth, req.text, req.actor_id, req.scope)
    svc.audit.record("memory.propose", req.actor_id, mem.id)
    return mem.model_dump()


@router.post("/memory/commit")
def commit(req: dict[str, str | None]) -> dict[str, object]:
    svc = services()
    mem = svc.memory.commit(str(req["memory_id"]), req.get("actor_id"))
    svc.audit.record("memory.commit", req.get("actor_id"), mem.id)
    return mem.model_dump()


@router.post("/memory/query")
def query(req: MemoryQuery) -> list[dict[str, object]]:
    svc = services()
    result = svc.memory.query(req.query, req.actor_id, req.scope)
    svc.audit.record("memory.query", req.actor_id)
    return [m.model_dump() for m in result]


@router.get("/memory/{memory_id}")
def read(memory_id: str, actor_id: str | None = None) -> dict[str, object]:
    svc = services()
    mem = svc.memory.read(memory_id, actor_id)
    svc.audit.record("memory.read", actor_id, mem.id)
    return mem.model_dump()


@router.post("/memory/{memory_id}/correct")
def correct(memory_id: str, req: MemoryWrite) -> dict[str, object]:
    return services().memory.correct(memory_id, req.text, req.actor_id).model_dump()


@router.post("/memory/{memory_id}/forget")
def forget(memory_id: str, req: dict[str, str | None]) -> dict[str, object]:
    return services().memory.forget(memory_id, req.get("actor_id")).model_dump()


@router.post("/memory/blur")
def blur(req: dict[str, str | None]) -> dict[str, object]:
    return services().memory.blur(str(req["memory_id"]), req.get("actor_id")).model_dump()


@router.post("/memory/sharpen")
def sharpen(req: dict[str, str | None]) -> dict[str, object]:
    return (
        services()
        .memory.sharpen(
            str(req["memory_id"]),
            str(req["evidence_ref"]),
            req.get("actor_id"),
        )
        .model_dump()
    )
