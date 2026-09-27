# Skills / Skills

## EN
Skills follow `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`, `refs/`.
The reference built-ins are metadata-oriented: memory critical solving,
contradiction resolution, and task trace distillation. Benchmark prompt building
belongs to validation adapters, not the core skill registry.

The supported Codex integration installs the packaged Skill from
`oacs/integrations/codex/assets/oacs` into `$HOME/.agents/skills/oacs` with
`acs integrations codex install`. Its database remains outside the Skill.
This packaged integration is the source of truth, not an example Skill.

Client consumer packs for Codex, Claude, and Cursor are adapter bundles, not
skill registry records or standard requirements. See `docs/CONSUMER_PACKS.md`.

## RU
Skills используют структуру `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`,
`refs/`. Reference built-ins ориентированы на metadata: memory critical solving,
contradiction resolution и task trace distillation. Benchmark prompt building
относится к validation adapters, а не к core skill registry.

Поддерживаемая интеграция Codex устанавливает Skill из
`oacs/integrations/codex/assets/oacs` в `$HOME/.agents/skills/oacs` командой
`acs integrations codex install`. База данных находится вне Skill.
Эта пакетная интеграция является единственным источником истины, а не примером
Skill.

Client consumer packs для Codex, Claude и Cursor являются adapter bundles, а не
skill registry records или требованиями стандарта. См. `docs/CONSUMER_PACKS.md`.
