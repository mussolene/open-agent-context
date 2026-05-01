from __future__ import annotations

from oacs.benchmark.models import BenchmarkTask


def score_answer(task: BenchmarkTask, answer: str) -> dict[str, object]:
    answer_lower = answer.lower()
    used = [fact for fact in task.expected_facts if fact.lower() in answer_lower]
    forbidden = [fact for fact in task.forbidden_facts if fact.lower() in answer_lower]
    score = 0
    if used:
        score += 4
    if not forbidden:
        score += 1
    return {
        "exact_success": bool(used and not forbidden),
        "rubric_score": score,
        "used_required_fact": bool(used),
        "ignored_superseded_memory": not forbidden,
        "output_json_valid": True,
    }
