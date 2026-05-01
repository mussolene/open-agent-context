# Roadmap / Дорожная карта

## EN
This roadmap keeps the OACS v0.1 draft standard small. Core work must define
memory, context, permissions, audit, and deterministic operation contracts.
Reference adapters prove integration, but they do not expand the standard.

### Current Position: v0.2.6 Reference POC, memory/context hardening
- Done: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, basic memory loop,
  memory_calls, validation adapters, and CI build checks.
- Done: `memory_calls` are backend-independent operation traces for intent
  classification, scoped memory query, structured evidence extraction, compact
  prompts, and operation metrics. Core memory loop does not synthesize final
  benchmark answers.
- Observed on `google/gemma-4-e2b`: medium/large/long memory tasks can improve
  token use and relevance through compact evidence projection; tiny tasks can
  show overhead.
- Done: benchmark-specific text parsing is outside the core memory-call loop.
  Synthetic tasks and public adapters attach structured evidence to
  `MemoryRecord.content`.
- Done: domain-shaped evidence selection is isolated behind pluggable selectors;
  the core memory-call loop now records calls and builds projections only.
- Done: benchmark execution uses explicit `memory_calls` instead of
  backend-dependent `tool_calls` or hidden parser heuristics, but scoring stays
  in validation adapters.
- Done: README quickstart is the minimal local path: commit memory, query it,
  and build an explainable Context Capsule.
- Done: CI build pipeline added for lint, typecheck, tests, package build,
  wheel install, and CLI smoke checks.
- Done: optional repo dogfood commands use ordinary OACS memory/context
  operations and are not part of the standard surface.
- Done: `memory_calls` are available in `MemoryLoopEngine`, CLI `loop run`, and
  API `/v1/loop/run` with intent, read trace, evidence, compact prompt, and
  deepening controls.
- Done: adaptive context policy added so tiny low-pressure tasks can use compact
  capsules, while structured evidence and medium/large contexts use
  `memory_calls`.
- Done: thin backend-neutral `StorageBackend` protocol added with SQLite kept as
  the reference backend.
- Done: capability-scoped shared memory added for subagents through
  `CapabilityGrant.scope`, `namespaces_allowed`, and `memory_depth_allowed`.
- Current technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2.6 - Memory Standard Hardening
- Done: core `memory_calls` now produce operation traces, selected evidence, and
  compact prompts without synthesizing final benchmark answers.
- Done: generic loop/API metrics are named `operation_metrics`; benchmark
  scoring stays inside validation adapters.
- Done: `StorageBackend` no longer exposes SQL fragments; selectors are
  filters, order, and limit.
- Remaining: add `MemoryOperation` schema for observe, propose, commit, query, read,
  correct, forget, blur, and sharpen.
- Remaining: add `memory_call` schema for OACS-native memory operation traces.
- Remaining: specify scope semantics: requested scope must be a subset of granted/resource
  scope; wildcard access requires explicit `*`.
- Remaining: specify audit requirements for memory read/query/write and context build/export.
- Remaining: add deterministic conformance tests for capability-safe memory operations.

### v0.2.7 - Context Capsule Integrity
- Add signed capsule export with verifiable checksum metadata.
- Tighten capsule import/export validation and compatibility notes.
- Expand API tests for context, registry, and audit routes.

### v0.2.8 - Retrieval Adapter Contract
- Define a retrieval provider contract with policy-first filtering.
- Keep deterministic lexical retrieval as the required baseline.
- Define structured-evidence retrieval without benchmark-specific parsing.
- Treat embeddings as optional adapters: disabled by default, no network by
  default, and never part of core conformance.

### v0.3 - Integration Adapters
- Refine MCP binding model and add optional MCP client execution adapter.
- Extend namespace/scope-aware capability constraints from memory/context to
  tools and skills.
- Add audit chain verification commands.
- Add task pack import/download with schema and checksum validation.
- Add larger benchmark suites with real LM Studio mode reporting and native
  harness comparison where available.

### v1.0
- Freeze stable schemas for ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef, and
  AuditEvent.
- Define compatibility guarantees and migration policy.
- Provide backend and retrieval conformance tests.
- Publish a reference benchmark pack and reproducibility report.

