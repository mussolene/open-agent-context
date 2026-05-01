# OACS v0.1 Specification / Спецификация OACS v0.1

## EN
OACS defines a deterministic lower layer for agent context. A model receives a
Context Capsule assembled from task intent, scope, memory, rules, skills, tools,
evidence, permissions, and explicit forbidden assumptions.

Core records: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Operations are JSON-first and auditable. Memory writes are explicit:
`observe`, `propose`, and `commit` are separate operations. Fuzzy memories
at D3-D5 are hypotheses, not facts.

## RU
OACS задаёт детерминированный нижний слой агентского контекста. Модель получает
Context Capsule, собранную из задачи, намерения, области видимости, памяти,
правил, skills, tools, evidence, разрешений и явно запрещённых предположений.

Основные записи: Actor, Agent, Identity, CapabilityGrant, MemoryRecord,
ContextCapsule, RuleManifest, SkillManifest, ToolBinding, McpBinding,
EvidenceRef, AuditEvent, TaskTrace, ExperienceTrace, MemoryLoopRun.

Операции ориентированы на JSON и аудит. Запись памяти явная:
`observe`, `propose` и `commit` разделены. Размытая память D3-D5 является
гипотезой, а не фактом.
