# Compatibility Policy / Политика совместимости

## EN
OACS v1.0 freezes the portable standard surface listed below. Compatibility is
defined for stable schemas, conformance fixtures, and spec semantics; Python
CLI/API/storage behavior remains a reference implementation detail unless a
stable schema, fixture, or spec section requires it.

Breaking changes after v1.0 include:
- Removing or renaming a public CLI command or API endpoint.
- Changing required fields or semantics in JSON schemas.
- Changing lifecycle transition rules.
- Changing default capability policy from deny-by-default.
- Changing encryption metadata format in a way that makes existing records unreadable.
- Changing ContextCapsule checksum semantics.
- Changing ContextCapsule export envelope or integrity metadata semantics,
  including `integrity.payload_checksum`, `integrity.mac`, the deprecated
  `integrity.signature` alias, algorithm names, or checksum canonicalization.
- Changing conformance fixture scoring semantics.

Non-breaking changes after v1.0 include:
- Adding optional fields.
- Adding commands, endpoints, schemas, rules, skills, or tools.
- Tightening validation for invalid data.
- Fixing behavior that previously returned success without durable state.
- Adding new storage or retrieval backends behind existing interfaces.
- Accepting both raw ContextCapsule JSON and `context_capsule_export` envelopes
  on import/validation while preserving existing checksum behavior.

The `StorageBackend` protocol remains reference implementation support and may
evolve when the portable storage selector contract is preserved; SQLite remains
the reference backend for compatibility checks.

Reference benchmark scoring is adapter-level unless a fixture is explicitly
promoted to conformance. Changing optional benchmark adapters is not a standard
breaking change by itself.

Scoped memory grants are part of the v1.0 stable permission surface. Exact
matching rules may tighten only as documented security rejection examples;
broadening access without an explicit grant is a compatibility and security
regression.

Context grants are operation-specific. `context.read` and `context.explain` do
not imply `context.export`, and `context.export` does not imply runtime read,
import, mount, lock, reduce, or expand permissions. Tightening a reference
implementation that previously over-granted through `context.export` is a
security fix when the portable operation names remain additive and documented.

### v1.0 Stable Surface

The v1.0 release separates the portable standard surface from reference-only
support files. `docs/FREEZE_PREP.md` is the per-schema manifest; this section is
the compatibility policy summary.

Freeze candidate schemas:

| Area | Schemas | Freeze expectation |
| --- | --- | --- |
| Context and memory | `context_capsule`, `memory_record` | Stable JSON shape, checksum semantics, lifecycle, depth, scope, and evidence projection. |
| Permissions and audit | `capability_grant`, `audit_event` | Stable deny-by-default capability semantics, explicit wildcard handling, content hash semantics, and audit chain metadata. |
| Evidence and protected refs | `evidence_ref`, `protected_ref` | Stable public payload rules, external protected reference boundary, and no plaintext or masked protected values in portable records. |
| Manifests and bindings | `rule_manifest`, `skill_manifest`, `tool_binding`, `mcp_binding` | Stable metadata contract for adapters; execution remains adapter behavior unless the schema requires otherwise. |
| Operation envelopes | `memory_operation`, `context_operation`, `memory_call`, `memory_loop_run`, `tool_call_result` | Stable auditable envelopes for operation traces and tool-result evidence. |
| Retrieval and storage selectors | `retrieval_query`, `retrieval_result`, `storage_selector` | Stable policy-first query/result/selector shape without backend-specific query fragments. |

Draft support schemas remain outside the v1.0 freeze candidate set. For the
v1.0 freeze, `actor` stays reference identity/API support: stable records carry
actor identifiers, but the identity registry shape is not a stable portable
record. `context_capsule_export` stays reference import/export packaging: raw
`ContextCapsule` JSON is the portable record, while export integrity envelopes
are optional adapter behavior. Benchmark task schemas remain reference-only.

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
OACS v1.0 замораживает portable standard surface, перечисленный ниже.
Compatibility определяется для stable schemas, conformance fixtures и spec
semantics; Python CLI/API/storage behavior остаётся detail reference
implementation, если stable schema, fixture или spec section не требует его.

