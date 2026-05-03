# Roadmap / Дорожная карта

## EN
This roadmap keeps the OACS v0.1 draft standard small. Core work must define
memory, context, permissions, audit, and deterministic operation contracts.
Reference adapters prove integration, but they do not expand the standard.

### Current Position: v0.3.2a1 Reference POC
Core contract:

- Done: OACS v0.1 draft terminology, schemas, encrypted `MemoryRecord`,
  `ContextCapsule`, `CapabilityGrant`, `EvidenceRef`, `MemoryOperation`,
  `ContextOperation`, `MemoryLoopRun`, `memory_call`, and audit chain metadata.
- Done: `memory_calls` are backend-independent operation traces for intent
  classification, scoped memory query, structured evidence extraction, compact
  prompts, and operation metrics. Core memory loop does not synthesize final
  benchmark answers.
- Done: `memory_calls` are available in `MemoryLoopEngine`, CLI `loop run`, and
  API `/v1/loop/run` with intent, read trace, evidence, compact prompt, and
  deepening controls.
- Done: adaptive context policy added so tiny low-pressure tasks can use compact
  capsules, while structured evidence and medium/large contexts use
  `memory_calls`.
- Done: preferred execution path clarified: `oacs_memory_call_loop` is the
  practical benchmark/product-validation path; broad `oacs_memory_loop` remains
  a Context Capsule compatibility mode.
- Done: thin backend-neutral `StorageBackend` protocol added with SQLite kept as
  the reference backend.
- Done: capability-scoped shared memory added for subagents through
  `CapabilityGrant.scope`, `namespaces_allowed`, and `memory_depth_allowed`.

Reference adapters:

- Done: CLI/API, SQLite storage, retrieval providers, tools/skills/MCP bindings,
  validation fixtures, LM Studio reporting, and CI build checks exercise the
  contract without expanding conformance.
- Done: benchmark-specific parsing and scoring are outside the core
  memory-call loop. Synthetic tasks and public adapters attach structured
  evidence to `MemoryRecord.content`.
- Done: tool and skill adapter calls are capability-scoped through
  `tool.call`, `skill.run`, `tools_allowed`, `skills_allowed`, namespace, and
  scope checks.
- Done: MCP bindings remain metadata-first, with an optional stdio execution
  adapter guarded by tool capabilities and binding `allowed_tools`.
- Done: audit chain verification is exposed through CLI and API.
- Done: benchmark task packs use schema validation, explicit checksums, and
  no-network-by-default download/import commands.
- Done: benchmark comparisons report provider/model/task-pack compatibility and
  LM Studio usage metadata when the server returns it.
- Done: repo dogfood moved to the removable `repo_development_memory` skill
  under `examples/skills/`; it is source-checkout validation, not standard
  surface.
- Done: Agent Workflow UX added as reference CLI convenience:
  project-local discovery/status, resume aggregation, task checkpoints,
  governed command evidence, and deny-pattern policy helpers.
- Observed on `google/gemma-4-e2b`: medium/large/long memory tasks can improve
  token use and relevance through compact evidence projection; tiny tasks can
  show overhead.
