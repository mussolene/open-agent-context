# Benchmark Validation / Benchmark Validation

## EN
Benchmarks are validation fixtures for the OACS v0.1 draft memory/context
contract. They are not the standard itself and they are not intended to replace
native public benchmark harnesses.

The validation target is not model score by itself. The target is whether
`MemoryRecord`, `ContextCapsule`, `EvidenceRef`, `CapabilityGrant`,
`memory_calls`, and adapter isolation behave consistently under repeatable
tasks.

The benchmark compares:

- `baseline_no_memory`: the model receives only the current task.
- `baseline_full_context`: the model receives raw prior task context plus the current task.
- `oacs_memory_loop`: OACS commits scoped memory, builds a Context Capsule, and prompts
  the model with governed context. This is the reference Context Capsule
  compatibility mode, not the preferred benchmark execution path.
- `oacs_memory_call_loop`: OACS commits scoped memory, records deterministic
  `memory_calls`, extracts structured evidence, and gives the model a compact
  evidence prompt. This is the preferred current execution path for benchmark
  and product validation. Benchmark-only deterministic scoring lives in this
  adapter, not in the core memory loop.

Synthetic tasks are local and deterministic. External adapters are thin import
layers for checking OACS memory/context compatibility, not a replacement for the
native benchmark harnesses. Current adapters cover MemoryArena
`group_travel_planner`, MemoryArena `progressive_search`, and AMA-Bench
open-ended QA trajectory rows. Scoring checks required facts, forbidden facts,
superseded memory handling, clarification behavior, JSON validity, estimated
prompt/output tokens, memory used, `memory_calls`, evidence items, and
audit events. Token estimates are deterministic approximations, not
model-tokenizer counts. In LM Studio mode, OACS records provider usage,
latency, model, and finish reason when the OpenAI-compatible server returns
those fields. LM Studio runs use stateless OpenAI-compatible chat completions:
each request sends only the current `messages` payload, with no LM Studio UI
chat window history or persistent conversation context.

Task packs are imported through `benchmark_task_pack.schema.json`. Packs must
carry an integrity checksum over canonical JSON excluding the integrity field.
Downloads require an explicit URL, expected SHA-256, and `--allow-network`;
local synthetic generation and file imports never use the network by default.
Benchmark comparison reports whether baseline and OACS runs are compatible by
provider, model, and task pack id.

The MemoryArena group-travel adapter does not use natural-language slot aliases
inside benchmark execution. It imports only rows where the reused plan item is
unambiguous from structured answer overlap, writes typed `memory_selectors`, and
skips ambiguous rows instead of guessing from phrases such as "same place".

Current position: broad capsule prompting is kept to prove Context Capsule
compatibility and portability. Structured `memory_calls` plus compact
`EvidenceRef` projection are the recommended line for small models and
long-memory tasks.

## RU
Benchmarks - это validation fixtures для OACS v0.1 draft memory/context
contract. Они не являются самим стандартом и не заменяют native public benchmark
harnesses.

Validation target - не model score сам по себе. Цель проверки - стабильно ли
работают `MemoryRecord`, `ContextCapsule`, `EvidenceRef`, `CapabilityGrant`,
`memory_calls` и adapter isolation на repeatable tasks.

Benchmark сравнивает:

- `baseline_no_memory`: модель получает только текущую задачу.
- `baseline_full_context`: модель получает сырой предыдущий контекст и текущую задачу.
- `oacs_memory_loop`: OACS записывает scoped memory, строит Context Capsule и даёт
  модели управляемый контекст. Это reference compatibility mode для Context
  Capsule, а не preferred benchmark execution path.
- `oacs_memory_call_loop`: OACS записывает scoped memory, фиксирует
  deterministic `memory_calls`, извлекает structured evidence и даёт модели
  compact evidence prompt. Это текущий preferred execution path для benchmark и
  product validation. Benchmark-only deterministic scoring находится в этом
  adapter, а не в core memory loop.

Синтетические задачи локальные и детерминированные. External adapters являются
тонкими import layers для проверки OACS memory/context compatibility, а не
заменой native benchmark harnesses. Сейчас adapters покрывают MemoryArena
`group_travel_planner`, MemoryArena `progressive_search` и AMA-Bench
open-ended QA trajectory rows. Scoring проверяет required facts, forbidden
facts, superseded memory, clarification, JSON validity, estimated prompt/output
tokens, использованную память, `memory_calls`, evidence items и audit
events. Token estimates являются deterministic approximations, а не
tokenizer-specific counts. В LM Studio mode OACS записывает provider usage,
latency, model и finish reason, если OpenAI-compatible server возвращает эти
поля. LM Studio runs используют stateless OpenAI-compatible chat completions:
каждый request отправляет только текущий `messages` payload, без истории UI
chat window LM Studio и без persistent conversation context.

Task packs импортируются через `benchmark_task_pack.schema.json`. Packs должны
содержать integrity checksum по canonical JSON без integrity field. Downloads
требуют явный URL, expected SHA-256 и `--allow-network`; local synthetic
generation и file imports не используют network по умолчанию. Benchmark
comparison показывает, совместимы ли baseline и OACS runs по provider, model и
task pack id.

MemoryArena group-travel adapter не использует natural-language slot aliases во
время benchmark execution. Он импортирует только строки, где reused plan item
однозначен по structured answer overlap, записывает typed `memory_selectors` и
пропускает неоднозначные строки вместо угадывания по фразам вроде "same place".

Текущая позиция: broad capsule prompting остаётся для проверки Context Capsule
compatibility и portability. Structured `memory_calls` плюс compact
`EvidenceRef` projection являются рекомендованной линией для маленьких моделей
и long-memory tasks.

Current technical reports:

- `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`
- `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md`
- `examples/benchmarks/community_memory_gemma_e2b_2026-05-02.md`
