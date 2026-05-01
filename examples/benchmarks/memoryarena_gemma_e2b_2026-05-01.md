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

Estimated tokens use a deterministic character-based approximation, not a
model tokenizer.

| Mode | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 711 | 2419 | 3130 | 1.5974 |
| `baseline_full_context` | 4.2 | 4/5 | 5355 | 2498 | 7853 | 2.6741 |
| `oacs_memory_loop` | 2.6 | 2/5 | 6431 | 2041 | 8472 | 1.5345 |

Interpretation:

- OACS improves over current-task-only prompting: +1.6 average score and +2 exact
  successes.
- OACS is worse than raw full-context prompting on this small 5-task sample:
  -1.6 average score, -2 exact successes, and +619 estimated tokens.
- This means the current OACS POC proves scoped memory helps small-context
  prompting, but it does not yet prove that the current capsule prompt beats a
  short raw full-context baseline when the full context fits comfortably.
- The next benchmark step must test longer histories where raw full context
  grows beyond the practical context budget, and must make the OACS prompt more
  selective than the current memory text inclusion.

Reproduction:

```bash
acs init --db ./.oacs-memoryarena/oacs.db --json
acs key init --db ./.oacs-memoryarena/oacs.db --passphrase "local-passphrase" --json
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

Оценка tokens использует детерминированную character-based approximation, а не
tokenizer конкретной модели.

| Режим | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 711 | 2419 | 3130 | 1.5974 |
| `baseline_full_context` | 4.2 | 4/5 | 5355 | 2498 | 7853 | 2.6741 |
| `oacs_memory_loop` | 2.6 | 2/5 | 6431 | 2041 | 8472 | 1.5345 |

Вывод:

- OACS лучше режима “только текущая задача”: +1.6 среднего score и +2 exact
  successes.
- OACS хуже сырого full-context baseline на этой небольшой выборке: -1.6 среднего
  score, -2 exact successes и +619 estimated tokens.
- Значит текущий POC доказывает пользу scoped memory против малого контекста, но
  пока не доказывает преимущество текущего capsule prompt над коротким raw
  full-context baseline, когда весь контекст помещается.
- Следующий шаг benchmark: длинные истории, где raw full context выходит за
  практический budget, и более селективный OACS prompt без лишнего memory text.
