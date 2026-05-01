from __future__ import annotations


def classify_intent(user_request: str) -> str:
    lowered = user_request.lower()
    if "report" in lowered or "отч" in lowered:
        return "answer_project_question"
    return "general_task"
