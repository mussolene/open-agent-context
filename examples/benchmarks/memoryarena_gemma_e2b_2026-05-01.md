# MemoryArena Gemma e2b external benchmark / Внешний benchmark

## EN

Source dataset: `ZexueHe/memoryarena`, subset `group_travel_planner`.
Model: `google/gemma-4-e2b` through LM Studio OpenAI-compatible API.
Date: 2026-05-01.
Tasks: first 5 rows converted into memory-dependent OACS tasks.

Modes:

- `baseline_no_memory`: current task only.
- `baseline_full_context`: raw prior context plus current task.
- `oacs_memory_loop`: scoped OACS memories plus Context Capsule prompt.
- `oacs_memory_tool_loop`: scoped OACS memories plus deterministic MCP-like
  memory operations that extract participant/day/slot evidence before prompting.

Estimated tokens use a deterministic character-based approximation, not a
model tokenizer.

| Mode | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 711 | 2522 | 3233 | 1.5466 |
| `baseline_full_context` | 4.2 | 4/5 | 5355 | 2405 | 7760 | 2.7062 |
| `oacs_memory_loop` | 1.8 | 1/5 | 6431 | 1989 | 8420 | 1.0689 |
| `oacs_memory_tool_loop` | 5.0 | 5/5 | 2536 | 2743 | 5279 | 4.7357 |

Interpretation:

- The basic `oacs_memory_loop` is not enough; it still behaves like broad
  context injection and underperforms raw full context here.
- The `oacs_memory_tool_loop` is the intended OACS shape: deterministic memory
  operations first, compact evidence prompt second.
- `oacs_memory_tool_loop` beats raw full context on this sample: +0.8 average
  score, +1 exact success, and -2481 estimated total tokens.
- This supports the roadmap direction: OACS should be a thin memory-tool layer
  under agents, not just a memory database or prompt stuffing helper.

### Public Deterministic Harness: 20 Tasks

The same public MemoryArena subset was also run through the deterministic
benchmark provider on 20 memory-supported tasks. This isolates the OACS
memory-tool layer from model variance and checks whether the adapter extracts
the correct evidence for tasks OACS is currently designed to solve.

| Mode | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/20 | 3824 | 3924 | 7748 | 2.5813 |
| `baseline_full_context` | 5.0 | 20/20 | 32805 | 32905 | 65710 | 1.5218 |
| `oacs_memory_loop` | 5.0 | 20/20 | 3824 | 30165 | 33989 | 2.9421 |
| `oacs_memory_tool_loop` | 5.0 | 20/20 | 13263 | 3075 | 16338 | 6.1207 |

Interpretation:

- On the supported memory-reuse class, `oacs_memory_tool_loop` preserves full
  accuracy while using far fewer tokens than raw full context.
- MemoryArena questions that require solving new constraints against an external
  environment are intentionally not claimed as solved by this adapter yet; they
  belong to a future tool/runtime benchmark layer.

Reproduction:

```bash
acs init --db ./.oacs-memoryarena/oacs.db --json
ACS_PASSPHRASE="<choose-a-local-dev-passphrase>"
acs key init --db ./.oacs-memoryarena/oacs.db --passphrase "$ACS_PASSPHRASE" --json
acs benchmark import-memoryarena \
  --db ./.oacs-memoryarena/oacs.db \
  --subset group_travel_planner \
  --count 5 \
  --json
acs benchmark run \
  --db ./.oacs-memoryarena/oacs.db \
  --mode baseline_no_memory \
  --provider lmstudio \
  --model google/gemma-4-e2b \
  --json
acs benchmark run \
  --db ./.oacs-memoryarena/oacs.db \
  --mode baseline_full_context \
  --provider lmstudio \
  --model google/gemma-4-e2b \
  --json
acs benchmark run \
  --db ./.oacs-memoryarena/oacs.db \
  --mode oacs_memory_loop \
  --provider lmstudio \
  --model google/gemma-4-e2b \
  --json
acs benchmark run \
  --db ./.oacs-memoryarena/oacs.db \
  --mode oacs_memory_tool_loop \
  --provider lmstudio \
  --model google/gemma-4-e2b \
  --json
```

## RU

Источник данных: `ZexueHe/memoryarena`, subset `group_travel_planner`.
Модель: `google/gemma-4-e2b` через LM Studio OpenAI-compatible API.
Дата: 2026-05-01.
Задачи: первые 5 строк преобразованы в memory-dependent OACS tasks.

Режимы:

- `baseline_no_memory`: только текущая задача.
- `baseline_full_context`: сырой предыдущий контекст плюс текущая задача.
- `oacs_memory_loop`: scoped OACS memories плюс Context Capsule prompt.
- `oacs_memory_tool_loop`: scoped OACS memories плюс deterministic MCP-like
  memory operations, которые извлекают participant/day/slot evidence до prompt.

Оценка tokens использует детерминированную character-based approximation, а не
tokenizer конкретной модели.

| Режим | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 711 | 2522 | 3233 | 1.5466 |
| `baseline_full_context` | 4.2 | 4/5 | 5355 | 2405 | 7760 | 2.7062 |
| `oacs_memory_loop` | 1.8 | 1/5 | 6431 | 1989 | 8420 | 1.0689 |
| `oacs_memory_tool_loop` | 5.0 | 5/5 | 2536 | 2743 | 5279 | 4.7357 |

Вывод:

- Базовый `oacs_memory_loop` недостаточен: он всё ещё похож на broad context
  injection и здесь проигрывает raw full context.
- `oacs_memory_tool_loop` соответствует целевой форме OACS: сначала
  deterministic memory operations, затем компактный evidence prompt.
- `oacs_memory_tool_loop` выигрывает у raw full context на этой выборке: +0.8
  среднего score, +1 exact success и -2481 estimated total tokens.
- Это поддерживает roadmap: OACS должен быть тонким memory-tool layer под
  агентами, а не только memory database или prompt stuffing helper.

### Public Deterministic Harness: 20 задач

Тот же public subset MemoryArena был дополнительно прогнан через deterministic
benchmark provider на 20 memory-supported задачах. Это изолирует OACS
memory-tool layer от model variance и проверяет, достаёт ли adapter правильное
evidence для класса задач, который OACS уже должен решать.

| Режим | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/20 | 3824 | 3924 | 7748 | 2.5813 |
| `baseline_full_context` | 5.0 | 20/20 | 32805 | 32905 | 65710 | 1.5218 |
| `oacs_memory_loop` | 5.0 | 20/20 | 3824 | 30165 | 33989 | 2.9421 |
| `oacs_memory_tool_loop` | 5.0 | 20/20 | 13263 | 3075 | 16338 | 6.1207 |

Вывод:

- На поддержанном классе memory-reuse задач `oacs_memory_tool_loop` сохраняет
  полную точность и использует заметно меньше tokens, чем raw full context.
- MemoryArena questions, где нужно решать новые constraints через внешнюю
  environment, пока честно не заявлены как решённые этим adapter; это будущий
  tool/runtime benchmark layer.
