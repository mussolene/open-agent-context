# Roadmap / Дорожная карта

## EN
This roadmap is for OACS v0.1 draft and the Python reference implementation.

### Current Position: v0.2.0 Reference POC
- Done: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, basic memory loop,
  and MemoryArena `group_travel_planner` adapter.
- Done: `oacs_memory_call_loop` dogfoods OACS as a deterministic memory-call
  layer under benchmark execution: intent classification, scoped memory query,
  structured evidence extraction, compact prompt, and token/evidence metrics.
- Proven on public data: MemoryArena `group_travel_planner` first 5 tasks with
  `google/gemma-4-e2b`, where `oacs_memory_call_loop` beats current-task-only,
  raw full context, and broad capsule prompting.
- Proven on public deterministic harness: MemoryArena `group_travel_planner`
  20 memory-supported tasks, where `oacs_memory_call_loop` reaches 20/20 exact
  success with lower token use than raw full context.
- In progress: promote benchmark-local memory_calls into the general
  MemoryLoopEngine and expose the same operations as stable OACS memory calls.
- Thin import adapters added: MemoryArena `progressive_search` and AMA-Bench
  open-ended QA rows. These validate OACS mapping only; they are not native
  benchmark harness replacements.
- Real LM Studio `google/gemma-4-e2b` runs now cover synthetic memory-critical,
  MemoryArena group travel, MemoryArena progressive search, and AMA-Bench
  open-ended QA. Results show clear gains for medium/large/long memory tasks and
  overhead on tiny tasks.
- Done in the v0.2 direction: benchmark-specific text parsing was moved out of
  the prototype memory-call loop. Synthetic tasks and public adapters now attach
  structured evidence to `MemoryRecord.content`, and the generic memory-call
  loop consumes that shape.
- Still in progress: promote these memory_calls into stable OACS memory calls
  on the general MemoryLoopEngine surface.
- Done: benchmark execution now uses explicit `memory_calls` instead of
  backend-dependent `tool_calls` or hidden parser heuristics. The benchmark mode
  is `oacs_memory_call_loop`.
- Not done yet: MemoryArena `bundled_shopping`, PERMA, Mem2ActBench, and native
  external benchmark harness compatibility.

### v0.2
- Dogfood OACS under its own development and benchmark workflows: memory,
  context, evidence, and audit operations should be usable as deterministic
  MCP-like tools.
- Promote `memory_calls` into the general MemoryLoopEngine, CLI, and API with
  structured intent, memory query/read, evidence extraction, and deepening.
- Stabilize structured evidence as an adapter boundary and remove any remaining
  source-specific parsing from generic loops.
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
Этот roadmap относится к OACS v0.1 draft и Python reference implementation.

### Текущая позиция: v0.2.0 Reference POC
- Готово: OACS v0.1 draft terminology, schemas, encrypted SQLite memory,
  ContextCapsule, CLI/API, rules/skills/tools/MCP registries, базовый memory
  loop и adapter для MemoryArena `group_travel_planner`.
- Готово: `oacs_memory_call_loop` использует OACS под капотом benchmark
  execution как deterministic memory-call layer: intent classification, scoped
  memory query, structured evidence extraction, compact prompt и
  token/evidence metrics.
- Доказано на public data: первые 5 задач MemoryArena `group_travel_planner` с
  `google/gemma-4-e2b`, где `oacs_memory_call_loop` выигрывает у current-task-only,
  raw full context и broad capsule prompting.
- Доказано на public deterministic harness: 20 memory-supported задач MemoryArena
  `group_travel_planner`, где `oacs_memory_call_loop` достигает 20/20 exact
  success с меньшим token use, чем raw full context.
- В работе: перенести benchmark-local memory_calls в общий MemoryLoopEngine и
  открыть те же операции как stable OACS memory calls.
- Добавлены thin import adapters: MemoryArena `progressive_search` и AMA-Bench
  open-ended QA rows. Они валидируют OACS mapping, но не заменяют native
  benchmark harnesses.
- Real LM Studio прогоны с `google/gemma-4-e2b` теперь покрывают synthetic
  memory-critical, MemoryArena group travel, MemoryArena progressive search и
  AMA-Bench open-ended QA. Результаты показывают пользу на medium/large/long
  memory tasks и overhead на tiny tasks.
- Сделано в направлении v0.2: benchmark-specific text parsing вынесен из
  prototype memory-call loop. Synthetic tasks и public adapters теперь пишут
  structured evidence в `MemoryRecord.content`, а generic memory-call loop
  читает эту форму.
- Ещё в работе: поднять эти memory_calls до stable OACS memory calls на
  общем MemoryLoopEngine surface.
- Готово: benchmark execution теперь использует явные `memory_calls` вместо
  backend-dependent `tool_calls` или скрытых parser heuristics. Benchmark mode:
  `oacs_memory_call_loop`.
- Ещё не готово: MemoryArena `bundled_shopping`, PERMA, Mem2ActBench и native
  external benchmark harness compatibility.

### v0.2
- Использовать OACS под капотом собственной разработки и benchmark workflows:
  memory, context, evidence и audit operations должны работать как
  deterministic MCP-like tools.
- Перенести `memory_calls` в общий MemoryLoopEngine, CLI и API со structured
  intent, memory query/read, evidence extraction и deepening.
- Стабилизировать structured evidence как adapter boundary и убрать оставшийся
  source-specific parsing из generic loops.
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
