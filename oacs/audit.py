from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any, cast

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository

_AUDIT_TAIL_HASH_KEY = "audit_tail_hash"
_AUDIT_TAIL_CREATED_AT_KEY = "audit_tail_created_at"


class AuditService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def record(
        self,
        operation: str,
        actor_id: str | None = None,
        target_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> dict[str, object]:
        event: dict[str, object] = {
            "id": new_id("aud"),
            "operation": operation,
            "actor_id": actor_id,
            "target_id": target_id,
            "metadata": metadata or {},
            "previous_hash": None,
            "created_at": now_iso(),
            "status": "active",
            "namespace": "default",
            "scope": [],
            "owner_actor_id": actor_id,
        }
        atomic_append = getattr(self.repo.store, "append_audit_event", None)
        if callable(atomic_append):
            append = cast(Callable[[dict[str, object]], dict[str, object]], atomic_append)
            return append(event)
        previous_hash = self.repo.store.get_metadata(_AUDIT_TAIL_HASH_KEY)
        previous_created_at = self.repo.store.get_metadata(_AUDIT_TAIL_CREATED_AT_KEY)
        if previous_hash is None:
            previous = _audit_tail(
                self.repo.list(order_by=[("created_at", "asc"), ("id", "asc")])
            )
            if previous:
                previous_hash = str(previous["content_hash"])
                previous_created_at = str(previous["created_at"])
        event["previous_hash"] = previous_hash
        event["created_at"] = _after_previous_timestamp(
            str(event["created_at"]), previous_created_at
        )
        event["content_hash"] = hash_json(event)
        self.repo.save(event)
        self.repo.store.set_metadata(_AUDIT_TAIL_HASH_KEY, str(event["content_hash"]))
        self.repo.store.set_metadata(_AUDIT_TAIL_CREATED_AT_KEY, str(event["created_at"]))
        return event

    def list(self) -> list[dict[str, object]]:
        events = self.repo.list(order_by=[("created_at", "asc"), ("id", "asc")])
        return _chain_order(events)

    def verify_chain(self) -> dict[str, object]:
        events = self.list()
        return _verify_ordered_events(events)

    def repair_chain(self, write: bool = False) -> dict[str, object]:
        events = self.repo.list(order_by=[("created_at", "asc"), ("id", "asc")])
        repaired, summary = _repair_events(events)
        if write and summary["content_hash_mismatch_count"]:
            raise ValueError("audit repair refused because existing content hashes do not validate")
        if write:
            rewrite = getattr(self.repo.store, "rewrite_audit_events", None)
            if callable(rewrite):
                rewrite(repaired)
            else:
                for event in repaired:
                    self.repo.save(event)
                if repaired:
                    tail = repaired[-1]
                    self.repo.store.set_metadata(
                        _AUDIT_TAIL_HASH_KEY, str(tail["content_hash"])
                    )
                    self.repo.store.set_metadata(
                        _AUDIT_TAIL_CREATED_AT_KEY, str(tail["created_at"])
                    )
            summary["written"] = True
        return summary


def _verify_ordered_events(events: list[dict[str, object]]) -> dict[str, object]:
        errors: list[dict[str, object]] = []
        previous_hash: str | None = None
        for index, event in enumerate(events):
            expected_hash = _event_hash(event)
            if event.get("content_hash") != expected_hash:
                errors.append(
                    {
                        "index": index,
                        "id": event.get("id"),
                        "error": "content_hash_mismatch",
                    }
                )
            if event.get("previous_hash") != previous_hash:
                errors.append(
                    {
                        "index": index,
                        "id": event.get("id"),
                        "error": "previous_hash_mismatch",
                    }
                )
            previous_hash = str(event.get("content_hash") or "")
        return {"valid": not errors, "events": len(events), "errors": errors}


def _event_hash(event: dict[str, object]) -> str:
    payload = {key: value for key, value in event.items() if key != "content_hash"}
    return hash_json(payload)


def _chain_order(events: list[dict[str, object]]) -> list[dict[str, object]]:
    sorted_events = sorted(events, key=_event_sort_key)
    children: dict[str | None, list[dict[str, object]]] = {}
    for event in sorted_events:
        previous_hash = event.get("previous_hash")
        key = str(previous_hash) if previous_hash else None
        children.setdefault(key, []).append(event)

    ordered: list[dict[str, object]] = []
    seen: set[str] = set()

    def event_key(event: dict[str, object]) -> str:
        return str(event.get("id") or id(event))

    def append_chain(start: dict[str, object]) -> None:
        current: dict[str, object] | None = start
        while current is not None:
            key = event_key(current)
            if key in seen:
                return
            ordered.append(current)
            seen.add(key)

            content_hash = current.get("content_hash")
            if not content_hash:
                return
            next_events = [
                event
                for event in children.get(str(content_hash), [])
                if event_key(event) not in seen
            ]
            current = next_events[0] if next_events else None

    for event in children.get(None, []):
        append_chain(event)

    for event in sorted_events:
        if event_key(event) not in seen:
            append_chain(event)

    return ordered


def _event_sort_key(event: dict[str, object]) -> tuple[str, str]:
    return (str(event.get("created_at") or ""), str(event.get("id") or ""))


def _after_previous_timestamp(candidate: str, previous: str | None) -> str:
    if previous is None:
        return candidate
    candidate_dt = _parse_datetime(candidate)
    previous_dt = _parse_datetime(previous)
    if candidate_dt is None or previous_dt is None or candidate_dt > previous_dt:
        return candidate
    return (previous_dt + timedelta(microseconds=1)).isoformat()


def _audit_tail(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not events:
        return None
    referenced = {
        str(event["previous_hash"])
        for event in events
        if event.get("previous_hash") not in (None, "")
    }
    tails = [event for event in events if str(event.get("content_hash")) not in referenced]
    return max(tails or events, key=_event_sort_key)


def _repair_events(
    events: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    ordered = sorted(events, key=_event_sort_key)
    before = _verify_ordered_events(_chain_order(ordered))
    repaired: list[dict[str, object]] = []
    changed_ids: list[str] = []
    mismatch_ids: list[str] = []
    previous_hash: str | None = None
    previous_created_at: str | None = None
    for event in ordered:
        if event.get("content_hash") != _event_hash(event):
            mismatch_ids.append(str(event.get("id")))
        fixed = dict(event)
        fixed["previous_hash"] = previous_hash
        fixed["created_at"] = _after_previous_timestamp(
            str(fixed.get("created_at") or ""), previous_created_at
        )
        fixed["content_hash"] = _event_hash(fixed)
        if (
            fixed.get("previous_hash") != event.get("previous_hash")
            or fixed.get("created_at") != event.get("created_at")
            or fixed.get("content_hash") != event.get("content_hash")
        ):
            changed_ids.append(str(event.get("id")))
        repaired.append(fixed)
        previous_hash = str(fixed["content_hash"])
        previous_created_at = str(fixed["created_at"])

    after = _verify_ordered_events(repaired)
    before_errors = cast(list[dict[str, object]], before["errors"])
    after_errors = cast(list[dict[str, object]], after["errors"])
    summary: dict[str, object] = {
        "valid_before": before["valid"],
        "valid_after": after["valid"],
        "events": len(events),
        "error_count_before": len(before_errors),
        "error_count_after": len(after_errors),
        "changed_events": len(changed_ids),
        "first_changed_ids": changed_ids[:20],
        "content_hash_mismatch_count": len(mismatch_ids),
        "first_content_hash_mismatch_ids": mismatch_ids[:20],
        "written": False,
    }
    return repaired, summary


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
