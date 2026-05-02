# Repo Development Memory Skill

## EN
This is a non-standard OACS dogfood skill. It proves that repository
development memory can live as a removable skill layer instead of becoming part
of the OACS core standard.

Actions:

- `context`: build a repo-scoped Context Capsule.
- `capture`: commit a manual D1 repository episode.
- `auto_start`: build context and audit metadata without writing memory.
- `auto_finish`: commit a D1 repository episode for the completed iteration.
- `autorun`: build context, run a bounded local command, and commit a D1
  repository episode with command outcome metadata.

Policy:

- Auto mode commits only D1 `episode` memory.
- D2 facts, D2 procedures, rules, and D3-D5 patterns require explicit
  `memory propose` / `memory commit` review outside this skill.
- The skill is repo-local dogfood, not OACS conformance surface.

## RU
Это non-standard OACS dogfood skill. Он показывает, что память разработки
репозитория может жить как отключаемый skill layer, а не как часть core
standard OACS.

Actions:

- `context`: строит repo-scoped Context Capsule.
- `capture`: коммитит manual D1 repository episode.
- `auto_start`: строит context и audit metadata без записи memory.
- `auto_finish`: коммитит D1 repository episode по завершённой итерации.
- `autorun`: строит context, запускает bounded local command и коммитит D1
  repository episode с metadata результата команды.

Policy:

- Auto mode коммитит только D1 `episode` memory.
- D2 facts, D2 procedures, rules и D3-D5 patterns требуют явного review через
  `memory propose` / `memory commit` вне этого skill.
- Skill является repo-local dogfood, а не OACS conformance surface.
