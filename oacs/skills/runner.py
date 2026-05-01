from __future__ import annotations


def run_builtin_skill(name: str, payload: dict[str, object]) -> dict[str, object]:
    if name == "contradiction_resolver":
        return {"conflicts": [], "requires_sharpening": False}
    if name == "task_trace_distiller":
        return {"candidate_memory": str(payload.get("trace", ""))[:1000]}
    return {"result": payload}
