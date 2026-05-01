from __future__ import annotations


def test_builtin_rules_load_and_check(svc):
    rules = svc.rules.list()
    assert any(rule.name == "fuzzy_memory_not_fact" for rule in rules)
    result = svc.rules.check("context.build", {"memories": [{"depth": 3}]})
    assert any(item.status == "warn" for item in result)
