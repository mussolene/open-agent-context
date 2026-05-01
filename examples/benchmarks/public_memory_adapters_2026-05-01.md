# Public Memory Adapters Token Report / Token Report публичных адаптеров

## EN

Status: OACS v0.1 draft validation run.
Date: 2026-05-01.
Provider: deterministic OACS benchmark provider.
Token metric: deterministic character-based estimate, not a model tokenizer.

These runs validate thin OACS import adapters only. They are not replacements
for the native MemoryArena or AMA-Bench harnesses.

### MemoryArena `progressive_search`

Source: `ZexueHe/memoryarena`, first 5 `progressive_search` rows converted to
OACS memory tasks.

| Mode | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 1,036 | 1,061 | 2,097 | 2.3844 |
| `baseline_full_context` | 5.0 | 5/5 | 25,424 | 25,449 | 50,873 | 0.4914 |
| `oacs_memory_loop` | 5.0 | 5/5 | 1,036 | 23,346 | 24,382 | 1.0253 |
| `oacs_memory_call_loop` | 5.0 | 5/5 | 4,959 | 3,207 | 8,166 | 3.0615 |

Result: `oacs_memory_call_loop` preserved 5/5 success while using 83.9% fewer
estimated total tokens than raw full context.

### AMA-Bench `open_end_qa_set`

Source: `AMA-bench/AMA-bench`, first 5 `open_end_qa_set` rows converted to OACS
trajectory-memory tasks.

| Mode | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 397 | 422 | 819 | 6.1050 |
| `baseline_full_context` | 5.0 | 5/5 | 9,487 | 9,512 | 18,999 | 1.3159 |
| `oacs_memory_loop` | 5.0 | 5/5 | 397 | 8,929 | 9,326 | 2.6807 |
| `oacs_memory_call_loop` | 5.0 | 5/5 | 1,754 | 629 | 2,383 | 10.4910 |

Result: `oacs_memory_call_loop` preserved 5/5 success while using 87.5% fewer
estimated total tokens than raw full context.

## RU

Статус: validation run для OACS v0.1 draft.
Дата: 2026-05-01.
Provider: deterministic OACS benchmark provider.
Метрика tokens: deterministic character-based estimate, не tokenizer модели.

Эти прогоны валидируют только thin OACS import adapters. Это не замена native
MemoryArena или AMA-Bench harnesses.

### MemoryArena `progressive_search`

Источник: `ZexueHe/memoryarena`, первые 5 строк `progressive_search`
преобразованы в OACS memory tasks.

| Режим | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 1,036 | 1,061 | 2,097 | 2.3844 |
| `baseline_full_context` | 5.0 | 5/5 | 25,424 | 25,449 | 50,873 | 0.4914 |
| `oacs_memory_loop` | 5.0 | 5/5 | 1,036 | 23,346 | 24,382 | 1.0253 |
| `oacs_memory_call_loop` | 5.0 | 5/5 | 4,959 | 3,207 | 8,166 | 3.0615 |

Вывод: `oacs_memory_call_loop` сохранил 5/5 success и использовал на 83.9%
меньше estimated total tokens, чем raw full context.

### AMA-Bench `open_end_qa_set`

Источник: `AMA-bench/AMA-bench`, первые 5 строк `open_end_qa_set`
преобразованы в OACS trajectory-memory tasks.

| Режим | Avg score | Exact success | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_no_memory` | 1.0 | 0/5 | 397 | 422 | 819 | 6.1050 |
| `baseline_full_context` | 5.0 | 5/5 | 9,487 | 9,512 | 18,999 | 1.3159 |
| `oacs_memory_loop` | 5.0 | 5/5 | 397 | 8,929 | 9,326 | 2.6807 |
| `oacs_memory_call_loop` | 5.0 | 5/5 | 1,754 | 629 | 2,383 | 10.4910 |

Вывод: `oacs_memory_call_loop` сохранил 5/5 success и использовал на 87.5%
меньше estimated total tokens, чем raw full context.
