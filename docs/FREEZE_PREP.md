# v1.0 Freeze Prep Manifest / Манифест подготовки v1.0 freeze

## EN
This manifest is the working control surface for stabilizing OACS v1.0. It is
not the v1.0 freeze itself. It classifies every checked-in JSON Schema and makes
the conformance coverage target explicit.

Status values:

- `stable_candidate`: intended for the v1.0 portable standard surface.
- `draft_support`: useful draft schema, but not yet promoted to the v1.0 stable
  set.
- `reference_only`: reference validation artifact, not a standard requirement.

Each `stable_candidate` schema must have a positive fixture for v1.0. A
negative fixture is required when the schema has a meaningful adapter-boundary
or semantic rejection rule.

| Schema | Status | Positive fixture | Negative fixture coverage | Freeze criterion |
| --- | --- | --- | --- | --- |
| `actor` | `draft_support` | no | no | Keep actor identity records outside v1.0 stable schemas; stable records reference actor IDs, while identity registry shape remains reference/API support. |
| `audit_event` | `stable_candidate` | yes | yes | Freeze content hash semantics, chain metadata, metadata redaction, scope, namespace, and lifecycle fields. |
| `benchmark_task` | `reference_only` | no | no | Keep benchmark pack internals outside core conformance unless explicitly promoted. |
| `benchmark_task_pack` | `reference_only` | no | no | Keep benchmark pack internals outside core conformance unless explicitly promoted. |
| `capability_grant` | `stable_candidate` | yes | yes | Freeze deny-by-default, explicit wildcard semantics, scope subset rules, namespace allowlists, depth limits, and distinct context operation grants. |
| `context_capsule` | `stable_candidate` | yes | yes | Freeze canonical checksum, projection rules, permission envelope, evidence references, expiry, and forbidden assumptions. |
| `context_capsule_export` | `draft_support` | no | no | Keep export integrity envelopes outside v1.0 stable schemas; raw ContextCapsule remains the portable record, while signed import/export packaging remains reference support. |
| `context_operation` | `stable_candidate` | yes | yes | Freeze operation envelope fields, actor/scope/status metadata, and audit reference semantics. |
| `evidence_ref` | `stable_candidate` | yes | yes | Freeze public payload rules, sensitive payload boundary, content hash, URI, status, namespace, and scope semantics. |
| `mcp_binding` | `stable_candidate` | yes | yes | Freeze metadata-first binding shape and keep stdio execution adapter behavior outside core unless explicitly required. |
| `memory_call` | `stable_candidate` | yes | yes | Freeze operation names, intent/read/evidence trace shape, compact prompt metadata, and no final-answer synthesis rule. |
| `memory_loop_run` | `stable_candidate` | yes | yes | Freeze loop trace metadata, operation metrics, memory call linkage, and adapter-neutral result shape. |
| `memory_operation` | `stable_candidate` | yes | yes | Freeze observe/propose/commit/query/read/correct/forget/blur/sharpen operation envelope fields. |
| `memory_record` | `stable_candidate` | yes | yes | Freeze lifecycle, depth, scope, encrypted content boundary, evidence refs, D3-D5 embedded evidence thresholds, and status metadata. |
| `protected_ref` | `stable_candidate` | yes | yes | Freeze external provider/URI requirement for secrets, redacted projection, no plaintext/masked values, and status fields. |
| `retrieval_query` | `stable_candidate` | yes | no | Freeze policy-first query filters, scope/depth/status inputs, and backend-neutral options. |
| `retrieval_result` | `stable_candidate` | yes | yes | Freeze hit shape, evidence projection rules, and D3-D5 non-factual semantics. |
| `rule_manifest` | `stable_candidate` | yes | yes | Freeze rule metadata, risk/status enums, and required adapter-safe fields. |
| `skill_manifest` | `stable_candidate` | yes | yes | Freeze skill metadata, required tool/rule linkage, risk/status enums, and adapter-safe fields. |
| `storage_selector` | `stable_candidate` | yes | yes | Freeze backend-neutral filters/order/limit shape and reject backend-specific query fragments. |
| `tool_binding` | `stable_candidate` | yes | yes | Freeze tool metadata, input/output schema references, capability gates, and explicit network opt-in. |
| `tool_call_result` | `stable_candidate` | yes | yes | Freeze tool result envelope, evidence linkage, status metadata, and protected value leak rejection. |

Completed freeze-prep work:

1. Add descriptions to schema fields where a v1.0 implementer could confuse
   reference behavior with standard behavior.
2. Add semantic negative fixtures for stable candidates where rejection rules
   are not fully expressible as JSON Schema constraints.
3. Decide that `actor` and `context_capsule_export` remain `draft_support`
   rather than promoted to the v1.0 stable set.
4. Publish `docs/V1_RELEASE_CHECKLIST.md`, a final v1.0 checklist that blocks
   release on manifest drift, fixture drift, local gate failure, published
   package smoke failure, secret scan failure, or missing OACS proof.

Open freeze-prep work:

- None. The next step is running the v1.0 release checklist, not expanding the
  freeze-prep scope.

