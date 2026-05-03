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

### v1.0 Freeze Prep

Freeze prep separates the portable standard surface from reference-only support
files before the first stable standard release. `docs/FREEZE_PREP.md` is the
per-schema manifest; this section is the compatibility policy summary.

Freeze candidate schemas:

| Area | Schemas | Freeze expectation |
| --- | --- | --- |
| Context and memory | `context_capsule`, `memory_record` | Stable JSON shape, checksum semantics, lifecycle, depth, scope, and evidence projection. |
| Permissions and audit | `capability_grant`, `audit_event` | Stable deny-by-default capability semantics, explicit wildcard handling, content hash semantics, and audit chain metadata. |
| Evidence and protected refs | `evidence_ref`, `protected_ref` | Stable public payload rules, external protected reference boundary, and no plaintext or masked protected values in portable records. |
| Manifests and bindings | `rule_manifest`, `skill_manifest`, `tool_binding`, `mcp_binding` | Stable metadata contract for adapters; execution remains adapter behavior unless the schema requires otherwise. |
| Operation envelopes | `memory_operation`, `context_operation`, `memory_call`, `memory_loop_run`, `tool_call_result` | Stable auditable envelopes for operation traces and tool-result evidence. |
| Retrieval and storage selectors | `retrieval_query`, `retrieval_result`, `storage_selector` | Stable policy-first query/result/selector shape without backend-specific query fragments. |

Draft support schemas remain outside the v1.0 freeze candidate set until they
are explicitly promoted by the roadmap: `actor`, `context_capsule_export`,
`benchmark_task`, and `benchmark_task_pack`.

Migration policy for v1.0:

- Stable schemas use additive optional fields for compatible evolution.
- New required fields, enum removals, checksum changes, or semantic rejection
  changes require a new draft/stable version and migration notes.
- Security tightening that rejects previously invalid or unsafe data may happen
  in a patch release when the rejected data was outside the documented contract.
- Python CLI/API/storage behavior is not a standard compatibility guarantee
  unless the behavior is required by a stable schema, fixture, or spec section.

Conformance boundary for v1.0:

- Positive fixtures are portable examples every implementation should accept.
- Negative fixtures are required rejection examples for adapter-boundary checks.
- The Python `acs conformance validate` command is the reference checker, not a
  mandatory runtime interface.
- Backend, retrieval, vault, model, benchmark, MCP stdio, and hosted API choices
  are adapter behavior unless promoted into the stable schema/spec set.

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

### v1.0 Freeze Prep

Freeze prep отделяет portable standard surface от reference-only support files
перед первым stable release стандарта. `docs/FREEZE_PREP.md` является
per-schema manifest; этот раздел является summary compatibility policy.

Freeze candidate schemas:

| Area | Schemas | Freeze expectation |
| --- | --- | --- |
| Context and memory | `context_capsule`, `memory_record` | Stable JSON shape, checksum semantics, lifecycle, depth, scope и evidence projection. |
| Permissions and audit | `capability_grant`, `audit_event` | Stable deny-by-default capability semantics, explicit wildcard handling, content hash semantics и audit chain metadata. |
| Evidence and protected refs | `evidence_ref`, `protected_ref` | Stable public payload rules, external protected reference boundary и отсутствие plaintext или masked protected values в portable records. |
| Manifests and bindings | `rule_manifest`, `skill_manifest`, `tool_binding`, `mcp_binding` | Stable metadata contract для adapters; execution остаётся adapter behavior, если schema не требует иного. |
| Operation envelopes | `memory_operation`, `context_operation`, `memory_call`, `memory_loop_run`, `tool_call_result` | Stable auditable envelopes для operation traces и tool-result evidence. |
| Retrieval and storage selectors | `retrieval_query`, `retrieval_result`, `storage_selector` | Stable policy-first query/result/selector shape без backend-specific query fragments. |

Draft support schemas остаются вне freeze candidate set v1.0, пока roadmap явно
не продвинет их: `actor`, `context_capsule_export`, `benchmark_task` и
`benchmark_task_pack`.

Migration policy для v1.0:

- Stable schemas развиваются совместимо через additive optional fields.
- Новые required fields, удаление enum values, изменения checksum или semantic
  rejection changes требуют новой draft/stable version и migration notes.
- Security tightening, который reject ранее invalid или unsafe data, может
  выйти в patch release, если rejected data была вне documented contract.
- Python CLI/API/storage behavior не является standard compatibility guarantee,
  если behavior не требуется stable schema, fixture или spec section.

Conformance boundary для v1.0:

- Positive fixtures являются portable examples, которые implementation должна
  принимать.
- Negative fixtures являются required rejection examples для adapter-boundary
  checks.
- Python command `acs conformance validate` является reference checker, а не
  mandatory runtime interface.
- Backend, retrieval, vault, model, benchmark, MCP stdio и hosted API choices
  являются adapter behavior, если не promoted в stable schema/spec set.
