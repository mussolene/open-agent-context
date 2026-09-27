# Skills / Skills

## EN
Skills follow `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`, `refs/`.
The reference built-ins are metadata-oriented: memory critical solving,
contradiction resolution, and task trace distillation. Benchmark prompt building
belongs to validation adapters, not the core skill registry.

The supported Codex, Claude Code, and Cursor integrations install the same
packaged `oacs` and `proof-loop` Skills from
`oacs/integrations/shared_assets`. Client commands place them in each native
user-scoped Skill directory. The OACS database remains outside every Skill.
The proof loop uses OACS as its durable evidence and checkpoint layer instead
of creating a parallel task-artifact store. These shared packaged assets are
the source of truth, not example Skills.

The old repository-local consumer pack remains only as a migration shim. See
`docs/CONSUMER_PACKS.md`.

## RU
Skills используют структуру `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`,
`refs/`. Reference built-ins ориентированы на metadata: memory critical solving,
contradiction resolution и task trace distillation. Benchmark prompt building
относится к validation adapters, а не к core skill registry.

Поддерживаемые интеграции Codex, Claude Code и Cursor устанавливают одинаковые
Skills `oacs` и `proof-loop` из `oacs/integrations/shared_assets` в нативный
пользовательский каталог Skills каждого клиента. База OACS находится вне
Skills. Proof loop использует OACS как долговечный слой доказательств и
контрольных точек вместо параллельного хранилища артефактов задач. Общие
пакетные assets являются единственным источником истины, а не примерами Skills.

Старый локальный consumer pack оставлен только как migration shim. См.
`docs/CONSUMER_PACKS.md`.
