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

Each `stable_candidate` schema must have a positive fixture before v1.0. A
negative fixture is required when the schema has a meaningful adapter-boundary
or semantic rejection rule.

| Schema | Status | Positive fixture | Negative fixture coverage | Freeze criterion |
| --- | --- | --- | --- | --- |
| `actor` | `draft_support` | no | no | Decide whether identity records are stable standard records or reference API inputs. |
| `audit_event` | `stable_candidate` | yes | yes | Freeze content hash semantics, chain metadata, metadata redaction, scope, namespace, and lifecycle fields. |
| `benchmark_task` | `reference_only` | no | no | Keep benchmark pack internals outside core conformance unless explicitly promoted. |
| `benchmark_task_pack` | `reference_only` | no | no | Keep benchmark pack internals outside core conformance unless explicitly promoted. |
| `capability_grant` | `stable_candidate` | yes | yes | Freeze deny-by-default, explicit wildcard semantics, scope subset rules, namespace allowlists, and depth limits. |
| `context_capsule` | `stable_candidate` | yes | yes | Freeze canonical checksum, projection rules, permission envelope, evidence references, expiry, and forbidden assumptions. |
| `context_capsule_export` | `draft_support` | no | no | Decide whether export integrity envelope is core v1.0 or reference import/export behavior. |
| `context_operation` | `stable_candidate` | yes | no | Freeze operation envelope fields, actor/scope/status metadata, and audit reference semantics. |
| `evidence_ref` | `stable_candidate` | yes | yes | Freeze public payload rules, sensitive payload boundary, content hash, URI, status, namespace, and scope semantics. |
| `mcp_binding` | `stable_candidate` | yes | no | Freeze metadata-first binding shape and keep stdio execution adapter behavior outside core unless explicitly required. |
| `memory_call` | `stable_candidate` | yes | yes | Freeze operation names, intent/read/evidence trace shape, compact prompt metadata, and no final-answer synthesis rule. |
| `memory_loop_run` | `stable_candidate` | yes | no | Freeze loop trace metadata, operation metrics, memory call linkage, and adapter-neutral result shape. |
| `memory_operation` | `stable_candidate` | yes | no | Freeze observe/propose/commit/query/read/correct/forget/blur/sharpen operation envelope fields. |
| `memory_record` | `stable_candidate` | yes | no | Freeze lifecycle, depth, scope, encrypted content boundary, evidence refs, and status metadata. |
| `protected_ref` | `stable_candidate` | yes | yes | Freeze external provider/URI requirement for secrets, redacted projection, no plaintext/masked values, and status fields. |
| `retrieval_query` | `stable_candidate` | yes | no | Freeze policy-first query filters, scope/depth/status inputs, and backend-neutral options. |
| `retrieval_result` | `stable_candidate` | yes | yes | Freeze hit shape, evidence projection rules, and D3-D5 non-factual semantics. |
| `rule_manifest` | `stable_candidate` | yes | no | Freeze rule metadata, risk/status enums, and required adapter-safe fields. |
| `skill_manifest` | `stable_candidate` | yes | no | Freeze skill metadata, required tool/rule linkage, risk/status enums, and adapter-safe fields. |
| `storage_selector` | `stable_candidate` | yes | yes | Freeze backend-neutral filters/order/limit shape and reject backend-specific query fragments. |
| `tool_binding` | `stable_candidate` | yes | yes | Freeze tool metadata, input/output schema references, capability gates, and explicit network opt-in. |
| `tool_call_result` | `stable_candidate` | yes | yes | Freeze tool result envelope, evidence linkage, status metadata, and protected value leak rejection. |

Open freeze-prep work:

1. Add descriptions to schema fields where a v1.0 implementer could confuse
   reference behavior with standard behavior.
2. Add missing negative fixtures for stable candidates where the rejection rule
   is semantic rather than structural.
3. Decide whether `actor` and `context_capsule_export` are promoted to
   `stable_candidate` or remain draft/reference support.