Breaking changes после v1.0:
- Удаление или переименование public CLI command или API endpoint.
- Изменение required fields или semantics в JSON schemas.
- Изменение lifecycle transition rules.
- Изменение default capability policy с deny-by-default.
- Изменение encryption metadata format так, что существующие records нельзя читать.
- Изменение semantics checksum для ContextCapsule.
- Изменение ContextCapsule export envelope или integrity metadata semantics,
  включая `integrity.payload_checksum`, `integrity.mac`, deprecated alias
  `integrity.signature`, algorithm names или checksum canonicalization.
- Изменение conformance fixture scoring semantics.

Non-breaking changes после v1.0:
- Добавление optional fields.
- Добавление commands, endpoints, schemas, rules, skills или tools.
- Усиление validation для invalid data.
- Исправление поведения, которое раньше возвращало success без durable state.
- Добавление новых storage или retrieval backends за существующими interfaces.
- Приём raw ContextCapsule JSON и `context_capsule_export` envelopes на
  import/validation при сохранении текущего checksum behavior.

`StorageBackend` protocol остаётся support reference implementation и может
меняться при сохранении portable storage selector contract; SQLite остаётся
reference backend для compatibility checks.

Reference benchmark scoring находится на уровне adapter, если fixture явно не
promoted to conformance. Изменение optional benchmark adapters само по себе не
является breaking change стандарта.

Scoped memory grants являются частью v1.0 stable permission surface. Точные
правила matching могут ужесточаться только как documented security rejection
examples; расширение доступа без явного grant является compatibility и security
regression.

Context grants разделены по операциям. `context.read` и `context.explain` не
означают `context.export`, а `context.export` не означает runtime read, import,
mount, lock, reduce или expand permissions. Ужесточение reference
implementation, где раньше всё шло через `context.export`, является security fix,
если portable operation names остаются additive и documented.

### v1.0 Stable Surface

v1.0 release отделяет portable standard surface от reference-only support files.
`docs/FREEZE_PREP.md` является per-schema manifest; этот раздел является summary
compatibility policy.

Freeze candidate schemas:

| Area | Schemas | Freeze expectation |
| --- | --- | --- |
| Context and memory | `context_capsule`, `memory_record` | Stable JSON shape, checksum semantics, lifecycle, depth, scope и evidence projection. |
| Permissions and audit | `capability_grant`, `audit_event` | Stable deny-by-default capability semantics, explicit wildcard handling, content hash semantics и audit chain metadata. |
| Evidence and protected refs | `evidence_ref`, `protected_ref` | Stable public payload rules, external protected reference boundary и отсутствие plaintext или masked protected values в portable records. |
| Manifests and bindings | `rule_manifest`, `skill_manifest`, `tool_binding`, `mcp_binding` | Stable metadata contract для adapters; execution остаётся adapter behavior, если schema не требует иного. |
| Operation envelopes | `memory_operation`, `context_operation`, `memory_call`, `memory_loop_run`, `tool_call_result` | Stable auditable envelopes для operation traces и tool-result evidence. |
| Retrieval and storage selectors | `retrieval_query`, `retrieval_result`, `storage_selector` | Stable policy-first query/result/selector shape без backend-specific query fragments. |

Draft support schemas остаются вне freeze candidate set v1.0. Для v1.0 freeze
`actor` остаётся reference identity/API support: stable records несут actor
identifiers, но identity registry shape не является stable portable record.
`context_capsule_export` остаётся reference import/export packaging: raw
`ContextCapsule` JSON является portable record, а export integrity envelopes
являются optional adapter behavior. Benchmark task schemas остаются
reference-only.

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
