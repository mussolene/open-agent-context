from __future__ import annotations


def evaluate_answer(answer: str, required_facts: list[str] | None = None) -> dict[str, object]:
    required_facts = required_facts or []
    used = [fact for fact in required_facts if fact.lower() in answer.lower()]
    return {"score": len(used), "used_required_facts": used}
