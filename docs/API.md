# API / API

## EN
FastAPI exposes `/health`, `/v1/actors`, memory operations, context operations,
rules, audit, loop, and benchmark endpoints. All mutating endpoints accept
`actor_id` and write audit events.

`POST /v1/loop/run` accepts `user_request`, optional `actor_id`, `agent_id`,
`scope`, `token_budget`, `allowed_tools`, and `model_config`. The response
includes the Context Capsule id, memories used, `memory_calls`, selected
evidence, and compact model prompt.

## RU
FastAPI предоставляет `/health`, `/v1/actors`, операции памяти, операции
context, rules, audit, loop и benchmark endpoints. Все изменяющие endpoints
принимают `actor_id` и пишут audit events.

`POST /v1/loop/run` принимает `user_request`, optional `actor_id`, `agent_id`,
`scope`, `token_budget`, `allowed_tools` и `model_config`. Ответ включает id
Context Capsule, использованную память, `memory_calls`, selected evidence и
compact model prompt.
