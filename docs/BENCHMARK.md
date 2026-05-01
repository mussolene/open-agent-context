# Benchmark / Benchmark

## EN
The benchmark compares:

- `baseline_no_memory`: the model receives only the current task.
- `baseline_full_context`: the model receives raw prior task context plus the current task.
- `oacs_memory_loop`: OACS commits scoped memory, builds a Context Capsule, and prompts
  the model with governed context.

Synthetic tasks are local and deterministic. External adapters can import open
benchmark data such as MemoryArena. Scoring checks required facts, forbidden
facts, superseded memory handling, clarification behavior, JSON validity,
estimated prompt/output tokens, memory used, and audit events.

## RU
Benchmark сравнивает:

- `baseline_no_memory`: модель получает только текущую задачу.
- `baseline_full_context`: модель получает сырой предыдущий контекст и текущую задачу.
- `oacs_memory_loop`: OACS записывает scoped memory, строит Context Capsule и даёт
  модели управляемый контекст.

Синтетические задачи локальные и детерминированные. External adapters могут
импортировать открытые benchmark data, например MemoryArena. Scoring проверяет
required facts, forbidden facts, superseded memory, clarification, JSON validity,
estimated prompt/output tokens, использованную память и audit events.
