# Gemma 4 E2B Full Context Control, 2026-05-02

## EN
This report compares three stateless LM Studio modes on the same task sets and
same model, `google/gemma-4-e2b`:

- `baseline_no_memory`: only the current task is sent.
- `baseline_full_context`: raw setup memory/context is sent in the prompt.
- `oacs_memory_call_loop`: OACS builds memory calls and compact evidence prompts.

LM Studio was used only through the OpenAI-compatible `/v1/chat/completions`
API. The LM Studio UI chat window and persistent conversation context were not
used.

Raw local artifacts: `/tmp/oacs-fixed-bench-20260501-233800`.

| Suite | Tasks | No memory | Full context | OACS memory calls |
|---|---:|---:|---:|---:|
| synthetic memory_critical | 7 | 0/7, avg 1.0, 2,123 tokens | 6/7, avg 4.8571, 2,992 tokens | 7/7, avg 5.0, 5,504 tokens |
| MemoryArena group_travel_planner | 5 | 0/5, avg 1.0, 2,960 tokens | 4/5, avg 4.2, 9,137 tokens | 5/5, avg 5.0, 5,216 tokens |
| MemoryArena progressive_search | 5 | 0/5, avg 1.0, 3,555 tokens | 5/5, avg 5.0, 31,707 tokens | 5/5, avg 5.0, 9,141 tokens |
| AMA-Bench open_end_qa | 3 | 0/3, avg 1.0, 1,697 tokens | 2/3, avg 3.6667, 8,062 tokens | 3/3, avg 5.0, 3,054 tokens |
| Aggregate | 20 | 0/20, avg 1.0, 10,335 tokens | 17/20, avg 4.55, 51,898 tokens | 20/20, avg 5.0, 22,915 tokens |

Score per 1k tokens:

- `baseline_no_memory`: 1.9352
- `baseline_full_context`: 1.7534
- `oacs_memory_call_loop`: 4.3640

Interpretation: full context is a strong control and can solve short or simple
memory tasks, but it becomes expensive and still misses some public tasks. OACS
adds overhead compared with no memory, but it is materially more token-efficient
than raw full-context prompting on these memory-critical suites.

## RU
Этот отчёт сравнивает три stateless LM Studio режима на одних и тех же задачах
и одной модели, `google/gemma-4-e2b`:

- `baseline_no_memory`: в prompt отправляется только текущая задача.
- `baseline_full_context`: в prompt отправляется сырой setup memory/context.
- `oacs_memory_call_loop`: OACS строит memory calls и compact evidence prompt.

LM Studio использовался только через OpenAI-compatible `/v1/chat/completions`
API. UI chat window и persistent conversation context LM Studio не
использовались.

Raw local artifacts: `/tmp/oacs-fixed-bench-20260501-233800`.

| Suite | Tasks | No memory | Full context | OACS memory calls |
|---|---:|---:|---:|---:|
| synthetic memory_critical | 7 | 0/7, avg 1.0, 2,123 tokens | 6/7, avg 4.8571, 2,992 tokens | 7/7, avg 5.0, 5,504 tokens |
| MemoryArena group_travel_planner | 5 | 0/5, avg 1.0, 2,960 tokens | 4/5, avg 4.2, 9,137 tokens | 5/5, avg 5.0, 5,216 tokens |
| MemoryArena progressive_search | 5 | 0/5, avg 1.0, 3,555 tokens | 5/5, avg 5.0, 31,707 tokens | 5/5, avg 5.0, 9,141 tokens |
| AMA-Bench open_end_qa | 3 | 0/3, avg 1.0, 1,697 tokens | 2/3, avg 3.6667, 8,062 tokens | 3/3, avg 5.0, 3,054 tokens |
| Aggregate | 20 | 0/20, avg 1.0, 10,335 tokens | 17/20, avg 4.55, 51,898 tokens | 20/20, avg 5.0, 22,915 tokens |

Score per 1k tokens:

- `baseline_no_memory`: 1.9352
- `baseline_full_context`: 1.7534
- `oacs_memory_call_loop`: 4.3640

Вывод: full context является сильным контролем и может решать короткие или
простые memory tasks, но быстро становится дорогим и всё равно ошибается на
части public tasks. OACS дороже, чем no-memory baseline, но на этих
memory-critical suites существенно эффективнее сырого full-context prompting по
качеству на token.
