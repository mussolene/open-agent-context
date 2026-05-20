# OACS Consumer Packs / Пакеты потребителей OACS

## EN
OACS consumer packs are local adapter bundles for agent clients. They are not
part of the OACS v1.0 standard surface. The standard remains the portable JSON
records, lifecycle, capabilities, evidence, context capsules, and conformance
fixtures. A consumer pack only teaches a client such as Codex, Claude, Cursor,
or another IDE agent how to use those records consistently in a repository.

The strong pattern is:

```text
root repo instructions -> OACS context/evidence/checkpoint loop -> current
tooling gates -> OACS evidence refs -> final answer
```

For Codex and Claude, the root instruction surfaces are `AGENTS.md` and
`CLAUDE.md`. For Cursor, the durable surfaces are `.cursor/rules/*.mdc` and
`.cursor/skills/*/SKILL.md`. The same OACS policy should be projected into all
of them so each agent follows the same memory and proof discipline.

Consumer packs must keep these boundaries:

- OACS is the governed memory/context/evidence layer, not the tool scheduler.
- OACS context should be selected, not prepended unconditionally. The default
  for substantial repository work is still to use the OACS proof loop: context
  where useful, evidence ingestion, verification, leak/secret review, and a
  checkpoint. Skip context only for tiny visible-file edits where current files
  and user instructions are sufficient.
- `acs context gate --intent ... --scope ... --task ... --json` is the
  reference consumer-pack convenience for making that explicit build/skip
  decision before `acs context build`. It is reference behavior, not a portable
  standard requirement. Treat ambiguous results, missing gate output, missing
  local OACS setup, and domain-heavy repositories as `build` or explicit OACS
  unavailable, not as permission to drift into stateless work.
- Command output, CI, retrieval, package publication, and manual verification
  become `EvidenceRef` records through `acs tool ingest-result`.
- Standalone tool evidence does not enter a `ContextCapsule` by itself; it must
  be attached to reviewed memory when it should guide future context.
- D2+ durable facts/procedures and D3-D5 patterns require explicit review.
- Local `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`, `.agent/oacs`,
  `.oacs`, key material, passphrases, databases, and private agent state must
  not be read, printed, or committed.
- Client-specific rules may be strict, but they must not redefine the OACS
  standard.

Machine-facing gate contract:

- Command: `acs context gate --intent <intent> --scope <scope> --task <text> --json`.
- Required consumer decision keys: `decision`, `should_build_context`, `reason`,
  and `standard_boundary`.
- Valid `decision` values are `build` and `skip`.
- `decision=build` means run the returned `next_command` or an equivalent
  `acs context build`; `decision=skip` is valid only for tiny visible-file edits
  and does not relax evidence/checkpoint requirements for substantial work.
- `standard_boundary` must remain
  `reference_consumer_pack_convenience_not_oacs_standard`.

The reference pack in `examples/consumer_packs/oacs_repo_development` contains:

- `AGENTS.fragment.md` for Codex-style root instructions.
- `CLAUDE.fragment.md` for Claude root instructions.
- `cursor/rules/oacs-repo-memory.mdc` for Cursor always-on workflow rules.
- `cursor/skills/oacs-repo-memory/SKILL.md` for Cursor task execution.
- `scripts/install.py` to copy the selected surfaces into a local repository.

## RU
OACS consumer packs — это локальные adapter bundles для агентных клиентов. Они
не являются частью OACS v1.0 standard surface. Стандартом остаются переносимые
JSON records, lifecycle, capabilities, evidence, context capsules и conformance
fixtures. Consumer pack только учит конкретный client — Codex, Claude, Cursor
или другой IDE agent — последовательно использовать эти records в репозитории.

Сильный паттерн:

```text
root repo instructions -> OACS context/evidence/checkpoint loop -> текущие
tooling gates -> OACS evidence refs -> final answer
```

Для Codex и Claude root instruction surfaces — `AGENTS.md` и `CLAUDE.md`. Для
Cursor устойчивые surfaces — `.cursor/rules/*.mdc` и
`.cursor/skills/*/SKILL.md`. Одна и та же OACS policy должна проецироваться во
все эти файлы, чтобы разные агенты соблюдали одну дисциплину памяти и proof.

Consumer packs должны сохранять границы:

- OACS — governed memory/context/evidence layer, а не scheduler tools.
- OACS context нужно выбирать, а не добавлять в prompt безусловно. Default для
  substantial repository work всё равно — OACS proof loop: context где полезен,
  evidence ingestion, verification, leak/secret review и checkpoint. Пропускайте
  context только для tiny visible-file edits, где достаточно текущих файлов и
  инструкции пользователя.
- `acs context gate --intent ... --scope ... --task ... --json` — reference
  convenience для consumer packs, чтобы явно принять build/skip решение перед
  `acs context build`. Это reference behavior, а не переносимое требование
  стандарта. Ambiguous results, missing gate output, missing local OACS setup и
  domain-heavy repositories трактуются как `build` или явный OACS unavailable,
  а не как разрешение уйти в stateless work.
- Command output, CI, retrieval, package publication и manual verification
  становятся `EvidenceRef` через `acs tool ingest-result`.
- Standalone tool evidence само не попадает в `ContextCapsule`; его нужно
  привязать к reviewed memory, если оно должно влиять на будущий context.
- D2+ durable facts/procedures и D3-D5 patterns требуют explicit review.
- Локальные `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`,
  `.agent/oacs`, `.oacs`, key material, passphrases, databases и private agent
  state нельзя читать, печатать или коммитить.
- Client-specific rules могут быть жёсткими, но не должны переопределять OACS
  standard.

Machine-facing contract для gate:

- Команда: `acs context gate --intent <intent> --scope <scope> --task <text> --json`.
- Обязательные для consumer decision keys: `decision`,
  `should_build_context`, `reason` и `standard_boundary`.
- Допустимые значения `decision`: `build` и `skip`.
- `decision=build` означает запустить возвращённый `next_command` или
  эквивалентный `acs context build`; `decision=skip` допустим только для tiny
  visible-file edits и не ослабляет evidence/checkpoint requirements для
  substantial work.
- `standard_boundary` должен оставаться
  `reference_consumer_pack_convenience_not_oacs_standard`.

Reference pack в `examples/consumer_packs/oacs_repo_development` содержит:

- `AGENTS.fragment.md` для Codex-style root instructions.
- `CLAUDE.fragment.md` для Claude root instructions.
- `cursor/rules/oacs-repo-memory.mdc` для Cursor always-on workflow rules.
- `cursor/skills/oacs-repo-memory/SKILL.md` для Cursor task execution.
- `scripts/install.py` для копирования выбранных surfaces в локальный repo.
