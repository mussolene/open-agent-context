# Roadmap / Дорожная карта

## EN
This roadmap tracks the OACS v0.1 draft standard and the Python reference
implementation.

### Current Position: v0.2.3 Reference POC, adaptive context policy
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
- Current technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2
- Add a storage backend protocol and keep SQLite as the reference backend.
- Add real embedding retrieval behind the memory search interface.
- Add stricter JSON-only output handling for LM Studio prompts.
- Add signed capsule export with verifiable checksum metadata.
- Expand API tests for all registry and audit routes.

### v0.3
- Add a real MCP client execution adapter.
- Add namespace/scope-aware capability constraints for tools and skills.
- Add audit chain verification commands.
- Add task pack import/download with schema and checksum validation.
- Add larger benchmark suites with real LM Studio mode reporting and native
  harness comparison where available.

### v1.0
- Freeze stable schemas for ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef, and
  AuditEvent.
- Define compatibility guarantees and migration policy.
- Provide backend conformance tests.
- Publish a reference benchmark pack and reproducibility report.

## RU
Этот roadmap отслеживает OACS v0.1 draft standard и Python reference
implementation.

### Текущая позиция: v0.2.3 Reference POC, adaptive context policy
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
- Текущий technical report:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### v0.2
- Добавить protocol для storage backend и оставить SQLite reference backend.
- Добавить real embedding retrieval за интерфейсом memory search.
- Усилить JSON-only output handling для LM Studio prompts.
- Добавить signed capsule export с проверяемой checksum metadata.
- Расширить API tests для всех registry и audit routes.

### v0.3
- Добавить настоящий MCP client execution adapter.
- Добавить namespace/scope-aware capability constraints для tools и skills.
- Добавить команды проверки audit chain.
- Добавить import/download task packs с schema и checksum validation.
- Расширить benchmark suites с real LM Studio mode reporting и native harness
  comparison там, где он доступен.

### v1.0
- Заморозить stable schemas для ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef и
  AuditEvent.
- Зафиксировать compatibility guarantees и migration policy.
- Добавить backend conformance tests.
- Опубликовать reference benchmark pack и reproducibility report.
