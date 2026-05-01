# Gemma e2b Context Scale Report / Отчёт по масштабу контекста Gemma e2b

## EN

Status: OACS v0.1 draft validation run.
Date: 2026-05-01.
Model: `google/gemma-4-e2b` through LM Studio OpenAI-compatible API.
Tasks per suite: 5.
Token metric: deterministic character-based estimate, not a model tokenizer.

This report compares current-task-only prompting, raw full-context prompting,
the current OACS Context Capsule path, and the MCP-like OACS memory-tool path.
It is a reference-implementation validation report, not a change to the OACS
standard.

| Suite | Context shape | Mode | Success | Avg score | Prompt tokens | Output tokens | Total tokens | Wall time |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Synthetic memory-critical | Small controlled memory | `baseline_no_memory` | 0/5 | 1.0 | 60 | 1,474 | 1,534 | 31.6s |
| Synthetic memory-critical | Small controlled memory | `baseline_full_context` | 4/5 | 4.8 | 355 | 1,749 | 2,104 | 37.1s |
| Synthetic memory-critical | Small controlled memory | `oacs_memory_loop` | 5/5 | 5.0 | 1,185 | 2,011 | 3,196 | 56.4s |
| Synthetic memory-critical | Small controlled memory | `oacs_memory_tool_loop` | 0/5 | 1.0 | 800 | 1,953 | 2,753 | 43.7s |
| MemoryArena group travel | Medium structured reuse | `baseline_no_memory` | 0/5 | 1.0 | 688 | 2,380 | 3,068 | 46.0s |
| MemoryArena group travel | Medium structured reuse | `baseline_full_context` | 5/5 | 5.0 | 5,776 | 2,540 | 8,316 | 59.2s |
| MemoryArena group travel | Medium structured reuse | `oacs_memory_loop` | 4/5 | 4.2 | 6,805 | 2,069 | 8,874 | 73.1s |
| MemoryArena group travel | Medium structured reuse | `oacs_memory_tool_loop` | 5/5 | 5.0 | 2,296 | 2,743 | 5,039 | 60.3s |
| MemoryArena progressive search | Large accumulated context | `baseline_no_memory` | 0/5 | 1.0 | 1,036 | 2,854 | 3,890 | 57.3s |
| MemoryArena progressive search | Large accumulated context | `baseline_full_context` | 5/5 | 5.0 | 25,424 | 2,294 | 27,718 | 127.6s |
| MemoryArena progressive search | Large accumulated context | `oacs_memory_loop` | 5/5 | 5.0 | 26,102 | 1,999 | 28,101 | 140.6s |
| MemoryArena progressive search | Large accumulated context | `oacs_memory_tool_loop` | 5/5 | 5.0 | 4,959 | 5,755 | 10,714 | 66.5s |
| AMA-Bench open-ended QA | Long trajectory reasoning | `baseline_no_memory` | 0/5 | 1.0 | 397 | 2,431 | 2,828 | 50.7s |
| AMA-Bench open-ended QA | Long trajectory reasoning | `baseline_full_context` | 5/5 | 5.0 | 9,487 | 2,491 | 11,978 | 81.7s |
| AMA-Bench open-ended QA | Long trajectory reasoning | `oacs_memory_loop` | 5/5 | 5.0 | 10,198 | 2,286 | 12,484 | 87.8s |
| AMA-Bench open-ended QA | Long trajectory reasoning | `oacs_memory_tool_loop` | 5/5 | 5.0 | 1,754 | 3,238 | 4,992 | 59.0s |

### What Improved

- Medium and large public memory tasks benefit from deterministic memory tools.
  Compared with raw full-context prompting, `oacs_memory_tool_loop` kept 5/5
  success and used fewer estimated total tokens:
  - MemoryArena group travel: 39.4% fewer total tokens.
  - MemoryArena progressive search: 61.3% fewer total tokens.
  - AMA-Bench open-ended QA: 58.3% fewer total tokens.
- Long-context wall time improved where the tool layer reduced prompt size:
  progressive search dropped from 127.6s to 66.5s.
- The no-memory baseline failed all suites, which supports the core OACS claim:
  these tasks require external memory/context, not only model recall.

### What Got Worse

- Small synthetic tasks show OACS overhead. `oacs_memory_loop` reached 5/5, but
  used more tokens than raw full context on a tiny context window.
