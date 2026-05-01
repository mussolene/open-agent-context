# Structured Evidence Refactor Report / Отчёт по structured evidence

## EN

Status: OACS v0.1 draft reference implementation moving toward v0.2.
Date: 2026-05-01.

The benchmark-specific parsing gap has been closed in the core memory-tool loop.
`oacs/loop/memory_tools.py` no longer parses MemoryArena or AMA-Bench text
markers. Public adapters and synthetic tasks now write typed evidence into
`MemoryRecord.content.evidence`, and the generic memory-tool loop consumes only
that structured shape.

### Deterministic Verification

Tasks per suite: 5.

| Suite | Mode | Success | Evidence items | Total tokens |
| --- | --- | ---: | ---: | ---: |
| Synthetic memory-critical | `baseline_full_context` | 4/5 | 0 | 747 |
| Synthetic memory-critical | `oacs_memory_loop` | 5/5 | 0 | 214 |
| Synthetic memory-critical | `oacs_memory_tool_loop` | 5/5 | 5 | 1,097 |
| MemoryArena group travel | `baseline_full_context` | 5/5 | 0 | 11,577 |
| MemoryArena group travel | `oacs_memory_loop` | 5/5 | 0 | 5,893 |
| MemoryArena group travel | `oacs_memory_tool_loop` | 5/5 | 29 | 3,493 |
| MemoryArena progressive search | `baseline_full_context` | 5/5 | 0 | 50,873 |
| MemoryArena progressive search | `oacs_memory_loop` | 5/5 | 0 | 24,382 |
| MemoryArena progressive search | `oacs_memory_tool_loop` | 5/5 | 5 | 8,071 |
| AMA-Bench open-ended QA | `baseline_full_context` | 5/5 | 0 | 18,999 |
| AMA-Bench open-ended QA | `oacs_memory_loop` | 5/5 | 0 | 9,326 |
| AMA-Bench open-ended QA | `oacs_memory_tool_loop` | 5/5 | 5 | 2,282 |

### LM Studio Spot Check

Model: `google/gemma-4-e2b`.
Suite: synthetic memory-critical, 5 tasks.

| Mode | Success | Avg score | Evidence items | Total tokens | Wall time |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_full_context` | 4/5 | 4.8 | 0 | 1,634 | 41.9s |
| `oacs_memory_loop` | 5/5 | 5.0 | 0 | 2,854 | 80.3s |
| `oacs_memory_tool_loop` | 5/5 | 5.0 | 5 | 3,705 | 79.8s |

This directly fixes the prior `oacs_memory_tool_loop` synthetic failure. The
tool loop is now generic over structured evidence, not benchmark marker strings.

### Remaining Gap

The structured evidence path is still a reference implementation contract, not a
frozen v1.0 standard schema. v0.2 should promote it into stable OACS tool calls
and define conformance checks for adapters.

### Proof-loop Dogfood

The current development iteration was also recorded into an ignored repo-local
OACS store at `.agent/oacs/oacs.db` using scope
`proof-loop:structured-evidence-v02`. Three structured memories were committed:
spec intent, implementation summary, and verification summary. A context rebuild
used all three memories and returned a capsule-backed task summary. A plaintext
scan of the SQLite file did not find the structured evidence phrase, confirming
that the dogfood memory content was encrypted at rest.

## RU

Статус: reference implementation OACS v0.1 draft движется к v0.2.
Дата: 2026-05-01.

Gap с benchmark-specific parsing в core memory-tool loop закрыт.
`oacs/loop/memory_tools.py` больше не парсит текстовые markers MemoryArena или
AMA-Bench. Public adapters и synthetic tasks теперь пишут typed evidence в
`MemoryRecord.content.evidence`, а generic memory-tool loop потребляет только
эту структурированную форму.

### Deterministic Verification

Задач на suite: 5.

| Suite | Mode | Success | Evidence items | Total tokens |
| --- | --- | ---: | ---: | ---: |
| Synthetic memory-critical | `baseline_full_context` | 4/5 | 0 | 747 |
| Synthetic memory-critical | `oacs_memory_loop` | 5/5 | 0 | 214 |
| Synthetic memory-critical | `oacs_memory_tool_loop` | 5/5 | 5 | 1,097 |
| MemoryArena group travel | `baseline_full_context` | 5/5 | 0 | 11,577 |
| MemoryArena group travel | `oacs_memory_loop` | 5/5 | 0 | 5,893 |
| MemoryArena group travel | `oacs_memory_tool_loop` | 5/5 | 29 | 3,493 |
| MemoryArena progressive search | `baseline_full_context` | 5/5 | 0 | 50,873 |
| MemoryArena progressive search | `oacs_memory_loop` | 5/5 | 0 | 24,382 |
| MemoryArena progressive search | `oacs_memory_tool_loop` | 5/5 | 5 | 8,071 |
| AMA-Bench open-ended QA | `baseline_full_context` | 5/5 | 0 | 18,999 |
| AMA-Bench open-ended QA | `oacs_memory_loop` | 5/5 | 0 | 9,326 |
| AMA-Bench open-ended QA | `oacs_memory_tool_loop` | 5/5 | 5 | 2,282 |

### LM Studio Spot Check

Модель: `google/gemma-4-e2b`.
Suite: synthetic memory-critical, 5 задач.

| Mode | Success | Avg score | Evidence items | Total tokens | Wall time |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_full_context` | 4/5 | 4.8 | 0 | 1,634 | 41.9s |
| `oacs_memory_loop` | 5/5 | 5.0 | 0 | 2,854 | 80.3s |
| `oacs_memory_tool_loop` | 5/5 | 5.0 | 5 | 3,705 | 79.8s |

Это исправляет прежний провал synthetic suite в `oacs_memory_tool_loop`.
Tool loop теперь generic over structured evidence, а не benchmark marker
strings.

### Remaining Gap

Structured evidence path пока является contract reference implementation, а не
замороженной v1.0 standard schema. В v0.2 его нужно поднять до stable OACS tool
calls и определить conformance checks для adapters.

### Proof-loop Dogfood

Текущая development iteration также была записана в ignored repo-local OACS
store `.agent/oacs/oacs.db` со scope `proof-loop:structured-evidence-v02`.
Были committed три structured memories: spec intent, implementation summary и
verification summary. Context rebuild использовал все три memories и вернул
capsule-backed task summary. Plaintext scan SQLite-файла не нашёл фразу
structured evidence, что подтверждает encrypted-at-rest для dogfood memory.