## RU
Этот manifest является рабочей control surface для стабилизации OACS v1.0. Это
ещё не сам v1.0 freeze. Он классифицирует каждую checked-in JSON Schema и явно
фиксирует цель conformance coverage.

Status values:

- `stable_candidate`: планируется для portable standard surface v1.0.
- `draft_support`: полезная draft schema, но ещё не promoted в stable set v1.0.
- `reference_only`: reference validation artifact, не требование стандарта.

Каждая schema со статусом `stable_candidate` должна иметь positive fixture до
v1.0. Negative fixture требуется, когда у schema есть meaningful
adapter-boundary или semantic rejection rule.

| Schema | Status | Positive fixture | Negative fixture coverage | Freeze criterion |
| --- | --- | --- | --- | --- |
| `actor` | `draft_support` | no | no | Оставить actor identity records вне v1.0 stable schemas; stable records ссылаются на actor IDs, а identity registry shape остаётся reference/API support. |
| `audit_event` | `stable_candidate` | yes | yes | Заморозить content hash semantics, chain metadata, metadata redaction, scope, namespace и lifecycle fields. |
| `benchmark_task` | `reference_only` | no | no | Оставить benchmark pack internals вне core conformance, если они явно не promoted. |
| `benchmark_task_pack` | `reference_only` | no | no | Оставить benchmark pack internals вне core conformance, если они явно не promoted. |
| `capability_grant` | `stable_candidate` | yes | yes | Заморозить deny-by-default, explicit wildcard semantics, scope subset rules, namespace allowlists, depth limits и distinct context operation grants. |
| `context_capsule` | `stable_candidate` | yes | yes | Заморозить canonical checksum, projection rules, permission envelope, evidence references, expiry и forbidden assumptions. |
| `context_capsule_export` | `draft_support` | no | no | Оставить export integrity envelopes вне v1.0 stable schemas; raw ContextCapsule остаётся portable record, а signed import/export packaging остаётся reference support. |
| `context_operation` | `stable_candidate` | yes | yes | Заморозить operation envelope fields, actor/scope/status metadata и audit reference semantics. |
| `evidence_ref` | `stable_candidate` | yes | yes | Заморозить public payload rules, sensitive payload boundary, content hash, URI, status, namespace и scope semantics. |
| `mcp_binding` | `stable_candidate` | yes | yes | Заморозить metadata-first binding shape и оставить stdio execution adapter behavior вне core, если он явно не требуется. |
| `memory_call` | `stable_candidate` | yes | yes | Заморозить operation names, intent/read/evidence trace shape, compact prompt metadata и no final-answer synthesis rule. |
| `memory_loop_run` | `stable_candidate` | yes | yes | Заморозить loop trace metadata, operation metrics, memory call linkage и adapter-neutral result shape. |
| `memory_operation` | `stable_candidate` | yes | yes | Заморозить observe/propose/commit/query/read/correct/forget/blur/sharpen operation envelope fields. |
| `memory_record` | `stable_candidate` | yes | yes | Заморозить lifecycle, depth, scope, encrypted content boundary, evidence refs, D3-D5 embedded evidence thresholds и status metadata. |
| `protected_ref` | `stable_candidate` | yes | yes | Заморозить external provider/URI requirement для secrets, redacted projection, отсутствие plaintext/masked values и status fields. |
| `retrieval_query` | `stable_candidate` | yes | no | Заморозить policy-first query filters, scope/depth/status inputs и backend-neutral options. |
| `retrieval_result` | `stable_candidate` | yes | yes | Заморозить hit shape, evidence projection rules и D3-D5 non-factual semantics. |
| `rule_manifest` | `stable_candidate` | yes | yes | Заморозить rule metadata, risk/status enums и required adapter-safe fields. |
| `skill_manifest` | `stable_candidate` | yes | yes | Заморозить skill metadata, required tool/rule linkage, risk/status enums и adapter-safe fields. |
| `storage_selector` | `stable_candidate` | yes | yes | Заморозить backend-neutral filters/order/limit shape и reject backend-specific query fragments. |
| `tool_binding` | `stable_candidate` | yes | yes | Заморозить tool metadata, input/output schema references, capability gates и explicit network opt-in. |
| `tool_call_result` | `stable_candidate` | yes | yes | Заморозить tool result envelope, evidence linkage, status metadata и protected value leak rejection. |

Completed freeze-prep work:

1. Добавить descriptions к schema fields, где v1.0 implementer может спутать
   reference behavior со standard behavior.
2. Добавить semantic negative fixtures для stable candidates, где rejection
   rules не полностью выражаются JSON Schema constraints.
3. Решить, что `actor` и `context_capsule_export` остаются `draft_support`, а не
   promoted в v1.0 stable set.
4. Опубликовать `docs/V1_RELEASE_CHECKLIST.md`, финальный v1.0 checklist,
   который блокирует release при manifest drift, fixture drift, local gate
   failure, published package smoke failure, secret scan failure или missing
   OACS proof.

Open freeze-prep work:

- None. Следующий шаг - запуск v1.0 release checklist, а не расширение
  freeze-prep scope.
