from __future__ import annotations

import builtins
from typing import Any, cast

from oacs.rules.builtin import builtin_rules
from oacs.rules.models import RuleManifest, RuleResult
from oacs.storage.repositories import Repository


class RuleEngine:
    def __init__(self, repo: Repository):
        self.repo = repo

    def ensure_builtin(self) -> None:
        existing = {row["id"] for row in self.repo.list()}
        for rule in builtin_rules():
            if rule.id not in existing:
                self.repo.save(rule.to_record())

    def add(self, rule: RuleManifest) -> RuleManifest:
        self.repo.save(rule.to_record())
        return rule

    def list(self) -> list[RuleManifest]:
        self.ensure_builtin()
        return [
            RuleManifest(**row) for row in self.repo.list("WHERE status='active' ORDER BY priority")
        ]

    def check(
        self, operation: str, payload: dict[str, Any] | None = None
    ) -> builtins.list[RuleResult]:
        payload = payload or {}
        results: builtins.list[RuleResult] = []
        for rule in self.list():
            if rule.applies_to and operation not in rule.applies_to:
                continue
            status = "pass"
            message = rule.content
            if rule.name == "fuzzy_memory_not_fact":
                memories = cast(builtins.list[dict[str, object]], payload.get("memories", []) or [])
                for mem in memories:
                    if isinstance(mem, dict) and int(str(mem.get("depth", 0))) >= 3:
                        status = "warn"
                        message = "D3-D5 memory included as hypothesis only."
            results.append(
                RuleResult(
                    rule_id=rule.id,
                    name=rule.name,
                    status=status,
                    message=message,
                    blocking=rule.blocking and status == "fail",
                )
            )
        return results
