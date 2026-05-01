# OACS v0.1 draft Specification / Спецификация OACS v0.1 draft

## EN
OACS v0.1 draft defines a deterministic lower layer for agent context. A model receives a
Context Capsule assembled from task intent, scope, memory, rules, skills, tools,
evidence, permissions, and explicit forbidden assumptions.

Core records: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

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

Этот документ является draft-контрактом стандарта, а не финальным стандартом.
Python package в этом репозитории — reference implementation для draft.

Операции ориентированы на JSON и аудит. Запись памяти явная:
`observe`, `propose` и `commit` разделены. Размытая память D3-D5 является
гипотезой, а не фактом.
