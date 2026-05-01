# Memory Calls Benchmark Report / Отчёт по Memory Calls

## EN

Status: OACS v0.2.7 reference implementation.
Date: 2026-05-01.
Model: `google/gemma-4-e2b` through LM Studio OpenAI-compatible API.
Tasks per suite: 5.
Token metric: deterministic character-based estimate, not a model tokenizer.

`oacs_memory_call_loop` is the OACS v0.2.7 benchmark mode for deterministic
memory operations. It executes `memory_calls` (`memory.query`,
`memory.extract_evidence`) and returns the full machine-readable call trace in
benchmark results. The model prompt receives only a compact projection of the
trace plus the extracted evidence, so auditability does not require prompt
stuffing.

Selector cleanup note: after the selector split, a quickstart smoke run on 5
synthetic tasks produced `baseline_no_memory` 0/5 and `oacs_memory_call_loop`
5/5, `memory_calls_count` 10, estimated OACS tokens 1,207, and
`acs benchmark compare` improvement `+4.0`. The LM Studio tables below remain
the latest real-model run.

Fairness note: the current MemoryArena group-travel adapter no longer uses
natural-language slot aliases during benchmark execution. It accepts only
unambiguous structured answer overlaps and skips ambiguous rows.

### Deterministic Provider

| Suite | Mode | Success | Avg score | Prompt tokens | Output tokens | Total tokens | Memory calls | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Synthetic memory-critical | `baseline_no_memory` | 0/5 | 1.0 | 60 | 85 | 145 | 0 | 0 |
| Synthetic memory-critical | `baseline_full_context` | 4/5 | 4.8 | 361 | 386 | 747 | 0 | 0 |
| Synthetic memory-critical | `oacs_memory_loop` | 5/5 | 5.0 | 60 | 154 | 214 | 0 | 0 |
| Synthetic memory-critical | `oacs_memory_call_loop` | 5/5 | 5.0 | 1,073 | 194 | 1,267 | 10 | 5 |
| MemoryArena group travel | `baseline_no_memory` | 0/5 | 1.0 | 688 | 713 | 1,401 | 0 | 0 |
| MemoryArena group travel | `baseline_full_context` | 5/5 | 5.0 | 5,776 | 5,801 | 11,577 | 0 | 0 |
| MemoryArena group travel | `oacs_memory_loop` | 5/5 | 5.0 | 688 | 5,205 | 5,893 | 0 | 0 |
| MemoryArena group travel | `oacs_memory_call_loop` | 5/5 | 5.0 | 2,948 | 716 | 3,664 | 10 | 29 |
| MemoryArena progressive search | `baseline_no_memory` | 0/5 | 1.0 | 1,036 | 1,061 | 2,097 | 0 | 0 |
| MemoryArena progressive search | `baseline_full_context` | 5/5 | 5.0 | 25,424 | 25,449 | 50,873 | 0 | 0 |
| MemoryArena progressive search | `oacs_memory_loop` | 5/5 | 5.0 | 1,036 | 23,346 | 24,382 | 0 | 0 |
| MemoryArena progressive search | `oacs_memory_call_loop` | 5/5 | 5.0 | 5,037 | 3,207 | 8,244 | 10 | 5 |
| AMA-Bench open-ended QA | `baseline_no_memory` | 0/5 | 1.0 | 397 | 422 | 819 | 0 | 0 |
| AMA-Bench open-ended QA | `baseline_full_context` | 5/5 | 5.0 | 9,487 | 9,512 | 18,999 | 0 | 0 |
| AMA-Bench open-ended QA | `oacs_memory_loop` | 5/5 | 5.0 | 397 | 8,929 | 9,326 | 0 | 0 |
| AMA-Bench open-ended QA | `oacs_memory_call_loop` | 5/5 | 5.0 | 1,824 | 629 | 2,453 | 10 | 5 |

### LM Studio Gemma e2b

