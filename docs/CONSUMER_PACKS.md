# Supported Agent Integrations / Поддерживаемые интеграции агентов

## EN

Client integrations are not part of the OACS v1.0 standard surface. The
portable records, lifecycle, capabilities, evidence, context capsules, and
conformance fixtures remain the standard. The packaged adapters teach clients
how to use those primitives consistently.

Install one or more integrations:

```bash
acs integrations codex install
acs integrations claude install
acs integrations cursor install
```

Every client also provides `status`, `doctor`, and `uninstall`. Use the common
rendered retrieval command from any client:

```bash
acs integrations context \
  --intent repo_development \
  --query "<actual task>" \
  --json
```

Intent is a task classification. Retrieval uses the actual task as `--query`
and returns rendered model-facing content, not capsule identifiers alone.
Project memory is selected from the current repository and receives the larger
budget. Relevant global memory comes from a separate user-data store. Project A
storage is never queried while working in Project B.

All clients install the same source Skills from
`oacs/integrations/shared_assets`:

- `oacs` owns retrieval, evidence, checkpoint, and recovery guidance;
- `proof-loop` owns acceptance criteria, smallest-safe-change discipline,
  current evidence, fresh verification, and bounded correction.

Persistent databases never live inside a Skill directory. Project storage is
discovered at `.agent/oacs/oacs.db` or `.oacs/oacs.db`. Global storage follows
the operating system user-data convention and can be overridden with
`OACS_GLOBAL_DB`.

### Codex

Codex installs Skills in `$HOME/.agents/skills`, merges a small policy block
into `$HOME/.codex/AGENTS.md`, and merges OACS hooks into
`$HOME/.codex/hooks.json`. Session start restores checkpoint state, including
compact continuation, and substantial user prompts trigger bounded semantic
retrieval.

### Claude Code

Claude Code installs Skills in `$HOME/.claude/skills`, merges the same minimal
policy into `$HOME/.claude/CLAUDE.md`, and merges hooks into
`$HOME/.claude/settings.json`. `SessionStart` restores startup and resumed
state, `UserPromptSubmit` refreshes substantial task context, and `PostCompact`
restores current checkpoint state after compaction.

### Cursor

Cursor installs Skills in `$HOME/.cursor/skills` so they use Cursor's native
personal Skill location and can participate in Cursor Skill sync when the user
enables it. A user hook in `$HOME/.cursor/hooks.json` restores checkpoint state
at local `sessionStart`.

Cursor's documented `beforeSubmitPrompt` output can allow or block submission
but cannot inject additional context. Its `preCompact` hook is observational
and cannot inject post-compaction context. Therefore task-specific retrieval
and post-compaction recovery remain Skill-driven in Cursor. User-level hooks
also do not run in Cursor Cloud Agents. The installer and doctor report these
limits rather than claiming parity that the client contract cannot provide.

Uninstall removes only managed Skills, policy blocks, and hook entries. It does
not remove project or global databases. Existing user instructions and hooks
are preserved. Repeated install is safe.

The old `examples/consumer_packs/oacs_repo_development` pack is deprecated. It
contains only repository-local opt-in shims for migrations. New repositories
should use the packaged global integration and keep only project-specific rules
in repository instruction files.

## RU

Клиентские интеграции не входят в переносимую поверхность стандарта OACS v1.0.
Стандартом остаются записи, жизненный цикл, полномочия, доказательства, context
capsules и conformance fixtures. Пакетные адаптеры учат клиентов единообразно
использовать эти примитивы.

Установка:

```bash
acs integrations codex install
acs integrations claude install
acs integrations cursor install
```

Для каждого клиента доступны `status`, `doctor` и `uninstall`. Общая команда
retrieval принимает фактическую задачу как `--query` и возвращает rendered
model-facing context:

```bash
acs integrations context \
  --intent repo_development \
  --query "<actual task>" \
  --json
```

Все клиенты получают одинаковые Skills `oacs` и `proof-loop` из
`oacs/integrations/shared_assets`. Persistent databases не находятся внутри
Skills. Project storage определяется в `.agent/oacs/oacs.db` или
`.oacs/oacs.db`, а global storage использует системный каталог пользовательских
данных.

Codex получает Skills в `$HOME/.agents/skills`, минимальный блок политики в
`$HOME/.codex/AGENTS.md` и lifecycle hooks. Claude Code получает Skills в
`$HOME/.claude/skills`, минимальный блок в `$HOME/.claude/CLAUDE.md`, а также
`SessionStart`, `UserPromptSubmit` и `PostCompact` в
`$HOME/.claude/settings.json`.

Cursor получает нативные personal Skills в `$HOME/.cursor/skills` и локальное
восстановление checkpoint на `sessionStart`. Документированный контракт Cursor
не позволяет `beforeSubmitPrompt` внедрять дополнительный контекст, а
`preCompact` не может восстановить контекст после compaction. Поэтому retrieval
по новой задаче и восстановление после compaction в Cursor остаются частью
Skill protocol. Пользовательские hooks Cursor также не работают в Cloud
Agents. Эти ограничения явно показываются в doctor.

Uninstall удаляет только управляемые Skills, блоки политики и записи hooks. Он
не удаляет project или global databases и сохраняет пользовательские настройки.
Повторная установка безопасна.

Старый pack `examples/consumer_packs/oacs_repo_development` объявлен
устаревшим и оставлен как repository-local migration shim. Новые репозитории
должны использовать пакетную глобальную интеграцию, а в локальных instruction
files хранить только project-specific правила.