- `oacs_memory_tool_loop` failed the synthetic suite because its extractor does
  not understand the synthetic benchmark memory format. That is a coverage gap,
  not a model limitation.
- The current Context Capsule path is still broad-context assembly. On public
  memory tasks it often matches accuracy, but it does not reduce prompt size.

### Standards Check

No OACS standard behavior changed in this run. The implementation still treats
public benchmark adapters as validation layers, not as standard entities.

The main architecture gap is that `oacs/loop/memory_tools.py` currently parses
benchmark-specific text markers such as `Exact accepted plan`, `Accepted answer`,
and `AMA-Bench evidence answer`. That behavior is useful for validation, but it
is not a clean OACS standard contract. The standard-aligned fix is to move these
parsers into adapter-local code or store adapter output as structured
`EvidenceRef` / typed `MemoryRecord.content` fields, then let the generic memory
tool loop consume structured evidence only.

### Context Breakpoints

- Tiny context: raw full context can be cheaper than OACS because governance and
  capsule/tool metadata dominate the prompt.
- Medium context: OACS memory tools start paying off when reusable evidence can
  replace several kilotokens of raw trace.
- Large accumulated context: OACS memory tools are materially better. Progressive
  search preserved success with 10,714 total estimated tokens instead of 27,718.
- Long trajectory reasoning: compact evidence retrieval preserved success and
  cut estimated total tokens from 11,978 to 4,992.

## RU

Статус: validation run для OACS v0.1 draft.
Дата: 2026-05-01.
Модель: `google/gemma-4-e2b` через LM Studio OpenAI-compatible API.
Задач на suite: 5.
Метрика tokens: deterministic character-based estimate, не tokenizer модели.

Этот отчёт сравнивает current-task-only prompting, raw full-context prompting,
текущий OACS Context Capsule path и MCP-like OACS memory-tool path. Это отчёт
по reference implementation, а не изменение стандарта OACS.

### Что стало лучше

- На medium и large public memory tasks deterministic memory tools дают пользу.
  По сравнению с raw full context `oacs_memory_tool_loop` сохранил 5/5 success и
  снизил estimated total tokens:
  - MemoryArena group travel: на 39.4%.
  - MemoryArena progressive search: на 61.3%.
  - AMA-Bench open-ended QA: на 58.3%.
- На long-context задачах wall time тоже снизился там, где tool layer уменьшил
  prompt: progressive search упал со 127.6s до 66.5s.
- No-memory baseline провалился на всех suites. Это поддерживает главную идею
  OACS: таким задачам нужна внешняя memory/context layer, а не только память
  модели.

### Что стало хуже

- На маленьких synthetic tasks OACS overhead заметен. `oacs_memory_loop` дал
  5/5, но потратил больше tokens, чем raw full context на маленьком контексте.
- `oacs_memory_tool_loop` провалил synthetic suite, потому что extractor не
  понимает synthetic benchmark memory format. Это gap покрытия, а не ограничение
  модели.
- Текущий Context Capsule path пока похож на broad-context assembly. На public
  memory tasks он часто сохраняет accuracy, но не уменьшает prompt size.

### Проверка стандарта

Поведение стандарта OACS в этом прогоне не менялось. Public benchmark adapters
остаются validation layers, а не standard entities.

Главный архитектурный gap: `oacs/loop/memory_tools.py` сейчас парсит
benchmark-specific text markers, например `Exact accepted plan`, `Accepted
answer` и `AMA-Bench evidence answer`. Это полезно для валидации, но не является
чистым стандартным контрактом OACS. Правильный следующий шаг: вынести эти
parsers в adapter-local code или сохранять adapter output как structured
`EvidenceRef` / typed `MemoryRecord.content`, после чего generic memory tool loop
должен потреблять только структурированное evidence.

### Точки перелома по контексту

- Tiny context: raw full context может быть дешевле OACS, потому что governance и
  capsule/tool metadata занимают существенную долю prompt.
- Medium context: OACS memory tools начинают окупаться, когда reusable evidence
  заменяет несколько kilotokens raw trace.
- Large accumulated context: OACS memory tools дают существенную пользу.
  Progressive search сохранил success при 10,714 estimated total tokens вместо
  27,718.
- Long trajectory reasoning: compact evidence retrieval сохранил success и
  снизил estimated total tokens с 11,978 до 4,992.