- Current technical reports:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`,
  `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md`, and
  `examples/benchmarks/community_memory_gemma_e2b_2026-05-02.md`.

### v0.2.6 - Memory Standard Hardening
- Done: core `memory_calls` now produce operation traces, selected evidence, and
  compact prompts without synthesizing final benchmark answers.
- Done: generic loop/API metrics are named `operation_metrics`; benchmark
  scoring stays inside validation adapters.
- Done: `StorageBackend` no longer exposes SQL fragments; selectors are
  filters, order, and limit.
- Done: add `MemoryOperation` schema for observe, propose, commit, query, read,
  correct, forget, blur, and sharpen.
- Done: add `ContextOperation` and `MemoryLoopRun` schemas for context and loop traces.
- Done: add `memory_call` schema for OACS-native memory operation traces.
- Done: specify scope semantics: requested scope must be a subset of granted/resource
  scope; wildcard access requires explicit `*`.
- Done: specify audit requirements for memory read/query/write and context build/export.
- Done: add deterministic conformance tests for capability-safe memory operations.

### v0.2.7 - Context Capsule Integrity
- Done: add `context_capsule_export` envelope with checksum and HMAC integrity
  metadata. `integrity.signature` is a local HMAC tag, not a public-key digital
  signature or third-party-verifiable signing claim.
- Done: tighten capsule import/export validation and compatibility notes.
- Done: expand API tests for context export/import validation and audit behavior.

### v0.2.8 - Retrieval Adapter Contract
- Done: define a retrieval provider contract with policy-first filtering.
- Done: keep deterministic lexical retrieval as the required baseline.
- Done: define structured-evidence retrieval without benchmark-specific parsing.
- Done: treat embeddings as optional adapters: disabled by default, no network by
  default, and never part of core conformance.

### v0.3 - Integration Adapters
- Done: refine MCP binding model and add optional MCP client execution adapter.
- Done: extend namespace/scope-aware capability constraints from memory/context to
  tools and skills.
- Done: add audit chain verification commands.
- Done: add task pack import/download with schema and checksum validation.
- Done: add larger benchmark suites with real LM Studio mode reporting and native
  harness comparison where available.

### v0.3.1 - ToolBinding Execution Contract
- Done: normalize tool execution through one `ToolRunner` for
  `python_function`, `local_cli`, `http`, and `mcp` bindings.
- Done: validate tool inputs/outputs with declared JSON schemas when
  provided.
- Done: convert tool results into `EvidenceRef` records that can be
  audited and later projected into Context Capsules.
- Done: keep network-capable HTTP tools disabled unless the binding
  explicitly opts in.

### v0.3.2 - Agent Workflow UX

- Done: add project-local discovery for `.agent/oacs/oacs.db` and
  `.oacs/oacs.db`, plus `acs init --project` and `acs status`.
- Done: add `acs resume --scope ...` as an aggregate view over recent
  checkpoints, evidence, memory metadata, Context Capsules, and audit events.
- Done: add lightweight `acs checkpoint add/latest/list` backed by task traces.
- Done: add `acs run --label ... -- <cmd>` as a governed execution wrapper that
  records command output as `tool_result` evidence without becoming an
  orchestrator.
- Done: add project-local deny-pattern policy helpers and checks for memory,
  evidence, command evidence, and checkpoint capture.
- Done: keep all workflow UX outside OACS v0.1 draft core conformance.

### v1.0
- Freeze stable schemas for ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef, and
  AuditEvent.
- Define compatibility guarantees and migration policy.
- Provide backend, retrieval, and adapter-boundary conformance tests.
- Publish conformance fixtures for MemoryRecord, ContextCapsule,
  CapabilityGrant, EvidenceRef, memory_calls, and adapter boundaries.
- Keep public benchmark packs as optional validation artifacts.

## RU
Этот roadmap удерживает OACS v0.1 draft standard небольшим. Core work должен
определять memory, context, permissions, audit и deterministic operation
contracts. Reference adapters доказывают интеграцию, но не расширяют стандарт.

### Текущая позиция: v0.3.2a1 Reference POC
Core contract:

- Готово: OACS v0.1 draft terminology, schemas, encrypted `MemoryRecord`,
  `ContextCapsule`, `CapabilityGrant`, `EvidenceRef`, `MemoryOperation`,
  `ContextOperation`, `MemoryLoopRun`, `memory_call` и audit chain metadata.
- Готово: `memory_calls` являются backend-independent operation traces для
  intent classification, scoped memory query, structured evidence extraction,
  compact prompts и operation metrics. Core memory loop не синтезирует final
  benchmark answers.
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

Reference adapters:

- Готово: CLI/API, SQLite storage, retrieval providers, tools/skills/MCP
  bindings, validation fixtures, LM Studio reporting и CI build checks
  упражняют contract, не расширяя conformance.
- Готово: benchmark-specific parsing и scoring находятся вне core memory-call
  loop. Synthetic tasks и public adapters пишут structured evidence в
  `MemoryRecord.content`.
- Готово: вызовы tool и skill adapters ограничены capabilities через
  `tool.call`, `skill.run`, `tools_allowed`, `skills_allowed`, namespace и scope.
- Готово: MCP bindings остаются metadata-first, но добавлен optional stdio
  execution adapter с проверкой tool capabilities и binding `allowed_tools`.
- Готово: audit chain verification доступна через CLI и API.
- Готово: benchmark task packs используют schema validation, явные checksums и
  no-network-by-default download/import commands.
- Готово: benchmark comparisons показывают provider/model/task-pack
  compatibility и LM Studio usage metadata, когда сервер её возвращает.
- Готово: repo dogfood перенесён в отключаемый `repo_development_memory` skill
  в `examples/skills/`; это source-checkout validation, а не standard surface.
- Готово: Agent Workflow UX добавлен как reference CLI convenience:
  project-local discovery/status, resume aggregation, task checkpoints,
  governed command evidence и deny-pattern policy helpers.
- Наблюдение на `google/gemma-4-e2b`: medium/large/long memory tasks могут
  улучшать token use и relevance через compact evidence projection; tiny tasks
  могут показывать overhead.
- Текущие technical reports:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md` и
  `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md`.

