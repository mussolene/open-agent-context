# OACS v1.0 Specification / Спецификация OACS v1.0

## EN
OACS v1.0 defines a deterministic lower layer for agent context. A model receives a
Context Capsule assembled from task intent, scope, memory, rules, skills, tools,
evidence, permissions, and explicit forbidden assumptions.

OACS is not an agent framework, model backend, vector database, benchmark
harness, or replacement for MCP. It is the memory/context contract that those
systems can call before they invoke a model, tool, or external service.

Core records: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, ProtectedRef, TaskTrace, ExperienceTrace,
MemoryLoopRun.

Reference implementation note: OACS v1.0 allows `MemoryRecord.content` to
carry structured evidence items. This is not a new standard entity; it is the
current compatibility path for turning external traces into evidence-backed
memory without teaching the generic memory loop source-specific text formats.

Reference implementation v1.0 includes `memory_calls` as a backend-independent
operation trace for memory work in MemoryLoopEngine, CLI, API, and validation
adapters. `memory_calls` query, read, extract evidence, audit, and build compact
model prompts; they do not replace the model or synthesize final answers in the
core standard layer. Native model `tool_calls` may be used by a future adapter,
but OACS does not require backend tool-calling support. Storage is accessed
through a thin backend-neutral `StorageBackend` protocol, with SQLite as the
reference backend. Subagent shared memory is represented by ordinary scoped
`CapabilityGrant` records over ordinary scoped `MemoryRecord` records.

Integration adapters keep the standard boundary explicit. `tool.call` and
`skill.run` require capability grants, tool/skill allowlists, namespace checks,
and scope checks. MCP bindings are metadata-first; optional stdio execution is a
reference adapter behavior, not an OACS conformance requirement.

`ToolBinding` execution produces a `ToolCallResult` envelope. The reference
implementation records tool outputs as `tool_result` `EvidenceRef` records, so
later context assembly can cite tool evidence without treating tool stdout as
uncontrolled memory.

This document is the v1.0 standard contract. The Python package in this
repository is the reference implementation for the standard.
Other runtimes can implement OACS by emitting and accepting the JSON records in
`schemas/`, validating the conformance fixtures in `conformance/fixtures/`, and
following the checklist in `docs/INTEROPERABILITY.md`.

Operations are JSON-first and auditable. Memory writes are explicit:
`observe`, `propose`, and `commit` are separate operations. Fuzzy memories
at D3-D5 are hypotheses, not facts.

v1.0 includes operation envelopes for `MemoryOperation`, `ContextOperation`,
`memory_call`, and `MemoryLoopRun` plus conformance fixtures for
`RuleManifest`, `SkillManifest`, `ToolBinding`, `McpBinding`, and `AuditEvent`.
Operation envelopes are metadata contracts: they record actor, scope, status,
arguments, result metadata, and audit references without requiring plaintext
memory content.

Protected values are not ordinary memory and OACS is not a vault.
`ProtectedRef` is the portable reference projected into context, tool bindings,
evidence, or audit metadata. Secret storage, rotation, revocation, and plaintext
resolution belong to external vaults or runtime adapters. `protected.use`
allows adapter use without revealing plaintext through OACS records, while
`protected.read` and `secret.read` describe explicit plaintext disclosure by an
external vault adapter and should be narrowly granted. Context Capsules,
ToolCallResult, EvidenceRef public payloads, and AuditEvent metadata must not
persist plaintext protected values.

Scope semantics are strict. A requested operation scope must be a subset of both
the grant scope and the resource scope. Empty grant scope matches only an empty
requested scope. Broad access requires an explicit `*` in the grant. Namespace
and memory depth limits are checked before content is decrypted for non-bootstrap
actors.

Retrieval is pluggable but policy-bound. Providers receive only memories that
already passed capability, scope, namespace, depth, lifecycle, and status
filtering. The required baseline is deterministic lexical retrieval with
structured evidence retrieval over `MemoryContent.evidence`. Embeddings may be
implemented by explicit adapters, but they are disabled by default, require no
network for conformance, and are not required for OACS conformance.

Python-specific behavior is reference-only unless this specification or a JSON
Schema says otherwise. The `acs` CLI, FastAPI routes, SQLite backend, local
passphrase key provider, local CLI execution, HTTP execution, LM Studio support,
benchmark runners, and repo dogfood workflow are validation and integration
surfaces around the standard contract, not mandatory runtime features.

