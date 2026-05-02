# Compatibility Policy / Политика совместимости

## EN
OACS v0.1 draft is not stable. Until v1.0, compatibility is best-effort and the
project may make breaking changes when they improve correctness, security, or
clarity.

Breaking changes before v1.0 include:
- Removing or renaming a public CLI command or API endpoint.
- Changing required fields or semantics in JSON schemas.
- Changing lifecycle transition rules.
- Changing default capability policy from deny-by-default.
- Changing encryption metadata format in a way that makes existing records unreadable.
- Changing ContextCapsule checksum semantics.
- Changing ContextCapsule export envelope or integrity metadata semantics,
  including `integrity.payload_checksum`, `integrity.signature`, algorithm names,
  or checksum canonicalization.
- Changing conformance fixture scoring semantics.

Non-breaking changes before v1.0 include:
- Adding optional fields.
- Adding commands, endpoints, schemas, rules, skills, or tools.
- Tightening validation for invalid data.
- Fixing behavior that previously returned success without durable state.
- Adding new storage or retrieval backends behind existing interfaces.
- Accepting both raw ContextCapsule JSON and `context_capsule_export` envelopes
  on import/validation while preserving existing checksum behavior.

The `StorageBackend` protocol is still draft-level before v1.0 and may evolve;
SQLite remains the reference backend for compatibility checks.

Reference benchmark scoring is adapter-level unless a fixture is explicitly
promoted to conformance. Changing optional benchmark adapters is not a standard
breaking change by itself.

Scoped memory grants are part of the v0.2 reference implementation. Before
v1.0, exact grant matching rules may tighten, but broadening access without an
explicit grant is considered a compatibility and security regression.

At v1.0, the project should publish stable schemas, migration rules, and backend
conformance tests.

## RU
OACS v0.1 draft не является стабильным стандартом. До v1.0 совместимость
best-effort, и проект может делать breaking changes, если это улучшает
корректность, безопасность или ясность.

Breaking changes до v1.0:
- Удаление или переименование public CLI command или API endpoint.
- Изменение required fields или semantics в JSON schemas.
- Изменение lifecycle transition rules.
- Изменение default capability policy с deny-by-default.
- Изменение encryption metadata format так, что существующие records нельзя читать.
- Изменение semantics checksum для ContextCapsule.
- Изменение ContextCapsule export envelope или integrity metadata semantics,
  включая `integrity.payload_checksum`, `integrity.signature`, algorithm names
  или checksum canonicalization.
- Изменение conformance fixture scoring semantics.

Non-breaking changes до v1.0:
- Добавление optional fields.
- Добавление commands, endpoints, schemas, rules, skills или tools.
- Усиление validation для invalid data.
- Исправление поведения, которое раньше возвращало success без durable state.
- Добавление новых storage или retrieval backends за существующими interfaces.
- Приём raw ContextCapsule JSON и `context_capsule_export` envelopes на
  import/validation при сохранении текущего checksum behavior.

`StorageBackend` protocol до v1.0 остаётся draft-level и может меняться; SQLite
остаётся reference backend для compatibility checks.

Reference benchmark scoring находится на уровне adapter, если fixture явно не
promoted to conformance. Изменение optional benchmark adapters само по себе не
является breaking change стандарта.

Scoped memory grants являются частью v0.2 reference implementation. До v1.0
точные правила matching могут ужесточаться, но расширение доступа без явного
grant считается compatibility и security regression.

К v1.0 проект должен опубликовать stable schemas, migration rules и backend
conformance tests.
