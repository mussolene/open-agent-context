# OACS v0.1 draft Specification / Спецификация OACS v0.1 draft

## EN
OACS v0.1 draft defines a deterministic lower layer for agent context. A model receives a
Context Capsule assembled from task intent, scope, memory, rules, skills, tools,
evidence, permissions, and explicit forbidden assumptions.

OACS is not an agent framework, model backend, vector database, benchmark
harness, or replacement for MCP. It is the memory/context contract that those
systems can call before they invoke a model, tool, or external service.

Core records: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Reference implementation note: OACS v0.1 draft allows `MemoryRecord.content` to
carry structured evidence items. This is not a new standard entity; it is the
current compatibility path for turning external traces into evidence-backed
memory without teaching the generic memory loop source-specific text formats.

Reference implementation v0.3.0 includes `memory_calls` as a backend-independent
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

This document is a draft standard contract, not a final standard. The Python
package in this repository is the reference implementation for the draft.

Operations are JSON-first and auditable. Memory writes are explicit:
`observe`, `propose`, and `commit` are separate operations. Fuzzy memories
at D3-D5 are hypotheses, not facts.

v0.3.0 includes operation envelopes for `MemoryOperation`, `ContextOperation`,
`memory_call`, and `MemoryLoopRun` in `schemas/`. Operation envelopes are
metadata contracts: they record actor, scope, status, arguments, result
metadata, and audit references without requiring plaintext memory content.

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

## RU
OACS v0.1 draft задаёт детерминированный нижний слой агентского контекста. Модель получает
Context Capsule, собранную из задачи, намерения, области видимости, памяти,
правил, skills, tools, evidence, разрешений и явно запрещённых предположений.

OACS не является agent framework, model backend, vector database, benchmark
harness или заменой MCP. Это memory/context contract, который такие системы
могут вызывать до обращения к модели, tool или внешнему сервису.

Основные записи: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Примечание reference implementation: OACS v0.1 draft допускает structured
evidence items внутри `MemoryRecord.content`. Это не новая сущность стандарта, а
текущий compatibility path для преобразования внешних traces в evidence-backed
memory без обучения generic memory loop source-specific text formats.

Reference implementation v0.3.0 включает `memory_calls` как backend-independent
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

Этот документ является draft-контрактом стандарта, а не финальным стандартом.
Python package в этом репозитории — reference implementation для draft.

Операции ориентированы на JSON и аудит. Запись памяти явная:
`observe`, `propose` и `commit` разделены. Размытая память D3-D5 является
гипотезой, а не фактом.

v0.3.0 включает operation envelopes для `MemoryOperation`, `ContextOperation`,
`memory_call` и `MemoryLoopRun` в `schemas/`. Operation envelopes являются
metadata contracts: они записывают actor, scope, status, arguments, result
metadata и audit references без требования раскрывать plaintext memory content.

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
