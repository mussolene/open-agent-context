from __future__ import annotations

from fastapi import APIRouter

from oacs.app import services

router = APIRouter(prefix="/v1")


@router.get("/audit")
def list_audit() -> list[dict[str, object]]:
    return services(require_key=False).audit.list()


@router.get("/audit/verify")
def verify_audit() -> dict[str, object]:
    return services(require_key=False).audit.verify_chain()


@router.get("/audit/{audit_id}")
def get_audit(audit_id: str) -> dict[str, object]:
    events = [e for e in services(require_key=False).audit.list() if e["id"] == audit_id]
    return events[0] if events else {"error": "not found"}
