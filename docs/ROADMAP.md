# Roadmap / Дорожная карта

## EN
This roadmap keeps the OACS v1.0 standard small. Core work must define
memory, context, permissions, audit, and deterministic operation contracts.
Reference adapters prove integration, but they do not expand the standard.

### Current Position: v1.0 Released / Post-1.0 Hardening
Core contract:

- Done: OACS v1.0 terminology, schemas, encrypted `MemoryRecord`,
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
- Done: protected values boundary added for external secrets and non-public
  infrastructure facts through `ProtectedRef`. OACS is not a vault; secret
  storage, rotation, and plaintext resolution stay in external vault adapters.
- Done: v1.0 freeze prep tracks schema stability, migration policy, and
  conformance boundary coverage in `docs/COMPATIBILITY.md`,
  `docs/FREEZE_PREP.md`, and `conformance/README.md`.
- Done: stable-candidate schemas reject unknown top-level fields and carry
  portable field descriptions so implementers can distinguish standard
  semantics from reference adapter behavior.
- Done: v1.0.0 is tagged, published to PyPI, smoke-tested from a fresh install,
  and recorded with OACS release evidence.

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
- Done: repo dogfood moved to the removable `codex_oacs_runtime` skill
  under `examples/skills/`; it is source-checkout validation, not standard
  surface.
- Done: Agent Workflow UX added as reference CLI convenience:
  project-local discovery/status, resume aggregation, task checkpoints,
  governed command evidence, and deny-pattern policy helpers.
- Done: CLI release smoke UX includes `acs --version` / `acs -V`.
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
- Done: keep all workflow UX outside OACS v1.0 core conformance.

### v0.3.3 - Multi-Implementation Conformance

- Done: separate the standard contract from the Python package more
  explicitly in docs, fixtures, and conformance language. Python remains the
  reference implementation, not the only supported implementation strategy.
- Done: publish language-neutral JSON examples for ContextCapsule,
  MemoryRecord, CapabilityGrant, EvidenceRef, memory_call, and ToolCallResult.
- Done: add conformance fixtures that another runtime can validate without
  importing `oacs` Python modules or depending on SQLite.
- Done: define a small interoperability checklist for adapters that produce
  or consume OACS records through CLI/API, files, or native SDKs.
- Done: mark Python-specific behavior, storage choices, and convenience
  commands as reference behavior unless the schema/spec explicitly promotes them
  to core contract.
- Done: add positive operation-envelope fixtures and negative adapter-boundary
  fixtures for schema and semantic rejection checks.

### v0.3.4 - Conformance Freeze Prep

- Done: add language-neutral conformance fixtures for `RuleManifest`,
  `SkillManifest`, `ToolBinding`, `McpBinding`, and `AuditEvent`.
- Done: tighten manifest, binding, and audit event schemas with explicit
  status/risk enums, additional-property rejection, and reference-runtime
  extension fields where the Python implementation already emits them.
- Done: add negative adapter-boundary fixtures for audit hash mismatch,
  capability depth overflow, implicit wildcard scope/namespace grants, and HTTP
  tool bindings without explicit network opt-in.
- Done: extend the reference conformance checker so semantic rejection examples
  cover checksum, audit hash, D3-D5 factual projection, evidence linkage,
  explicit wildcard semantics, and HTTP adapter opt-in.
- Done: keep these fixtures language-neutral; Python, SQLite, CLI/API, MCP
  stdio execution, LM Studio, benchmarks, and repo dogfood remain reference
  implementation choices unless promoted by schemas/spec.

### v0.3.5 - Protected Values and Vault Boundary

- Done: define language-neutral `ProtectedRef` schema for references to
  external passwords, tokens, private keys, internal IPs, private hostnames,
  private URLs, topology, and other non-public values.
- Done: add conformance fixture for redacted protected references without
  storing ciphertext or vault state in OACS.
- Done: add negative conformance fixtures rejecting plaintext protected values
  in Context Capsules, ToolCallResult output, EvidenceRef public payloads, and
  AuditEvent metadata.
- Done: keep Python/SQLite vault storage, rotation, revocation, and plaintext
  release out of the `acs` reference implementation; use external vaults such
  as 1Password, HashiCorp Vault, cloud secret managers, SOPS, or OS keychains.
- Done: describe `protected.use`, `protected.read`, and `secret.read` as
  capability semantics for external vault adapters.

### v1.0 Freeze Prep

- Done: add `docs/FREEZE_PREP.md` as the per-schema freeze manifest for stable
  candidates, draft support schemas, and reference-only schemas.
- Done: stable-candidate schemas have strict top-level shape, portable field
  descriptions, and docs tests that block description or strictness drift.
- Done: semantic negative fixtures cover stable-candidate adapter-boundary
  rules that cannot be expressed fully as JSON Schema constraints.
- Done: `actor` and `context_capsule_export` remain draft support for v1.0;
  stable records reference actor IDs, and raw ContextCapsule JSON remains the
  portable context record.
- Done: define compatibility and migration rules for schema changes,
  semantic checks, and adapter-boundary behavior.
