# Architecture / Архитектура

## EN
The POC is layered:

1. Schemas and typed models.
2. Thin `StorageBackend` protocol with SQLite as the reference backend and
   encrypted sensitive payloads above it.
3. Capability and policy checks.
4. Registries for rules, skills, tools, and MCP bindings.
5. Context capsule builder and memory loop.
6. CLI `acs` and FastAPI HTTP API.
7. Deterministic benchmark runner.

Modules are intentionally small and framework-agnostic below CLI/API.

## RU
POC построен слоями:

1. Схемы и типизированные модели.
2. Тонкий `StorageBackend` protocol с SQLite как reference backend и
   шифрованием sensitive payloads поверх него.
3. Проверка capabilities и политик.
4. Реестры правил, skills, tools и MCP bindings.
5. Сборщик Context Capsule и memory loop.
6. CLI `acs` и HTTP API на FastAPI.
7. Детерминированный benchmark runner.

Модули ниже CLI/API небольшие и не зависят от агентных фреймворков.