## RU
Этот roadmap удерживает OACS v0.1 draft standard небольшим. Core work должен
определять memory, context, permissions, audit и deterministic operation
contracts. Reference adapters доказывают интеграцию, но не расширяют стандарт.

### Текущая позиция: v0.2.6 Reference POC, memory/context hardening
- Готово: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, базовый memory
  loop, memory_calls, validation adapters и CI build checks.
- Готово: `memory_calls` являются backend-independent operation traces для
  intent classification, scoped memory query, structured evidence extraction,
  compact prompts и operation metrics. Core memory loop не синтезирует final
  benchmark answers.
- Наблюдение на `google/gemma-4-e2b`: medium/large/long memory tasks могут
  улучшать token use и relevance через compact evidence projection; tiny tasks
  могут показывать overhead.
- Готово: benchmark-specific text parsing находится вне core memory-call loop.
  Synthetic tasks и public adapters пишут structured evidence в
  `MemoryRecord.content`.
- Готово: domain-shaped evidence selection изолирован за pluggable selectors;
  core memory-call loop только записывает calls и строит projections.
- Готово: benchmark execution использует явные `memory_calls` вместо
  backend-dependent `tool_calls` или скрытых parser heuristics, но scoring
  остаётся в validation adapters.
- Готово: README quickstart является minimal local path: commit memory, query it
  и build explainable Context Capsule.
- Готово: добавлена CI build pipeline для lint, typecheck, tests, package build,
  wheel install и CLI smoke checks.
- Готово: optional repo dogfood commands используют ordinary OACS memory/context
  operations и не являются standard surface.
- Готово: `memory_calls` доступны в `MemoryLoopEngine`, CLI `loop run` и API
  `/v1/loop/run` с intent, read trace, evidence, compact prompt и deepening
  controls.
- Готово: добавлена adaptive context policy: tiny low-pressure tasks могут
  использовать compact capsules, а structured evidence и medium/large contexts
  используют `memory_calls`.
- Готово: добавлен тонкий backend-neutral `StorageBackend` protocol, SQLite
  остаётся reference backend.
- Готово: capability-scoped shared memory добавлена для subagents через
  `CapabilityGrant.scope`, `namespaces_allowed` и `memory_depth_allowed`.
- Текущий technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2.6 - Memory Standard Hardening
- Готово: core `memory_calls` теперь создают operation traces, selected evidence
  и compact prompts без синтеза final benchmark answers.
- Готово: generic loop/API metrics называются `operation_metrics`; benchmark
  scoring остаётся внутри validation adapters.
- Готово: `StorageBackend` больше не раскрывает SQL fragments; selectors - это
  filters, order и limit.
- Осталось: добавить `MemoryOperation` schema для observe, propose, commit, query, read,
  correct, forget, blur и sharpen.
- Осталось: добавить `memory_call` schema для OACS-native traces операций памяти.
- Осталось: зафиксировать scope semantics: requested scope должен быть subset of
  granted/resource scope; wildcard access требует явного `*`.
- Осталось: зафиксировать audit requirements для memory read/query/write и context
  build/export.
- Осталось: добавить deterministic conformance tests для capability-safe memory
  operations.

### v0.2.7 - Context Capsule Integrity
- Добавить signed capsule export с проверяемой checksum metadata.
- Усилить capsule import/export validation и compatibility notes.
- Расширить API tests для context, registry и audit routes.

### v0.2.8 - Retrieval Adapter Contract
- Определить retrieval provider contract с policy-first filtering.
- Оставить deterministic lexical retrieval обязательным baseline.
- Определить structured-evidence retrieval без benchmark-specific parsing.
- Считать embeddings optional adapters: disabled by default, no network by
  default и не часть core conformance.

### v0.3 - Integration Adapters
- Уточнить MCP binding model и добавить optional MCP client execution adapter.
- Расширить namespace/scope-aware capability constraints с memory/context на
  tools и skills.
- Добавить команды проверки audit chain.
- Добавить import/download task packs с schema и checksum validation.
- Расширить benchmark suites с real LM Studio mode reporting и native harness
  comparison там, где он доступен.

### v1.0
- Заморозить stable schemas для ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef и
  AuditEvent.
- Зафиксировать compatibility guarantees и migration policy.
- Добавить backend и retrieval conformance tests.
- Опубликовать reference benchmark pack и reproducibility report.
