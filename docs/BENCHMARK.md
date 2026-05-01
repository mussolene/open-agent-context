# Benchmark / Benchmark

## EN
The benchmark compares:

- `baseline_no_memory`: the model receives only the current task.
- `baseline_full_context`: the model receives raw prior task context plus the current task.
- `oacs_memory_loop`: OACS commits scoped memory, builds a Context Capsule, and prompts
  the model with governed context.
- `oacs_memory_call_loop`: OACS commits scoped memory, executes deterministic
  `memory_calls`, extracts structured evidence, and gives the model a compact
  evidence prompt.

Synthetic tasks are local and deterministic. External adapters are thin import
layers for checking OACS memory/context compatibility, not a replacement for the
native benchmark harnesses. Current adapters cover MemoryArena
`group_travel_planner`, MemoryArena `progressive_search`, and AMA-Bench
open-ended QA trajectory rows. Scoring checks required facts, forbidden facts,
superseded memory handling, clarification behavior, JSON validity, estimated
prompt/output tokens, memory used, `memory_calls`, evidence items, and
audit events. Token estimates are deterministic approximations, not
model-tokenizer counts.

## RU
Benchmark сравнивает:

- `baseline_no_memory`: модель получает только текущую задачу.
- `baseline_full_context`: модель получает сырой предыдущий контекст и текущую задачу.
- `oacs_memory_loop`: OACS записывает scoped memory, строит Context Capsule и даёт
  модели управляемый контекст.
- `oacs_memory_call_loop`: OACS записывает scoped memory, выполняет
  deterministic `memory_calls`, извлекает structured evidence и даёт модели
  компактный evidence prompt.

Синтетические задачи локальные и детерминированные. External adapters являются
тонкими import layers для проверки OACS memory/context compatibility, а не
заменой native benchmark harnesses. Сейчас adapters покрывают MemoryArena
`group_travel_planner`, MemoryArena `progressive_search` и AMA-Bench
open-ended QA trajectory rows. Scoring проверяет required facts, forbidden
facts, superseded memory, clarification, JSON validity, estimated prompt/output
tokens, использованную память, `memory_calls`, evidence items и audit
events. Token estimates являются deterministic approximations, а не
tokenizer-specific counts.

Current technical report:
`examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.
