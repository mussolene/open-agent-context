from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository

ActorType = Literal["human", "agent", "application", "tool", "service", "organization"]


class Actor(BaseModel):
    id: str = Field(default_factory=lambda: new_id("act"))
    type: ActorType
    name: str
    public_key_ref: str | None = None
    trust_level: int = 0
    owner_actor_id: str | None = None
    created_at: str = Field(default_factory=now_iso)
    updated_at: str = Field(default_factory=now_iso)
    status: str = "active"
    namespace: str = "default"
    scope: list[str] = Field(default_factory=list)
    content_hash: str = ""

    def to_record(self) -> dict[str, object]:
        data = self.model_dump()
        data["content_hash"] = hash_json({k: v for k, v in data.items() if k != "content_hash"})
        return data


class ActorService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def create(self, actor_type: ActorType, name: str, owner_actor_id: str | None = None) -> Actor:
        actor = Actor(type=actor_type, name=name, owner_actor_id=owner_actor_id)
        self.repo.save(actor.to_record())
        return actor

    def list(self) -> list[Actor]:
        return [Actor(**row) for row in self.repo.list(order_by=[("created_at", "asc")])]
