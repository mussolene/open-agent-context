# OACS v0.1 draft Specification / Спецификация OACS v0.1 draft

## EN
OACS v0.1 draft defines a deterministic lower layer for agent context. A model receives a
Context Capsule assembled from task intent, scope, memory, rules, skills, tools,
evidence, permissions, and explicit forbidden assumptions.

Core records: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Reference implementation note: OACS v0.1 draft allows `MemoryRecord.content` to
carry structured evidence items. This is not a new standard entity; it is the
current compatibility path for turning external traces into evidence-backed
memory without teaching the generic memory loop source-specific text formats.

Reference implementation v0.2.5 includes `memory_calls` as a backend-independent
operation trace for memory work in the general MemoryLoopEngine, CLI, API, and
benchmark runner, with adaptive context policy deciding between compact capsule
and memory-call paths. Native model `tool_calls` may be used by a future
adapter, but OACS does not require backend tool-calling support to query, read,
extract evidence, audit, or build capsules. Storage is accessed through a thin
`StorageBackend` protocol, with SQLite as the reference backend. Subagent shared
memory is represented by ordinary scoped `CapabilityGrant` records over ordinary
scoped `MemoryRecord` records.

This document is a draft standard contract, not a final standard. The Python
package in this repository is the reference implementation for the draft.

Operations are JSON-first and auditable. Memory writes are explicit:
`observe`, `propose`, and `commit` are separate operations. Fuzzy memories
at D3-D5 are hypotheses, not facts.

## RU
OACS v0.1 draft задаёт детерминированный нижний слой агентского контекста. Модель получает
Context Capsule, собранную из задачи, намерения, области видимости, памяти,
правил, skills, tools, evidence, разрешений и явно запрещённых предположений.

Основные записи: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Примечание reference implementation: OACS v0.1 draft допускает structured
evidence items внутри `MemoryRecord.content`. Это не новая сущность стандарта, а
текущий compatibility path для преобразования внешних traces в evidence-backed
memory без обучения generic memory loop source-specific text formats.

Reference implementation v0.2.5 включает `memory_calls` как backend-independent
operation trace для работы с памятью в общем MemoryLoopEngine, CLI, API и
benchmark runner, а adaptive context policy выбирает между compact capsule и
memory-call paths. Native model `tool_calls` может использоваться будущим
adapter, но OACS не требует backend tool-calling support для query, read,
evidence extraction, audit или context capsule build. Storage доступен через
тонкий `StorageBackend` protocol, SQLite остаётся reference backend. Shared
memory для subagents представлена обычными scoped `CapabilityGrant` поверх
обычных scoped `MemoryRecord`.

Этот документ является draft-контрактом стандарта, а не финальным стандартом.
Python package в этом репозитории — reference implementation для draft.

Операции ориентированы на JSON и аудит. Запись памяти явная:
`observe`, `propose` и `commit` разделены. Размытая память D3-D5 является
гипотезой, а не фактом.
