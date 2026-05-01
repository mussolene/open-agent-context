# Compatibility Policy / Политика совместимости

## EN
OACS v0.1 is a draft. Until v1.0, compatibility is best-effort and the project
may make breaking changes when they improve correctness, security, or clarity.

Breaking changes before v1.0 include:
- Removing or renaming a public CLI command or API endpoint.
- Changing required fields or semantics in JSON schemas.
- Changing lifecycle transition rules.
- Changing default capability policy from deny-by-default.
- Changing encryption metadata format in a way that makes existing records unreadable.
- Changing ContextCapsule checksum semantics.
- Changing benchmark scoring semantics.

Non-breaking changes before v1.0 include:
- Adding optional fields.
- Adding commands, endpoints, schemas, rules, skills, or tools.
- Tightening validation for invalid data.
- Fixing behavior that previously returned success without durable state.
- Adding new storage or retrieval backends behind existing interfaces.

At v1.0, the project should publish stable schemas, migration rules, and backend
conformance tests.

## RU
OACS v0.1 является draft. До v1.0 совместимость best-effort, и проект может
делать breaking changes, если это улучшает корректность, безопасность или
ясность.

Breaking changes до v1.0:
- Удаление или переименование public CLI command или API endpoint.
- Изменение required fields или semantics в JSON schemas.
- Изменение lifecycle transition rules.
- Изменение default capability policy с deny-by-default.
- Изменение encryption metadata format так, что существующие records нельзя читать.
- Изменение semantics checksum для ContextCapsule.
- Изменение benchmark scoring semantics.

Non-breaking changes до v1.0:
- Добавление optional fields.
- Добавление commands, endpoints, schemas, rules, skills или tools.
- Усиление validation для invalid data.
- Исправление поведения, которое раньше возвращало success без durable state.
- Добавление новых storage или retrieval backends за существующими interfaces.

К v1.0 проект должен опубликовать stable schemas, migration rules и backend
conformance tests.
