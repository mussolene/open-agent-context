# Skills / Skills

## EN
Skills follow `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`, `refs/`.
The reference built-ins are metadata-oriented: memory critical solving,
contradiction resolution, and task trace distillation. Benchmark prompt building
belongs to validation adapters, not the core skill registry.

`examples/skills/codex_oacs_runtime` is a versioned removable dogfood
skill for this repository. It combines the repo development memory adapter with
an optional Codex runtime workflow for OACS-backed context rebuilds, evidence,
checkpoints, and multi-agent coordination. It is not part of OACS conformance or
the portable standard surface and is run through normal `acs skill scan` /
`acs skill run` operations. The intended long-term shape is a separately
installable skill package.

## RU
Skills используют структуру `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`,
`refs/`. Reference built-ins ориентированы на metadata: memory critical solving,
contradiction resolution и task trace distillation. Benchmark prompt building
относится к validation adapters, а не к core skill registry.

`examples/skills/codex_oacs_runtime` - versioned отключаемый dogfood skill
для этого репозитория. Он объединяет repo development memory adapter и optional
Codex runtime workflow для OACS-backed context rebuilds, evidence, checkpoints и
multi-agent coordination. Он не является частью OACS conformance или portable
standard surface и запускается через обычные `acs skill scan` / `acs skill run`
operations. Долгосрочная форма - отдельный устанавливаемый skill package.
