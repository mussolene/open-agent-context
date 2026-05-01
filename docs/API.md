# API / API

## EN
FastAPI exposes `/health`, `/v1/actors`, memory operations, context operations,
rules, audit, loop, and benchmark endpoints. All mutating endpoints accept
`actor_id` and write audit events.

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

## RU
FastAPI предоставляет `/health`, `/v1/actors`, операции памяти, операции
context, rules, audit, loop и benchmark endpoints. Все изменяющие endpoints
принимают `actor_id` и пишут audit events.

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
