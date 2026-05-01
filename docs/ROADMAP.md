# Roadmap / Дорожная карта

## EN
This roadmap is for OACS v0.1 draft and the Python reference implementation.

### v0.2
- Dogfood OACS under its own development and benchmark workflows: memory,
  context, evidence, and audit operations should be usable as deterministic
  MCP-like tools.
- Promote `oacs_memory_tool_loop` into the general MemoryLoopEngine with
  structured intent, memory query/read, evidence extraction, and deepening.
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
- Add larger benchmark suites with real LM Studio mode reporting.

### v1.0
- Freeze stable schemas for ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef, and
  AuditEvent.
- Define compatibility guarantees and migration policy.
- Provide backend conformance tests.
- Publish a reference benchmark pack and reproducibility report.

## RU
Этот roadmap относится к OACS v0.1 draft и Python reference implementation.

### v0.2
- Использовать OACS под капотом собственной разработки и benchmark workflows:
  memory, context, evidence и audit operations должны работать как
  deterministic MCP-like tools.
- Перенести `oacs_memory_tool_loop` в общий MemoryLoopEngine со structured
  intent, memory query/read, evidence extraction и deepening.
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
- Расширить benchmark suites с real LM Studio mode reporting.

### v1.0
- Заморозить stable schemas для ContextCapsule, MemoryRecord, CapabilityGrant,
  RuleManifest, SkillManifest, ToolBinding, McpBinding, EvidenceRef и
  AuditEvent.
- Зафиксировать compatibility guarantees и migration policy.
- Добавить backend conformance tests.
- Опубликовать reference benchmark pack и reproducibility report.
