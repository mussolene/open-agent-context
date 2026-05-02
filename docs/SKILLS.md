# Skills / Skills

## EN
Skills follow `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`, `refs/`.
The reference built-ins are metadata-oriented: memory critical solving,
contradiction resolution, and task trace distillation. Benchmark prompt building
belongs to validation adapters, not the core skill registry.

`examples/skills/repo_development_memory` is a removable dogfood skill for this
repository. It is not part of OACS conformance. The `acs repo ...` commands are
thin convenience wrappers around that skill while the skill is kept in this
repository; the intended long-term shape is a separately installable skill
package.

## RU
Skills используют структуру `.skills/<name>/skill.json`, `SKILL.md`, `scripts/`,
`refs/`. Reference built-ins ориентированы на metadata: memory critical solving,
contradiction resolution и task trace distillation. Benchmark prompt building
относится к validation adapters, а не к core skill registry.

`examples/skills/repo_development_memory` - отключаемый dogfood skill для этого
репозитория. Он не является частью OACS conformance. Команды `acs repo ...` -
тонкие convenience wrappers вокруг этого skill, пока skill хранится в этом
репозитории; долгосрочная форма - отдельный устанавливаемый skill package.
