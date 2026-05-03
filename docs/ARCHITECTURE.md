# OACS v1.0 Architecture / Архитектура OACS v1.0

## EN
OACS separates the v1.0 standard from reference adapters. The standard is the
memory/context contract; adapters prove that the contract can be embedded in
existing agent stacks.
The portability boundary is JSON records plus JSON Schema validation. The
Python package is one reference implementation of that boundary.

Core OACS should stay small: `MemoryRecord`, `ContextCapsule`,
`CapabilityGrant`, `EvidenceRef`, auditable operations, and `memory_calls`.
Shell commands, benchmarks, LM Studio, MCP execution, and repo dogfood are
reference adapters around that contract, not new standard layers.

The reference implementation is layered:

1. Schemas and typed models.
2. Thin `StorageBackend` protocol with SQLite as the reference backend and
   encrypted sensitive payloads above it.
3. Capability and policy checks, including scoped memory grants for subagents.
4. Registries for rules, skills, tools, and MCP bindings.
5. Context capsule builder and memory loop.
6. CLI `acs` and FastAPI HTTP API.
7. Validation adapters and deterministic benchmark fixtures outside the core
   contract.

`ToolRunner` is the reference execution boundary for `ToolBinding`. It checks
capabilities, validates JSON schemas, executes the selected adapter, stores the
result as an `EvidenceRef`, and writes audit events.

Modules are intentionally small and framework-agnostic below CLI/API.
For non-Python runtimes, use `docs/INTEROPERABILITY.md` and
`conformance/fixtures/` as the implementation target.

## RU
OACS разделяет v1.0 standard и reference adapters. Standard - это
memory/context contract; adapters доказывают, что contract можно встроить в
существующие agent stacks.
Portability boundary - это JSON records плюс JSON Schema validation. Python
package является одной reference implementation этой boundary.

Core OACS должен оставаться небольшим: `MemoryRecord`, `ContextCapsule`,
`CapabilityGrant`, `EvidenceRef`, auditable operations и `memory_calls`.
Shell commands, benchmarks, LM Studio, MCP execution и repo dogfood являются
reference adapters вокруг этого contract, а не новыми слоями стандарта.

Reference implementation построена слоями:

1. Схемы и типизированные модели.
2. Тонкий `StorageBackend` protocol с SQLite как reference backend и
   шифрованием sensitive payloads поверх него.
3. Проверка capabilities и политик, включая scoped memory grants для subagents.
4. Реестры правил, skills, tools и MCP bindings.
5. Сборщик Context Capsule и memory loop.
6. CLI `acs` и HTTP API на FastAPI.
7. Validation adapters и deterministic benchmark fixtures вне core contract.

`ToolRunner` является reference execution boundary для `ToolBinding`. Он
проверяет capabilities, валидирует JSON schemas, запускает выбранный adapter,
сохраняет результат как `EvidenceRef` и пишет audit events.

Модули ниже CLI/API небольшие и не зависят от агентных фреймворков.
Для non-Python runtimes используйте `docs/INTEROPERABILITY.md` и
`conformance/fixtures/` как implementation target.