| Suite | Mode | Success | Avg score | Prompt tokens | Output tokens | Total tokens | Memory calls | Evidence | Wall time |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Synthetic memory-critical | `baseline_no_memory` | 0/5 | 1.0 | 60 | 1,492 | 1,552 | 0 | 0 | 40.9s |
| Synthetic memory-critical | `baseline_full_context` | 4/5 | 4.8 | 361 | 1,320 | 1,681 | 0 | 0 | 37.9s |
| Synthetic memory-critical | `oacs_memory_loop` | 5/5 | 5.0 | 994 | 1,730 | 2,724 | 0 | 0 | 67.6s |
| Synthetic memory-critical | `oacs_memory_call_loop` | 5/5 | 5.0 | 1,073 | 2,769 | 3,842 | 10 | 5 | 72.9s |
| MemoryArena group travel | `baseline_no_memory` | 0/5 | 1.0 | 688 | 2,258 | 2,946 | 0 | 0 | 51.7s |
| MemoryArena group travel | `baseline_full_context` | 5/5 | 5.0 | 5,776 | 2,585 | 8,361 | 0 | 0 | 67.1s |
| MemoryArena group travel | `oacs_memory_loop` | 4/5 | 4.2 | 6,805 | 2,141 | 8,946 | 0 | 0 | 83.0s |
| MemoryArena group travel | `oacs_memory_call_loop` | 5/5 | 5.0 | 2,948 | 3,065 | 6,013 | 10 | 29 | 69.2s |
| MemoryArena progressive search | `baseline_no_memory` | 0/5 | 1.0 | 1,036 | 2,876 | 3,912 | 0 | 0 | 65.4s |
| MemoryArena progressive search | `baseline_full_context` | 5/5 | 5.0 | 25,424 | 2,133 | 27,557 | 0 | 0 | 137.0s |
| MemoryArena progressive search | `oacs_memory_loop` | 5/5 | 5.0 | 26,102 | 2,195 | 28,297 | 0 | 0 | 156.2s |
| MemoryArena progressive search | `oacs_memory_call_loop` | 5/5 | 5.0 | 5,037 | 5,725 | 10,762 | 10 | 5 | 77.6s |
| AMA-Bench open-ended QA | `baseline_no_memory` | 0/5 | 1.0 | 397 | 2,509 | 2,906 | 0 | 0 | 62.6s |
| AMA-Bench open-ended QA | `baseline_full_context` | 5/5 | 5.0 | 9,487 | 2,552 | 12,039 | 0 | 0 | 102.1s |
| AMA-Bench open-ended QA | `oacs_memory_loop` | 5/5 | 5.0 | 10,198 | 2,317 | 12,515 | 0 | 0 | 103.3s |
| AMA-Bench open-ended QA | `oacs_memory_call_loop` | 5/5 | 5.0 | 1,824 | 3,282 | 5,106 | 10 | 5 | 72.0s |

### Interpretation

- `memory_calls` make the memory trace explicit without depending on backend
  native tool-calling support.
- The mode is strongest on medium, large, and long-reasoning memory tasks:
  - MemoryArena group travel: 5/5 with 28.1% fewer total tokens than raw full
    context in LM Studio.
  - MemoryArena progressive search: 5/5 with 61.0% fewer total tokens and much
    lower wall time than raw full context.
  - AMA-Bench open-ended QA: 5/5 with 57.6% fewer total tokens than raw full
    context.
- Tiny synthetic tasks still show overhead. `oacs_memory_call_loop` improves
  relevance from 4/5 to 5/5 against raw full context, but costs more tokens.

## RU

Статус: OACS v0.2.7 reference implementation.
Дата: 2026-05-01.
Модель: `google/gemma-4-e2b` через LM Studio OpenAI-compatible API.
Задач на suite: 5.
Метрика tokens: deterministic character-based estimate, не tokenizer модели.

`oacs_memory_call_loop` — benchmark mode OACS v0.2.7 для deterministic memory
operations. Он выполняет `memory_calls` (`memory.query`,
`memory.extract_evidence`) и возвращает полный machine-readable call trace в
benchmark results. В prompt модели попадает только компактная projection trace
и extracted evidence, поэтому auditability не требует prompt stuffing.

Selector cleanup note: после selector split quickstart smoke run на 5 synthetic
tasks дал `baseline_no_memory` 0/5 и `oacs_memory_call_loop` 5/5, а
`memory_calls_count` 10, estimated OACS tokens 1,207 и
`acs benchmark compare` improvement `+4.0`. Таблицы LM Studio ниже остаются
последним real-model прогоном.

Fairness note: текущий MemoryArena group-travel adapter больше не использует
natural-language slot aliases во время benchmark execution. Он принимает только
однозначные structured answer overlaps и пропускает неоднозначные строки.

Вывод:

- `memory_calls` делают memory trace явным и не зависят от native tool calling
  конкретного backend.
- Режим сильнее всего на medium, large и long-reasoning memory tasks:
  - MemoryArena group travel: 5/5 и на 28.1% меньше total tokens, чем raw full
    context в LM Studio.
  - MemoryArena progressive search: 5/5, на 61.0% меньше total tokens и заметно
    ниже wall time, чем raw full context.
  - AMA-Bench open-ended QA: 5/5 и на 57.6% меньше total tokens, чем raw full
    context.
- На tiny synthetic tasks overhead сохраняется. `oacs_memory_call_loop`
  повышает relevance с 4/5 до 5/5 против raw full context, но стоит дороже по
  tokens.
