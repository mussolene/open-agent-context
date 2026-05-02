# API / API

## EN
FastAPI exposes core reference endpoints for actors, `MemoryRecord` operations,
`ContextCapsule` operations, capability policy, audit, and memory loop runs.
Optional adapter endpoints cover tools, skills, MCP bindings, and validation
benchmarks. All mutating endpoints accept `actor_id` and write audit events.

Context endpoints include `POST /v1/context/build`, `GET /v1/context/{id}`,
`POST /v1/context/{id}/export`, `POST /v1/context/validate`, and
`POST /v1/context/import`. `GET /v1/context/{id}` returns the raw capsule.
`POST /v1/context/{id}/export` returns a `context_capsule_export` envelope with
`capsule` and `integrity` metadata. Validation/import accept either raw capsules
or export envelopes. For envelopes, `integrity.signature` is an HMAC tag, not
public-key signing.

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

Benchmark endpoints accept `provider` and `model` when running tasks. Task pack
import uses schema and checksum validation; downloader paths remain explicit and
network is never used by default.

## RU
FastAPI предоставляет core reference endpoints для actors, операций
`MemoryRecord`, операций `ContextCapsule`, capability policy, audit и memory
loop runs. Optional adapter endpoints покрывают tools, skills, MCP bindings и
validation benchmarks. Все изменяющие endpoints принимают `actor_id` и пишут
audit events.

Context endpoints включают `POST /v1/context/build`, `GET /v1/context/{id}`,
`POST /v1/context/{id}/export`, `POST /v1/context/validate` и
`POST /v1/context/import`. `GET /v1/context/{id}` возвращает raw capsule.
`POST /v1/context/{id}/export` возвращает `context_capsule_export` envelope с
metadata `capsule` и `integrity`. Validation/import принимают raw capsules или
export envelopes. Для envelopes `integrity.signature` является HMAC tag, а не
public-key signing.

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

Benchmark endpoints принимают `provider` и `model` при запуске задач. Import
task packs использует schema и checksum validation; download paths явные, а
network никогда не используется по умолчанию.
