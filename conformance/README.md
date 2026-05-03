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

Fixtures:

- `fixtures/context_capsule.json`
- `fixtures/memory_record.json`
- `fixtures/capability_grant.json`
- `fixtures/evidence_ref.json`
- `fixtures/memory_call.json`
- `fixtures/memory_operation.json`
- `fixtures/context_operation.json`
- `fixtures/memory_loop_run.json`
- `fixtures/tool_call_result.json`

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

Fixtures:

- `fixtures/context_capsule.json`
- `fixtures/memory_record.json`
- `fixtures/capability_grant.json`
- `fixtures/evidence_ref.json`
- `fixtures/memory_call.json`
- `fixtures/memory_operation.json`
- `fixtures/context_operation.json`
- `fixtures/memory_loop_run.json`
- `fixtures/tool_call_result.json`

Negative fixtures в `negative/` покрывают schema и semantic boundary failures,
которые adapters должны reject до projection в task context.
