# API / API

## EN
FastAPI exposes core reference endpoints for actors, `MemoryRecord` operations,
`ContextCapsule` operations, capability policy, audit, and memory loop runs.
It is a reference interface for the Python package, not the only OACS transport.
Optional adapter endpoints cover tools, skills, MCP bindings, and validation
benchmarks. Memory, context, tool, skill, evidence, and benchmark mutation
endpoints accept `actor_id` where the underlying operation is actor-scoped and
write audit events for those governed operations. Registry and administration
endpoints may use system authority in this reference API.

Context endpoints include `POST /v1/context/build`, `GET /v1/context/{id}`,
`POST /v1/context/{id}/export`, `POST /v1/context/validate`, and
`POST /v1/context/import`. `GET /v1/context/{id}` returns the raw capsule and
checks `context.read`; export checks `context.export` separately.
`POST /v1/context/{id}/export` returns a `context_capsule_export` envelope with
`capsule` and `integrity` metadata. Validation/import accept either raw capsules
or export envelopes. For envelopes, `integrity.mac` is an HMAC tag, not
public-key signing; `integrity.signature` is a deprecated compatibility alias.

`POST /v1/loop/run` accepts `user_request`, optional `actor_id`, `agent_id`,
`scope`, `token_budget`, `allowed_tools`, and `model_config`. The response
includes the Context Capsule id, memories used, `memory_calls`, selected
evidence, compact model prompt, `context_policy` decision, and
`operation_metrics`.

Integration adapter endpoints include capability definitions/grants, tool and
skill inspection, guarded `POST /v1/tools/{id}/call`,
`POST /v1/tools/results/ingest`, `POST /v1/skills/{id}/run`, MCP
import/inspection, and `GET /v1/audit/verify`. Tool and skill calls are checked
through `tool.call` / `skill.run`, explicit resource allowlists, namespace, and
scope. External tool result ingest is checked through `evidence.ingest`.

Tool execution is normalized through `ToolRunner`. A tool call returns a
`ToolCallResult` envelope and records a `tool_result` `EvidenceRef`; HTTP tools
require explicit `http.allow_network=true`. External orchestrators may also
submit already executed tool result envelopes to OACS; OACS hashes, scopes,
audits, and stores them as `tool_result` evidence without selecting or running
the tool.

`ContextCapsule.evidence_refs` is projected from the memories included in the
capsule. A standalone tool-call or ingested tool-result evidence record is
available for inspection by id, but it is not added to a task capsule until a
memory that references it is sharpened and selected by context build.

Benchmark endpoints accept `provider` and `model` when running tasks. Task pack
import uses schema and checksum validation; downloader paths remain explicit and
network is never used by default.

## RU
FastAPI предоставляет core reference endpoints для actors, операций
`MemoryRecord`, операций `ContextCapsule`, capability policy, audit и memory
loop runs. Это reference interface для Python package, а не единственный OACS
transport. Optional adapter endpoints покрывают tools, skills, MCP bindings и
validation benchmarks. Mutation endpoints для memory, context, tools, skills,
evidence и benchmarks принимают `actor_id`, когда underlying operation
actor-scoped, и пишут audit events для таких governed operations. Registry и
administration endpoints могут использовать system authority в этом reference
API.

Context endpoints включают `POST /v1/context/build`, `GET /v1/context/{id}`,
`POST /v1/context/{id}/export`, `POST /v1/context/validate` и
`POST /v1/context/import`. `GET /v1/context/{id}` возвращает raw capsule и
проверяет `context.read`; export отдельно проверяет `context.export`.
`POST /v1/context/{id}/export` возвращает `context_capsule_export` envelope с
metadata `capsule` и `integrity`. Validation/import принимают raw capsules или
export envelopes. Для envelopes `integrity.mac` является HMAC tag, а не
public-key signing; `integrity.signature` - deprecated compatibility alias.

`POST /v1/loop/run` принимает `user_request`, optional `actor_id`, `agent_id`,
`scope`, `token_budget`, `allowed_tools` и `model_config`. Ответ включает id
Context Capsule, использованную память, `memory_calls`, selected evidence и
compact model prompt, а также `context_policy` decision и `operation_metrics`.

Integration adapter endpoints включают capability definitions/grants, inspect
для tools и skills, защищённые `POST /v1/tools/{id}/call`,
`POST /v1/tools/results/ingest`, `POST /v1/skills/{id}/run`, MCP
import/inspection и `GET /v1/audit/verify`. Tool и skill calls проверяются
через `tool.call` / `skill.run`, explicit resource allowlists, namespace и
scope. Ingest внешних результатов tools проверяется через `evidence.ingest`.

Tool execution нормализован через `ToolRunner`. Tool call возвращает
`ToolCallResult` envelope и записывает `tool_result` `EvidenceRef`; HTTP tools
требуют явный `http.allow_network=true`. Внешние orchestrators также могут
передать в OACS уже выполненный tool result envelope; OACS хеширует, scope-ит,
аудирует и сохраняет его как `tool_result` evidence без выбора или запуска tool.

`ContextCapsule.evidence_refs` проецируется из memories, включённых в capsule.
Standalone tool-call или ingested tool-result evidence record можно посмотреть
по id, но он не добавляется в task capsule, пока memory, которая на него
ссылается, не будет sharpened и выбрана context build.

Benchmark endpoints принимают `provider` и `model` при запуске задач. Import
task packs использует schema и checksum validation; download paths явные, а
network никогда не используется по умолчанию.
