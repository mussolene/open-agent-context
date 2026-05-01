# Architecture / Архитектура

## EN
The POC is layered:

1. Schemas and typed models.
2. SQLite storage with encrypted sensitive payloads.
3. Capability and policy checks.
4. Registries for rules, skills, tools, and MCP bindings.
5. Context capsule builder and memory loop.
6. CLI `acs` and FastAPI HTTP API.
7. Deterministic benchmark runner.

Modules are intentionally small and framework-agnostic below CLI/API.

## RU
POC построен слоями:

1. Схемы и типизированные модели.
2. SQLite-хранилище с шифрованием чувствительных payload.
3. Проверка capabilities и политик.
4. Реестры правил, skills, tools и MCP bindings.
5. Сборщик Context Capsule и memory loop.
6. CLI `acs` и HTTP API на FastAPI.
7. Детерминированный benchmark runner.

Модули ниже CLI/API небольшие и не зависят от агентных фреймворков.
