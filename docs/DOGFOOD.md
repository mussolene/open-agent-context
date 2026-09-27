# Development Dogfood / Использование OACS в этом репозитории

## EN

This repository validates the supported Codex integration against the OACS
Python reference implementation. The integration is not an example Skill and
does not expand the OACS v1.0 portable standard or conformance contract.

Install or refresh it with:

```bash
acs integrations codex install
acs integrations codex doctor --query "current OACS development task" --json
```

The installed integration provides:

- user-scoped `oacs` and `proof-loop` Skills under `$HOME/.agents/skills`;
- a small managed policy block in `$HOME/.codex/AGENTS.md`;
- `SessionStart` recovery for startup, resume, and compact continuation;
- selective `UserPromptSubmit` retrieval for substantial tasks;
- separate project and global memory retrieval with rendered model context.

Repository development still uses ordinary OACS primitives. State acceptance
criteria, run tools directly, ingest canonical results as evidence, and close a
verified iteration with a checkpoint:

```bash
acs integrations codex context \
  --intent repo_development \
  --query "<actual task>" \
  --json

acs tool ingest-result --db @project \
  --tool-id repo_check \
  --tool-name "Repository check" \
  --tool-type external \
  --status completed \
  --scope project \
  --input '{"commands":["pytest -q"]}' \
  --output '{"status":"PASS","summary":"current checks passed"}' \
  --json

acs checkpoint add --db @project \
  --task "<stable task id>" \
  --summary "Iteration verified." \
  --next "<next step or Complete>" \
  --evidence ev_... \
  --scope project \
  --json
```

Run current verification and a leak or secret scan before completion, then
record both results as evidence. Historical memory and recovered checkpoints
are context only. A current explicit user instruction always has priority.

The implementation source of truth is `oacs/integrations/shared_assets` and
the client adapters under `oacs/integrations`. Do not copy
the installed Skill into repository `examples/` or duplicate its operating
protocol in project `AGENTS.md` files.

## RU

Этот репозиторий проверяет поддерживаемую интеграцию Codex на эталонной
реализации OACS для Python. Интеграция не является примером Skill и не расширяет
переносимый стандарт OACS v1.0 или conformance contract.

Установка или обновление:

```bash
acs integrations codex install
acs integrations codex doctor --query "текущая задача разработки OACS" --json
```

Интеграция устанавливает:

- пользовательские Skills `oacs` и `proof-loop` в `$HOME/.agents/skills`;
- небольшой управляемый policy block в `$HOME/.codex/AGENTS.md`;
- восстановление `SessionStart` при startup, resume и compact continuation;
- выборочный retrieval `UserPromptSubmit` для существенных задач;
- раздельную project и global memory с rendered context для модели.

Разработка репозитория использует обычные примитивы OACS. Нужно определить
acceptance criteria, запускать инструменты напрямую, записывать канонические
результаты как evidence и закрывать проверенную итерацию checkpoint:

```bash
acs integrations codex context \
  --intent repo_development \
  --query "<фактическая задача>" \
  --json

acs tool ingest-result --db @project \
  --tool-id repo_check \
  --tool-name "Repository check" \
  --tool-type external \
  --status completed \
  --scope project \
  --input '{"commands":["pytest -q"]}' \
  --output '{"status":"PASS","summary":"текущие проверки прошли"}' \
  --json

acs checkpoint add --db @project \
  --task "<стабильный идентификатор задачи>" \
  --summary "Итерация проверена." \
  --next "<следующий шаг или Complete>" \
  --evidence ev_... \
  --scope project \
  --json
```

Перед завершением нужно выполнить актуальные проверки и поиск утечек или
секретов, затем записать оба результата как evidence. Historical memory и
восстановленный checkpoint являются только контекстом. Текущая явная инструкция
пользователя всегда имеет приоритет.

Единственный источник Skills находится в `oacs/integrations/shared_assets`, а
клиентские адаптеры находятся в `oacs/integrations`.
Установленный Skill не следует копировать в `examples/`, а его полный протокол
не следует дублировать в project `AGENTS.md`.