## RU
OACS v1.0 задаёт детерминированный нижний слой агентского контекста. Модель получает
Context Capsule, собранную из задачи, намерения, области видимости, памяти,
правил, skills, tools, evidence, разрешений и явно запрещённых предположений.

OACS не является agent framework, model backend, vector database, benchmark
harness или заменой MCP. Это memory/context contract, который такие системы
могут вызывать до обращения к модели, tool или внешнему сервису.

Основные записи: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, ProtectedRef, TaskTrace, ExperienceTrace,
MemoryLoopRun.

Примечание reference implementation: OACS v1.0 допускает structured
evidence items внутри `MemoryRecord.content`. Это не новая сущность стандарта, а
текущий compatibility path для преобразования внешних traces в evidence-backed
memory без обучения generic memory loop source-specific text formats.

Reference implementation v1.0 включает `memory_calls` как backend-independent
operation trace для работы с памятью в MemoryLoopEngine, CLI, API и validation
adapters. `memory_calls` выполняют query, read, evidence extraction, audit и
строят compact model prompts; они не заменяют модель и не синтезируют final
answers в core standard layer. Native model `tool_calls` может использоваться
будущим adapter, но OACS не требует backend tool-calling support. Storage
доступен через тонкий backend-neutral `StorageBackend` protocol, SQLite остаётся
reference backend. Shared memory для subagents представлена обычными scoped
`CapabilityGrant` поверх обычных scoped `MemoryRecord`.

Integration adapters сохраняют явную границу стандарта. `tool.call` и
`skill.run` требуют capability grants, allowlists для tools/skills, namespace
checks и scope checks. MCP bindings остаются metadata-first; optional stdio
execution является behavior reference adapter, а не OACS conformance
requirement.

Execution `ToolBinding` создаёт envelope `ToolCallResult`. Reference
implementation записывает tool outputs как `tool_result` `EvidenceRef`, чтобы
последующая сборка контекста могла ссылаться на evidence от tools без
превращения stdout в uncontrolled memory.

Этот документ является v1.0 contract стандарта. Python package в этом
репозитории — reference implementation для стандарта.
Другие runtimes могут реализовать OACS, если emit и accept JSON records из
`schemas/`, валидируют conformance fixtures из `conformance/fixtures/` и
следуют checklist в `docs/INTEROPERABILITY.md`.

Операции ориентированы на JSON и аудит. Запись памяти явная:
`observe`, `propose` и `commit` разделены. Размытая память D3-D5 является
гипотезой, а не фактом.

v1.0 включает operation envelopes для `MemoryOperation`, `ContextOperation`,
`memory_call` и `MemoryLoopRun`, а также conformance fixtures для
`RuleManifest`, `SkillManifest`, `ToolBinding`, `McpBinding` и `AuditEvent`.
Operation envelopes являются metadata contracts: они записывают actor, scope,
status, arguments, result metadata и audit references без требования раскрывать
plaintext memory content.

Protected values не являются обычной memory, и OACS не является vault.
`ProtectedRef` является portable reference, которая проецируется в context, tool
bindings, evidence или audit metadata. Secret storage, rotation, revocation и
plaintext resolution относятся к external vaults или runtime adapters.
`protected.use` разрешает adapter use без раскрытия plaintext через OACS
records, а `protected.read` и `secret.read` описывают явное plaintext disclosure
внешним vault adapter и должны выдаваться узко. Context Capsules,
ToolCallResult, public payloads EvidenceRef и metadata AuditEvent не должны
сохранять plaintext protected values.

Scope semantics строгие. Requested operation scope должен быть subset of grant
scope и resource scope. Empty grant scope совпадает только с empty requested
scope. Broad access требует явного `*` в grant. Namespace и memory depth limits
проверяются до decrypt content для non-bootstrap actors.

Retrieval расширяемый, но всегда bound by policy. Providers получают только
memories, которые уже прошли capability, scope, namespace, depth, lifecycle и
status filtering. Обязательный baseline - deterministic lexical retrieval и
structured evidence retrieval по `MemoryContent.evidence`. Embeddings могут быть
реализованы explicit adapters, но они disabled by default, не требуют network
для conformance и не являются требованием OACS conformance.

Python-specific behavior является reference-only, если эта спецификация или
JSON Schema не говорит обратного. `acs` CLI, FastAPI routes, SQLite backend,
local passphrase key provider, local CLI execution, HTTP execution, LM Studio
support, benchmark runners и repo dogfood workflow являются validation и
integration surfaces вокруг standard contract, а не обязательными runtime
features.
