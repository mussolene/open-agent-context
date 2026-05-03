# OACS Conformance Fixtures / OACS Conformance Fixtures

## EN
This directory contains language-neutral JSON fixtures for the OACS v0.1 draft.
They are standard contract examples, not Python object snapshots. A runtime can
validate them with the JSON Schemas in `schemas/` without importing the `oacs`
Python package or using SQLite.

The Python package remains the reference implementation and test harness for
these fixtures. Other implementations should treat the JSON shape, checksum
canonicalization, scope semantics, and evidence references as the portable
surface.

Use `docs/INTEROPERABILITY.md` as the implementation checklist when building a
runtime, SDK, adapter, or validation harness outside Python.

The Python reference package includes a convenience checker:

```bash
acs conformance validate --json
```

This command is a reference validation harness for the bundled fixtures. Passing
it is useful for package and adapter development, but the portable contract
remains the JSON records and schemas.

Fixtures:

- `fixtures/context_capsule.json`
- `fixtures/memory_record.json`
- `fixtures/capability_grant.json`
- `fixtures/evidence_ref.json`
- `fixtures/rule_manifest.json`
- `fixtures/skill_manifest.json`
- `fixtures/tool_binding.json`
- `fixtures/mcp_binding.json`
- `fixtures/audit_event.json`
- `fixtures/protected_ref.json`
- `fixtures/secret_record.json`
- `fixtures/sensitive_fact.json`
- `fixtures/memory_call.json`
- `fixtures/memory_operation.json`
- `fixtures/context_operation.json`
- `fixtures/memory_loop_run.json`
- `fixtures/tool_call_result.json`
- `fixtures/storage_selector.json`
- `fixtures/retrieval_query.json`
- `fixtures/retrieval_result.json`

Negative fixtures in `negative/` cover schema and semantic boundary failures
that adapters should reject before projection into task context.

## RU
Этот каталог содержит language-neutral JSON fixtures для OACS v0.1 draft. Это
examples standard contract, а не snapshots Python objects. Runtime может
валидировать их JSON Schemas из `schemas/` без import Python package `oacs` и
без SQLite.

Python package остаётся reference implementation и test harness для этих
fixtures. Другие реализации должны считать portable surface JSON shape,
checksum canonicalization, scope semantics и evidence references.

Используйте `docs/INTEROPERABILITY.md` как implementation checklist при
создании runtime, SDK, adapter или validation harness вне Python.

Python reference package включает convenience checker:

```bash
acs conformance validate --json
```

Эта команда является reference validation harness для bundled fixtures. Она
полезна для package и adapter development, но portable contract остаётся в JSON
records и schemas.

Fixtures:

- `fixtures/context_capsule.json`
- `fixtures/memory_record.json`
- `fixtures/capability_grant.json`
- `fixtures/evidence_ref.json`
- `fixtures/rule_manifest.json`
- `fixtures/skill_manifest.json`
- `fixtures/tool_binding.json`
- `fixtures/mcp_binding.json`
- `fixtures/audit_event.json`
- `fixtures/protected_ref.json`
- `fixtures/secret_record.json`
- `fixtures/sensitive_fact.json`
- `fixtures/memory_call.json`
- `fixtures/memory_operation.json`
- `fixtures/context_operation.json`
- `fixtures/memory_loop_run.json`
- `fixtures/tool_call_result.json`
- `fixtures/storage_selector.json`
- `fixtures/retrieval_query.json`
- `fixtures/retrieval_result.json`

Negative fixtures в `negative/` покрывают schema и semantic boundary failures,
которые adapters должны reject до projection в task context.