- Done: make the conformance boundary explicit: positive fixtures are
  portable examples, negative fixtures are required rejection examples, and
  Python `acs conformance validate` remains a reference checker.
- Done: decide which draft support schemas, if any, are promoted into the v1.0
  stable set; no draft support schemas are promoted for v1.0 freeze prep.
- Done: publish `docs/V1_RELEASE_CHECKLIST.md`, the final v1.0 release checklist
  that verifies schemas, fixtures, package artifacts, published-package smoke
  tests, secret scans, and OACS proof.

### v1.0
- Done: freeze stable schemas for `ContextCapsule`, `MemoryRecord`,
  `CapabilityGrant`, `RuleManifest`, `SkillManifest`, `ToolBinding`,
  `McpBinding`, `EvidenceRef`, `AuditEvent`, `ProtectedRef`,
  `MemoryOperation`, `ContextOperation`, `memory_call`, `MemoryLoopRun`,
  `ToolCallResult`, `StorageSelector`, `RetrievalQuery`, and
  `RetrievalResult`.
- Done: define compatibility guarantees and migration policy for stable schemas,
  semantic checks, checksum/hash behavior, and adapter-boundary rejection
  examples.
- Done: provide backend, retrieval, protected-ref, and adapter-boundary conformance
  tests without requiring SQLite, Python, LM Studio, hosted APIs, or MCP stdio
  execution.
- Done: publish conformance fixtures for memory/context records, permissions,
  manifests, bindings, evidence, audit, protected refs, operation envelopes,
  retrieval/storage selectors, and negative boundary cases.
- Done: keep public benchmark packs as optional validation artifacts.

### v1.0.x - Post-Release Hardening
- Done: publish a GitHub Release entry for `v1.0.0` in addition to the PyPI
  package publication.
- Done: remove CI/release workflow dependency on Node.js 20 artifact actions by
  building distributions inside the selected trusted-publishing job.
- Keep changes patch-safe: docs drift, release automation, conformance
  clarification, and bug fixes that do not change stable schema semantics.
- Add implementation-neutral guidance where needed so new runtimes can treat the
  Python package as a reference implementation rather than the standard itself.
- Track non-breaking conformance fixture additions separately from schema or
  semantic changes that require a new draft/stable version.

## RU
Этот roadmap удерживает OACS v1.0 standard небольшим. Core work должен
определять memory, context, permissions, audit и deterministic operation
contracts. Reference adapters доказывают интеграцию, но не расширяют стандарт.

### Текущая позиция: v1.0 Released / Post-1.0 Hardening
Core contract:

- Готово: OACS v1.0 terminology, schemas, encrypted `MemoryRecord`,
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
- Готово: добавлена protected values boundary для external secrets и
  непубличных infrastructure facts через `ProtectedRef`. OACS не является
  vault; secret storage, rotation и plaintext resolution остаются во внешних
  vault adapters.
- Готово: v1.0 freeze prep отслеживает schema stability, migration policy и
  conformance boundary coverage в `docs/COMPATIBILITY.md`,
  `docs/FREEZE_PREP.md` и `conformance/README.md`.
- Готово: stable-candidate schemas отвергают unknown top-level fields и имеют
  portable field descriptions, чтобы implementers отличали standard semantics
  от reference adapter behavior.
- Готово: v1.0.0 помечен tag, опубликован в PyPI, проверен fresh install smoke
  test и записан с OACS release evidence.

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
- Готово: repo dogfood перенесён в отключаемый `codex_oacs_runtime` skill
  в `examples/skills/`; это source-checkout validation, а не standard surface.
- Готово: Agent Workflow UX добавлен как reference CLI convenience:
  project-local discovery/status, resume aggregation, task checkpoints,
  governed command evidence и deny-pattern policy helpers.
- Готово: CLI release smoke UX включает `acs --version` / `acs -V`.
- Наблюдение на `google/gemma-4-e2b`: medium/large/long memory tasks могут
  улучшать token use и relevance через compact evidence projection; tiny tasks
  могут показывать overhead.
- Текущие technical reports:
  `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`,
  `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md` и
  `examples/benchmarks/community_memory_gemma_e2b_2026-05-02.md`.

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
- Готово: оставить workflow UX вне OACS v1.0 core conformance.

### v0.3.3 - Multi-Implementation Conformance

- Готово: ещё явнее отделить standard contract от Python package в docs,
  fixtures и conformance language. Python остаётся reference implementation, а
  не единственным поддерживаемым способом реализации.
- Готово: опубликовать language-neutral JSON examples для
  ContextCapsule, MemoryRecord, CapabilityGrant, EvidenceRef, memory_call и
  ToolCallResult.
- Готово: добавить conformance fixtures, которые другой runtime сможет
  валидировать без import `oacs` Python modules и без зависимости от SQLite.
- Готово: описать короткий interoperability checklist для adapters,
  которые produce или consume OACS records через CLI/API, files или native SDKs.
- Готово: помечать Python-specific behavior, storage choices и
  convenience commands как reference behavior, если schema/spec явно не
  повышает их до core contract.
- Готово: добавить positive operation-envelope fixtures и negative
  adapter-boundary fixtures для schema и semantic rejection checks.

