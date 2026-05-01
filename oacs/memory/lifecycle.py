from __future__ import annotations

ALLOWED_TRANSITIONS = {
    "observed": {"candidate", "forgotten"},
    "candidate": {"clarifying", "confirmed", "active", "forgotten"},
    "clarifying": {"confirmed", "deprecated", "forgotten"},
    "confirmed": {"active", "deprecated", "forgotten"},
    "active": {"deprecated", "superseded", "forgotten"},
    "deprecated": {"superseded", "forgotten"},
    "superseded": {"forgotten"},
    "forgotten": set(),
}


def can_transition(old: str, new: str) -> bool:
    return old == new or new in ALLOWED_TRANSITIONS.get(old, set())