4. Publish a final v1.0 checklist that blocks release on manifest drift,
   fixture drift, local gate failure, published package smoke failure, or secret
   scan failure.

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
| `actor` | `draft_support` | no | no | Решить, являются ли identity records stable standard records или reference API inputs. |
| `audit_event` | `stable_candidate` | yes | yes | Заморозить content hash semantics, chain metadata, metadata redaction, scope, namespace и lifecycle fields. |
| `benchmark_task` | `reference_only` | no | no | Оставить benchmark pack internals вне core conformance, если они явно не promoted. |
| `benchmark_task_pack` | `reference_only` | no | no | Оставить benchmark pack internals вне core conformance, если они явно не promoted. |
| `capability_grant` | `stable_candidate` | yes | yes | Заморозить deny-by-default, explicit wildcard semantics, scope subset rules, namespace allowlists и depth limits. |
| `context_capsule` | `stable_candidate` | yes | yes | Заморозить canonical checksum, projection rules, permission envelope, evidence references, expiry и forbidden assumptions. |
| `context_capsule_export` | `draft_support` | no | no | Решить, является ли export integrity envelope core v1.0 или reference import/export behavior. |
| `context_operation` | `stable_candidate` | yes | no | Заморозить operation envelope fields, actor/scope/status metadata и audit reference semantics. |
| `evidence_ref` | `stable_candidate` | yes | yes | Заморозить public payload rules, sensitive payload boundary, content hash, URI, status, namespace и scope semantics. |
| `mcp_binding` | `stable_candidate` | yes | no | Заморозить metadata-first binding shape и оставить stdio execution adapter behavior вне core, если он явно не требуется. |
| `memory_call` | `stable_candidate` | yes | yes | Заморозить operation names, intent/read/evidence trace shape, compact prompt metadata и no final-answer synthesis rule. |
| `memory_loop_run` | `stable_candidate` | yes | no | Заморозить loop trace metadata, operation metrics, memory call linkage и adapter-neutral result shape. |
| `memory_operation` | `stable_candidate` | yes | no | Заморозить observe/propose/commit/query/read/correct/forget/blur/sharpen operation envelope fields. |
| `memory_record` | `stable_candidate` | yes | no | Заморозить lifecycle, depth, scope, encrypted content boundary, evidence refs и status metadata. |
| `protected_ref` | `stable_candidate` | yes | yes | Заморозить external provider/URI requirement для secrets, redacted projection, отсутствие plaintext/masked values и status fields. |
| `retrieval_query` | `stable_candidate` | yes | no | Заморозить policy-first query filters, scope/depth/status inputs и backend-neutral options. |
| `retrieval_result` | `stable_candidate` | yes | yes | Заморозить hit shape, evidence projection rules и D3-D5 non-factual semantics. |
| `rule_manifest` | `stable_candidate` | yes | no | Заморозить rule metadata, risk/status enums и required adapter-safe fields. |
| `skill_manifest` | `stable_candidate` | yes | no | Заморозить skill metadata, required tool/rule linkage, risk/status enums и adapter-safe fields. |
| `storage_selector` | `stable_candidate` | yes | yes | Заморозить backend-neutral filters/order/limit shape и reject backend-specific query fragments. |
| `tool_binding` | `stable_candidate` | yes | yes | Заморозить tool metadata, input/output schema references, capability gates и explicit network opt-in. |
| `tool_call_result` | `stable_candidate` | yes | yes | Заморозить tool result envelope, evidence linkage, status metadata и protected value leak rejection. |

Open freeze-prep work:

1. Добавить descriptions к schema fields, где v1.0 implementer может спутать
   reference behavior со standard behavior.
2. Добавить missing negative fixtures для stable candidates, где rejection rule
   semantic, а не structural.
3. Решить, будут ли `actor` и `context_capsule_export` promoted to
   `stable_candidate` или останутся draft/reference support.
4. Опубликовать финальный v1.0 checklist, который блокирует release при
   manifest drift, fixture drift, local gate failure, published package smoke
   failure или secret scan failure.