### v0.3.4 - Conformance Freeze Prep

- Готово: добавить language-neutral conformance fixtures для `RuleManifest`,
  `SkillManifest`, `ToolBinding`, `McpBinding` и `AuditEvent`.
- Готово: усилить manifest, binding и audit event schemas через explicit
  status/risk enums, rejection лишних полей и reference-runtime extension
  fields там, где Python implementation уже их пишет.
- Готово: добавить negative adapter-boundary fixtures для audit hash mismatch,
  capability depth overflow, implicit wildcard scope/namespace grants и HTTP
  tool bindings без explicit network opt-in.
- Готово: расширить reference conformance checker: semantic rejection examples
  покрывают checksum, audit hash, D3-D5 factual projection, evidence linkage,
  explicit wildcard semantics и HTTP adapter opt-in.
- Готово: сохранить fixtures language-neutral; Python, SQLite, CLI/API, MCP
  stdio execution, LM Studio, benchmarks и repo dogfood остаются choices
  reference implementation, если schemas/spec не продвигают их в core.

### v0.3.5 - Protected Values and Vault Boundary

- Готово: определить language-neutral schema `ProtectedRef` для references на
  external passwords, tokens, private keys, internal IPs, private hostnames,
  private URLs, topology и другие непубличные values.
- Готово: добавить conformance fixture для redacted protected references без
  хранения ciphertext или vault state в OACS.
- Готово: добавить negative conformance fixtures, которые reject plaintext
  protected values в Context Capsules, ToolCallResult output, EvidenceRef public
  payloads и AuditEvent metadata.
- Готово: оставить Python/SQLite vault storage, rotation, revocation и plaintext
  release вне `acs` reference implementation; использовать внешние vaults:
  1Password, HashiCorp Vault, cloud secret managers, SOPS или OS keychains.
- Готово: описать `protected.use`, `protected.read` и `secret.read` как
  capability semantics для external vault adapters.

### v1.0 Freeze Prep

- Готово: добавить `docs/FREEZE_PREP.md` как per-schema freeze manifest для
  stable candidates, draft support schemas и reference-only schemas.
- Готово: stable-candidate schemas имеют strict top-level shape, portable field
  descriptions и docs tests, которые блокируют description или strictness drift.
- Готово: semantic negative fixtures покрывают stable-candidate
  adapter-boundary rules, которые нельзя полностью выразить JSON Schema
  constraints.
- Готово: `actor` и `context_capsule_export` остаются draft support для v1.0;
  stable records ссылаются на actor IDs, а raw ContextCapsule JSON остаётся
  portable context record.
- Готово: определить compatibility и migration rules для schema changes,
  semantic checks и adapter-boundary behavior.
- Готово: сделать conformance boundary явной: positive fixtures являются
  portable examples, negative fixtures являются required rejection examples, а
  Python `acs conformance validate` остаётся reference checker.
- Готово: решить, какие draft support schemas, если такие есть, продвигаются в
  stable set v1.0; для v1.0 freeze prep draft support schemas не продвигаются.
- Готово: опубликовать `docs/V1_RELEASE_CHECKLIST.md`, финальный v1.0 release
  checklist, который проверяет schemas, fixtures, package artifacts,
  published-package smoke tests, secret scans и OACS proof.

### v1.0
- Готово: заморозить stable schemas для `ContextCapsule`, `MemoryRecord`,
  `CapabilityGrant`, `RuleManifest`, `SkillManifest`, `ToolBinding`,
  `McpBinding`, `EvidenceRef`, `AuditEvent`, `ProtectedRef`,
  `MemoryOperation`, `ContextOperation`, `memory_call`, `MemoryLoopRun`,
  `ToolCallResult`, `StorageSelector`, `RetrievalQuery` и `RetrievalResult`.
- Готово: зафиксировать compatibility guarantees и migration policy для stable schemas,
  semantic checks, checksum/hash behavior и adapter-boundary rejection examples.
- Готово: добавить backend, retrieval, protected-ref и adapter-boundary conformance tests
  без требования SQLite, Python, LM Studio, hosted APIs или MCP stdio execution.
- Готово: опубликовать conformance fixtures для memory/context records, permissions,
  manifests, bindings, evidence, audit, protected refs, operation envelopes,
  retrieval/storage selectors и negative boundary cases.
- Готово: оставить public benchmark packs как optional validation artifacts.

### v1.0.x - Post-Release Hardening
- Готово: опубликовать GitHub Release entry для `v1.0.0` дополнительно к PyPI
  package publication.
- Готово: убрать dependency CI/release workflow от Node.js 20 artifact actions,
  собирая distributions внутри selected trusted-publishing job.
- Держать изменения patch-safe: docs drift, release automation, conformance
  clarification и bug fixes, которые не меняют stable schema semantics.
- Добавлять implementation-neutral guidance, когда нужно, чтобы новые runtimes
  рассматривали Python package как reference implementation, а не сам standard.
- Отслеживать non-breaking conformance fixture additions отдельно от schema или
  semantic changes, требующих новую draft/stable version.