### v0.2.6 - Memory Standard Hardening
- Готово: core `memory_calls` теперь создают operation traces, selected evidence
  и compact prompts без синтеза final benchmark answers.
- Готово: generic loop/API metrics называются `operation_metrics`; benchmark
  scoring остаётся внутри validation adapters.
- Готово: `StorageBackend` больше не раскрывает SQL fragments; selectors - это
  filters, order и limit.
- Готово: добавить `MemoryOperation` schema для observe, propose, commit, query, read,
  correct, forget, blur и sharpen.
- Готово: добавить `ContextOperation` и `MemoryLoopRun` schemas для context и loop traces.
- Готово: добавить `memory_call` schema для OACS-native traces операций памяти.
- Готово: зафиксировать scope semantics: requested scope должен быть subset of
  granted/resource scope; wildcard access требует явного `*`.
- Готово: зафиксировать audit requirements для memory read/query/write и context
  build/export.
- Готово: добавить deterministic conformance tests для capability-safe memory
  operations.

### v0.2.7 - Context Capsule Integrity
- Готово: добавить `context_capsule_export` envelope с checksum и HMAC integrity
  metadata. `integrity.signature` является local HMAC tag, а не public-key
  digital signature и не third-party-verifiable signing claim.
- Готово: усилить capsule import/export validation и compatibility notes.
- Готово: расширить API tests для context export/import validation и audit behavior.

### v0.2.8 - Retrieval Adapter Contract
- Готово: определить retrieval provider contract с policy-first filtering.
- Готово: оставить deterministic lexical retrieval обязательным baseline.
- Готово: определить structured-evidence retrieval без benchmark-specific parsing.
- Готово: считать embeddings optional adapters: disabled by default, no network by
  default и не часть core conformance.

### v0.3 - Integration Adapters
- Готово: уточнить MCP binding model и добавить optional MCP client execution adapter.
- Готово: расширить namespace/scope-aware capability constraints с memory/context на
  tools и skills.
- Готово: добавить команды проверки audit chain.
- Готово: добавить import/download task packs с schema и checksum validation.
- Готово: расширить benchmark suites с real LM Studio mode reporting и native harness
  comparison там, где он доступен.

### v0.3.1 - ToolBinding Execution Contract
- Готово: нормализовать tool execution через единый `ToolRunner` для
  `python_function`, `local_cli`, `http` и `mcp` bindings.
- Готово: валидировать tool inputs/outputs по объявленным JSON schemas, если
  они заданы.
- Готово: превращать tool results в `EvidenceRef` records, которые можно
  audit и позже включать в Context Capsules.
- Готово: HTTP tools с network доступом отключены, пока binding явно не
  разрешит это.

### v0.3.2 - Agent Workflow UX

- Готово: добавить project-local discovery для `.agent/oacs/oacs.db` и
  `.oacs/oacs.db`, плюс `acs init --project` и `acs status`.
- Готово: добавить `acs resume --scope ...` как aggregate view по recent
  checkpoints, evidence, memory metadata, Context Capsules и audit events.
- Готово: добавить lightweight `acs checkpoint add/latest/list` на базе task traces.
- Готово: добавить `acs run --label ... -- <cmd>` как governed execution wrapper,
  который записывает output команды как `tool_result` evidence, не становясь
  orchestrator.
- Готово: добавить project-local deny-pattern policy helpers и checks для
  memory, evidence, command evidence и checkpoint capture.
- Готово: оставить workflow UX вне OACS v0.1 draft core conformance.

### v1.0
- Заморозить stable schemas для ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef и
  AuditEvent.
- Зафиксировать compatibility guarantees и migration policy.
- Добавить backend, retrieval и adapter-boundary conformance tests.
- Опубликовать conformance fixtures для MemoryRecord, ContextCapsule,
  CapabilityGrant, EvidenceRef, memory_calls и adapter boundaries.
- Оставить public benchmark packs как optional validation artifacts.
