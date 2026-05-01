from __future__ import annotations

from oacs.context.capsule import ContextCapsule


def explain_capsule(capsule: ContextCapsule) -> dict[str, object]:
    return {
        "id": capsule.id,
        "why": "Capsule assembled from relevant memory, active rules, registries, and policy.",
        "counts": {
            "memories": len(capsule.included_memories),
            "rules": len(capsule.included_rules),
            "skills": len(capsule.included_skills),
            "tools": len(capsule.included_tools),
        },
    }
