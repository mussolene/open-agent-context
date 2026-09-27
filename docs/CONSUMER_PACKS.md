# Supported Codex Integration And Consumer Packs / Интеграция Codex и consumer packs

## EN

OACS client adapters are not part of the OACS v1.0 standard surface. The
portable records, lifecycle, capabilities, evidence, context capsules, and
conformance fixtures remain the standard. An adapter teaches a client how to
use those primitives consistently.

Codex uses two user-scoped Skills and one lifecycle integration:

```bash
acs integrations codex install
acs integrations codex status
acs integrations codex doctor
acs integrations codex uninstall
```

The installer places `oacs` and `proof-loop` in `$HOME/.agents/skills`, merges
a small managed policy block into `$HOME/.codex/AGENTS.md`, and merges OACS
entries into `$HOME/.codex/hooks.json`. It preserves existing user content.
Uninstall removes only managed integration surfaces and never removes
persistent databases.

The Codex adapter keeps these boundaries:

- OACS is the governed memory, context, and evidence layer, not the tool
  scheduler.
- The generic proof loop owns acceptance criteria, smallest-safe-change
  discipline, current evidence, fresh verification, and bounded correction.
  It uses OACS for durable state and does not create `.agent/tasks/`.
- Intent is a task classification. Retrieval uses the actual task as `--query`
  and returns rendered model-facing content, not capsule identifiers alone.
- Project memory is retrieved from the current repository. Relevant global
  memory is retrieved from a separate user-data store. Project memory receives
  the larger budget and Project A storage is never queried from Project B.
- Checkpoints provide compact current task state. Historical memory is
  evidence and context, not authorization. A newer user instruction wins.
- `SessionStart` handles startup, resume, and compact continuation.
  `UserPromptSubmit` refreshes semantic context only for substantial prompts.
- Command output, CI, retrieval, publication, and verification can become
  `EvidenceRef` records through `acs tool ingest-result`.
- Standalone evidence enters a future context capsule only through reviewed
  memory that references it.
- Local keys, passphrases, databases, and private agent state must not be
  printed or committed.

Project storage is discovered at `.agent/oacs/oacs.db` or `.oacs/oacs.db`.
Global storage follows the operating system user-data convention and stays
outside the Skill directory.

Repository `AGENTS.md` files should keep only project-specific policy and a
small OACS opt-in statement. They should not copy the full Codex protocol.

The compatibility pack in `examples/consumer_packs/oacs_repo_development`
remains for Claude, Cursor, and migration support. It contains:

- `AGENTS.fragment.md`: minimal Codex project opt-in policy.
- `CLAUDE.fragment.md`: repository-local Claude workflow.
- `cursor/rules/oacs-repo-memory.mdc`: always-on Cursor workflow.
- `cursor/skills/oacs-repo-memory/SKILL.md`: Cursor execution workflow.
- `scripts/install.py`: repository-local surface installer.

## RU

Клиентские адаптеры OACS не входят в стандарт OACS v1.0. Стандартом остаются
переносимые записи, жизненный цикл, полномочия, доказательства, context capsules
и conformance fixtures. Адаптер учит конкретный клиент последовательно
использовать эти примитивы.

Codex использует два пользовательских Skills и одну lifecycle integration:

```bash
acs integrations codex install
acs integrations codex status
acs integrations codex doctor
acs integrations codex uninstall
```

Установщик помещает `oacs` и `proof-loop` в `$HOME/.agents/skills`, добавляет
небольшой управляемый блок в `$HOME/.codex/AGENTS.md` и добавляет OACS hooks в
`$HOME/.codex/hooks.json`. Существующее содержимое сохраняется. Uninstall
удаляет только управляемые поверхности интеграции и никогда не удаляет базы.

Адаптер Codex сохраняет следующие границы:

- OACS является управляемым слоем памяти, контекста и доказательств, а не
  планировщиком tools.
- Общий proof loop отвечает за критерии приемки, минимальное безопасное
  изменение, актуальные доказательства, свежую проверку и ограниченный цикл
  исправлений. Он использует OACS для долговечного состояния и не создает
  `.agent/tasks/`.
- Intent классифицирует задачу. Retrieval использует текущую задачу как
  `--query` и возвращает текст для модели, а не только identifiers capsule.
- Project memory выбирается из текущего репозитория. Релевантная global memory
  выбирается из отдельного пользовательского хранилища. Project memory получает
  больший бюджет, а хранилище Project A не запрашивается из Project B.
- Checkpoint содержит компактное состояние текущей задачи. Historical memory
  является контекстом и доказательством, а не разрешением. Более новая
  инструкция пользователя имеет приоритет.
- `SessionStart` обслуживает startup, resume и продолжение после compact.
  `UserPromptSubmit` обновляет semantic context только для существенных prompts.
- Результаты commands, CI, retrieval, публикации и verification можно сохранять
  как `EvidenceRef` через `acs tool ingest-result`.
- Отдельное evidence попадает в будущий context capsule только через
  проверенную memory, которая ссылается на него.
- Локальные ключи, passphrases, базы и private agent state нельзя печатать или
  коммитить.

В project `AGENTS.md` следует оставлять только специфические правила проекта и
короткое включение OACS. Полный протокол Codex там дублировать не следует.

Compatibility pack в `examples/consumer_packs/oacs_repo_development` сохранён
для Claude, Cursor и миграции. Он содержит:

- `AGENTS.fragment.md`: минимальный project policy Codex.
- `CLAUDE.fragment.md`: локальный workflow Claude.
- `cursor/rules/oacs-repo-memory.mdc`: постоянное правило Cursor.
- `cursor/skills/oacs-repo-memory/SKILL.md`: workflow выполнения Cursor.
- `scripts/install.py`: установщик локальных поверхностей репозитория.
