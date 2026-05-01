# Roadmap / Дорожная карта

## EN
This roadmap keeps the OACS v0.1 draft standard small. Core work must define
memory, context, permissions, audit, and deterministic operation contracts.
Reference adapters prove integration, but they do not expand the standard.

### Current Position: v0.2.5 Reference POC, scoped subagent memory
- Done: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, basic memory loop,
  memory_calls, and public benchmark adapters.
- Done: `oacs_memory_call_loop` dogfoods OACS as a deterministic memory-call
  layer under benchmark execution: intent classification, scoped memory query,
  structured evidence extraction, compact prompt, and token/evidence metrics.
- Proven on `google/gemma-4-e2b`: medium/large/long memory tasks improve token
  use and relevance through compact evidence projection; tiny tasks still show
  overhead.
- Done: benchmark-specific text parsing is outside the core memory-call loop.
  Synthetic tasks and public adapters attach structured evidence to
  `MemoryRecord.content`.
- Done: domain-shaped evidence selection is isolated behind pluggable selectors;
  the core memory-call loop now records calls and builds projections only.
- Done: benchmark execution now uses explicit `memory_calls` instead of
  backend-dependent `tool_calls` or hidden parser heuristics. The benchmark mode
  is `oacs_memory_call_loop`.
- Done: README quickstart was reduced to the minimal local path and validated
  against a clean temporary SQLite store.
- Done: CI build pipeline added for lint, typecheck, tests, package build,
  wheel install, and CLI smoke checks.
- Done: repo dogfood commands added for capturing development episodes and
  building repo-scoped context capsules.
- Done: `memory_calls` promoted into general `MemoryLoopEngine`, CLI `loop run`,
  and API `/v1/loop/run` with intent, read trace, evidence, compact prompt, and
  deepening controls.
- Done: adaptive context policy added so tiny low-pressure tasks can use compact
  capsules, while structured evidence and medium/large contexts use
  `memory_calls`.
- Done: thin `StorageBackend` protocol added with SQLite kept as the reference
  backend.
- Done: capability-scoped shared memory added for subagents through
  `CapabilityGrant.scope`, `namespaces_allowed`, and `memory_depth_allowed`.
- Current technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2.6 - Memory Standard Hardening
- Add `MemoryOperation` schema for observe, propose, commit, query, read,
  correct, forget, blur, and sharpen.
- Add `memory_call` schema for OACS-native memory operation traces.
- Specify scope semantics: requested scope must be a subset of granted/resource
  scope; wildcard access requires explicit `*`.
- Specify audit requirements for memory read/query/write and context build/export.
- Add deterministic conformance tests for capability-safe memory operations.

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

### Текущая позиция: v0.2.5 Reference POC, scoped subagent memory
- Готово: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, базовый memory
  loop, memory_calls и public benchmark adapters.
- Готово: `oacs_memory_call_loop` использует OACS под капотом benchmark
  execution как deterministic memory-call layer: intent classification, scoped
  memory query, structured evidence extraction, compact prompt и
  token/evidence metrics.
- Доказано на `google/gemma-4-e2b`: medium/large/long memory tasks улучшают
  token use и relevance через compact evidence projection; tiny tasks всё ещё
  показывают overhead.
- Готово: benchmark-specific text parsing находится вне core memory-call loop.
  Synthetic tasks и public adapters пишут structured evidence в
  `MemoryRecord.content`.
- Готово: domain-shaped evidence selection изолирован за pluggable selectors;
  core memory-call loop только записывает calls и строит projections.
- Готово: benchmark execution теперь использует явные `memory_calls` вместо
  backend-dependent `tool_calls` или скрытых parser heuristics. Benchmark mode:
  `oacs_memory_call_loop`.
- Готово: README quickstart сокращён до минимального local path и проверен на
  чистом temporary SQLite store.
- Готово: добавлена CI build pipeline для lint, typecheck, tests, package build,
  wheel install и CLI smoke checks.
- Готово: добавлены repo dogfood commands для capture development episodes и
  repo-scoped context capsules.
- Готово: `memory_calls` перенесены в общий `MemoryLoopEngine`, CLI `loop run`
  и API `/v1/loop/run` с intent, read trace, evidence, compact prompt и
  deepening controls.
- Готово: добавлена adaptive context policy: tiny low-pressure tasks могут
  использовать compact capsules, а structured evidence и medium/large contexts
  используют `memory_calls`.
- Готово: добавлен тонкий `StorageBackend` protocol, SQLite остаётся reference
  backend.
- Готово: capability-scoped shared memory добавлена для subagents через
  `CapabilityGrant.scope`, `namespaces_allowed` и `memory_depth_allowed`.
- Текущий technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2.6 - Memory Standard Hardening
- Добавить `MemoryOperation` schema для observe, propose, commit, query, read,
  correct, forget, blur и sharpen.
- Добавить `memory_call` schema для OACS-native traces операций памяти.
- Зафиксировать scope semantics: requested scope должен быть subset of
  granted/resource scope; wildcard access требует явного `*`.
- Зафиксировать audit requirements для memory read/query/write и context
  build/export.
- Добавить deterministic conformance tests для capability-safe memory
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
