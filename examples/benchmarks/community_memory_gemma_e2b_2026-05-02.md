# Community Memory Benchmark, Gemma 4 E2B, 2026-05-02

## EN

This report checks OACS against public community memory datasets, not synthetic
tasks. The goal is to validate whether OACS memory/context helps a small local
model solve memory-dependent tasks with less raw context.

Sources:

- MemoryArena `group_travel_planner`, 15 tasks from
  `ZexueHe/memoryarena`.
- MemoryArena `progressive_search`, 15 tasks from `ZexueHe/memoryarena`.
- AMA-Bench open-ended QA, 15 tasks from `AMA-bench/AMA-bench`.

Model and runtime:

- Provider: LM Studio OpenAI-compatible `/v1/chat/completions`.
- Model: `google/gemma-4-e2b`.
- LM Studio UI chat history was not used; every request was stateless.
- Raw local artifacts: `/tmp/oacs-community-bench-20260502-133443`.

Aggregate results:

| Mode | Success | Avg score | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens | Memory calls | Evidence items |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_no_memory` | 0/45 | 1.0000 | 8,134 | 21,505 | 29,639 | 1.5183 | 0 | 0 |
| `baseline_full_context` | 38/45 | 4.3778 | 133,843 | 22,307 | 156,150 | 1.2616 | 0 | 0 |
| `oacs_memory_loop` | 33/45 | 3.9333 | 151,166 | 23,040 | 174,206 | 1.0160 | 0 | 0 |
| `oacs_memory_call_loop` | 42/45 | 4.7333 | 39,112 | 23,040 | 62,152 | 3.4271 | 90 | 92 |

Per-suite results:

| Suite | Mode | Success | Avg score | Total tokens |
|---|---|---:|---:|---:|
| AMA-Bench open-ended QA | `baseline_no_memory` | 0/15 | 1.0000 | 8,046 |
| AMA-Bench open-ended QA | `baseline_full_context` | 14/15 | 4.7333 | 36,473 |
| AMA-Bench open-ended QA | `oacs_memory_loop` | 13/15 | 4.4667 | 42,263 |
| AMA-Bench open-ended QA | `oacs_memory_call_loop` | 13/15 | 4.4667 | 17,213 |
| MemoryArena group travel | `baseline_no_memory` | 0/15 | 1.0000 | 11,011 |
| MemoryArena group travel | `baseline_full_context` | 11/15 | 3.9333 | 39,399 |
| MemoryArena group travel | `oacs_memory_loop` | 7/15 | 2.8667 | 46,071 |
| MemoryArena group travel | `oacs_memory_call_loop` | 15/15 | 5.0000 | 19,394 |
| MemoryArena progressive search | `baseline_no_memory` | 0/15 | 1.0000 | 10,582 |
| MemoryArena progressive search | `baseline_full_context` | 13/15 | 4.4667 | 80,278 |
| MemoryArena progressive search | `oacs_memory_loop` | 13/15 | 4.4667 | 85,872 |
| MemoryArena progressive search | `oacs_memory_call_loop` | 14/15 | 4.7333 | 25,545 |

Isolation checks:

- Scoped subagent memory tests passed: `19 passed`.
- Manual scoped isolation check:
  - allowed scope memory was returned;
  - blocked scope memory was not returned;
  - blocked memory was not included in the Context Capsule;
  - ungranted sibling subagent access was denied.
- Cross-task expected-fact leakage check on `oacs_memory_call_loop`: `0`
  detected leaks.

Interpretation:

- `baseline_no_memory` fails because the required facts are absent from the
  current prompt.
- `baseline_full_context` is a strong control, but it costs 156k tokens and
  still misses 7/45 tasks.
- The broad `oacs_memory_loop` is not the preferred line for community
  benchmarks: it is more expensive than full context here and less accurate.
- `oacs_memory_call_loop` is the strongest current OACS line: it improves
  success from 38/45 to 42/45 versus raw full context while using about 60%
  fewer total tokens.

## RU

Этот отчёт проверяет OACS на public community memory datasets, а не на
синтетике. Цель - проверить, помогает ли OACS memory/context маленькой локальной
модели решать memory-dependent задачи с меньшим raw context.

Источники:

- MemoryArena `group_travel_planner`, 15 задач из `ZexueHe/memoryarena`.
- MemoryArena `progressive_search`, 15 задач из `ZexueHe/memoryarena`.
- AMA-Bench open-ended QA, 15 задач из `AMA-bench/AMA-bench`.

Модель и runtime:

- Provider: LM Studio OpenAI-compatible `/v1/chat/completions`.
- Model: `google/gemma-4-e2b`.
- История LM Studio UI chat не использовалась; каждый request был stateless.
- Raw local artifacts: `/tmp/oacs-community-bench-20260502-133443`.

Aggregate results:

| Mode | Success | Avg score | Prompt tokens | Output tokens | Total tokens | Score / 1k tokens | Memory calls | Evidence items |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `baseline_no_memory` | 0/45 | 1.0000 | 8,134 | 21,505 | 29,639 | 1.5183 | 0 | 0 |
| `baseline_full_context` | 38/45 | 4.3778 | 133,843 | 22,307 | 156,150 | 1.2616 | 0 | 0 |
| `oacs_memory_loop` | 33/45 | 3.9333 | 151,166 | 23,040 | 174,206 | 1.0160 | 0 | 0 |
| `oacs_memory_call_loop` | 42/45 | 4.7333 | 39,112 | 23,040 | 62,152 | 3.4271 | 90 | 92 |

Вывод:

- `baseline_no_memory` падает, потому что нужных фактов нет в текущем prompt.
- `baseline_full_context` является сильным контролем, но тратит 156k tokens и
  всё равно ошибается на 7/45 задачах.
- Широкий `oacs_memory_loop` не является preferred line для community
  benchmarks: здесь он дороже full context и менее точен.
- `oacs_memory_call_loop` сейчас самая сильная линия OACS: 42/45 против 38/45 у
  raw full context и примерно на 60% меньше total tokens.
