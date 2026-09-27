# Skills / Skills

## EN
Skills follow `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`, `refs/`.
The reference built-ins are metadata-oriented: memory critical solving,
contradiction resolution, and task trace distillation. Benchmark prompt building
belongs to validation adapters, not the core skill registry.

The supported Codex integration installs the packaged `oacs` and `proof-loop`
Skills from `oacs/integrations/codex/assets` into `$HOME/.agents/skills` with
`acs integrations codex install`. The OACS database remains outside both
Skills. The proof loop uses OACS as its durable evidence and checkpoint layer
instead of creating a parallel task-artifact store. This packaged integration
is the source of truth, not an example Skill.

Client consumer packs for Codex, Claude, and Cursor are adapter bundles, not
skill registry records or standard requirements. See `docs/CONSUMER_PACKS.md`.

## RU
Skills используют структуру `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`,
`refs/`. Reference built-ins ориентированы на metadata: memory critical solving,
contradiction resolution и task trace distillation. Benchmark prompt building
относится к validation adapters, а не к core skill registry.

Поддерживаемая интеграция Codex устанавливает Skills `oacs` и `proof-loop` из
`oacs/integrations/codex/assets` в `$HOME/.agents/skills` командой
`acs integrations codex install`. База OACS находится вне обоих Skills.
Proof loop использует OACS как долговечный слой доказательств и контрольных
точек вместо параллельного хранилища артефактов задач. Эта пакетная интеграция
является единственным источником истины, а не примером Skill.

Client consumer packs для Codex, Claude и Cursor являются adapter bundles, а не
skill registry records или требованиями стандарта. См. `docs/CONSUMER_PACKS.md`.
