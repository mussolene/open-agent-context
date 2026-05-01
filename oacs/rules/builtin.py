from __future__ import annotations

from oacs.rules.models import RuleManifest


def builtin_rules() -> list[RuleManifest]:
    return [
        RuleManifest(
            id="rule_no_secret_leak",
            name="no_secret_leak",
            rule_kind="safety_rule",
            content="Do not export sensitive payloads without capability.",
            applies_to=["capsule.export", "memory.export"],
            enforcement_mode="block",
            blocking=True,
            priority=10,
        ),
        RuleManifest(
            id="rule_no_unconfirmed_sensitive_memory_commit",
            name="no_unconfirmed_sensitive_memory_commit",
            rule_kind="hard_policy",
            content="Sensitive memories require confirmation before commit.",
            applies_to=["memory.commit"],
            enforcement_mode="require_confirmation",
            blocking=True,
            priority=20,
        ),
        RuleManifest(
            id="rule_fuzzy_memory_not_fact",
            name="fuzzy_memory_not_fact",
            rule_kind="workflow_rule",
            content="D3-D5 memory must be marked as hypothesis.",
            applies_to=["context.build", "loop.run"],
            enforcement_mode="annotate_context",
            priority=30,
        ),
        RuleManifest(
            id="rule_deny_tool_write_without_capability",
            name="deny_tool_write_without_capability",
            rule_kind="hard_policy",
            content="Write tools require explicit tool.call capability.",
            applies_to=["tool.call"],
            enforcement_mode="block",
            blocking=True,
            priority=40,
        ),
        RuleManifest(
            id="rule_audit_all_memory_access",
            name="audit_all_memory_access",
            rule_kind="workflow_rule",
            content="All memory access must create audit events.",
            applies_to=["memory.read", "memory.query"],
            enforcement_mode="annotate_context",
            priority=50,
        ),
    ]
