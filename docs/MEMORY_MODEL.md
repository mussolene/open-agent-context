# Memory Model / Модель памяти

## EN
Depths:

- D0 raw trace.
- D1 episode.
- D2 fact, preference, or procedure.
- D3 pattern.
- D4 user/project/org model.
- D5 community/domain prior.

D0-D2 may support factual answers. D3-D5 may only rank hypotheses, triage,
prioritize context, personalize, or ask clarifying questions. High-risk actions
must sharpen fuzzy memory into evidence-backed memory.

D3-D5 commits require support. A reference implementation may accept either
external `evidence_refs` or embedded structured `MemoryContent.evidence`.
Embedded support must meet the depth threshold before commit: D3 >= 0.5
confidence, D4 >= 0.7 confidence, and D5 >= 0.8 confidence with an explicit
`source_ref`.

Lifecycle: observed -> candidate -> clarifying -> confirmed -> active ->
deprecated -> superseded -> forgotten.

### Structured Evidence

`MemoryContent.evidence` is the reference implementation path for typed
evidence attached to encrypted memory. It keeps adapter-specific parsing at the
boundary and lets the generic memory-call loop consume a stable shape:

- `evidence_kind`
- `claim`
- `value`
- `source_ref`
- `confidence`
- `scope`
- optional dimensions such as `participant`, `day`, `slot`, `order`, and
  `trajectory_step`

Core memory_calls must not depend on benchmark-specific text markers. Importers
or adapters may parse external formats, but they must write structured evidence
before generic retrieval and context building use it. Domain-specific evidence
selection belongs in selector/adapters, not in the memory-call orchestrator.

### Retrieval Contract

v0.2.8 defines retrieval as a provider contract over already-authorized
`MemoryRecord` objects. The reference baseline is deterministic:

- policy-first filtering happens before provider ranking or evidence extraction;
- `LexicalRetrievalProvider` ranks by token overlap, depth, and stable memory id;
- `StructuredEvidenceRetrievalProvider` ranks typed `MemoryContent.evidence`
  without benchmark-specific text parsing;
- `EmbeddingRetrievalProvider` is disabled by default and never required for
  conformance.

Portable retrieval conformance is expressed through
`schemas/retrieval_query.schema.json`, `schemas/retrieval_result.schema.json`,
and fixtures in `conformance/fixtures/`. Storage access uses
`schemas/storage_selector.schema.json`: selector records carry filters,
ordered field/direction pairs, and limits rather than backend-specific SQL.

### Encrypted Record Health

Memory query and context build degrade gracefully by default in the reference
implementation. If an authorized memory row cannot be decrypted or decoded,
OACS skips that row, returns usable results, and emits a structured
`UnreadableMemoryRecord` warning with safe metadata only: `record_id`, `scope`,
`namespace`, `memory_type`, and `created_at`. Encrypted content is never
included in the warning. Context build diagnostics are returned beside the
capsule by the reference CLI/API; they are not fields in the portable
`ContextCapsule` standard record. Use `--strict` on `acs memory query` or
`acs context build` to preserve fail-fast behavior for verification runs.

Health and recovery commands:

- `acs status` reports `memory_decrypt_health` when the key is unlocked.
- `acs doctor` and `acs memory doctor` fail when active memory rows are
  unreadable.
- `acs memory quarantine <id>` marks a bad row as `quarantined` so normal reads
  skip it without deleting data.
- `acs memory export-readable` exports only decryptable memories plus warnings.
- `acs memory purge-unreadable --dry-run` lists unreadable rows; use `--apply`
  only after reviewing the ids.

Read/write boundaries while memory health is degraded:

- Requires memory decrypt: `memory read`, `memory query`, `memory export`,
  `context build`, loop runs that build context, and memory update commands that
  first read an existing memory (`commit`, `correct`, `deprecate`, `supersede`,
  `forget`, `blur`, `sharpen`).
- Does not need decrypting old memories: `memory observe`, `memory propose`,
  `memory import`, `tool ingest-result`, evidence list/inspect, audit list/tail,
  rule/skill/tool registration, and checkpoint append commands. These commands
  may warn about degraded memory health but should not be blocked by unreadable
  old rows.

## RU
Глубины:

- D0 сырой trace.
- D1 эпизод.
- D2 факт, предпочтение или процедура.
- D3 паттерн.
- D4 модель пользователя, проекта или организации.
- D5 доменный/community prior.

D0-D2 могут поддерживать фактические ответы. D3-D5 используются только для
ранжирования гипотез, triage, приоритизации контекста, персонализации или
уточняющих вопросов. Рискованные действия требуют sharpening.

D3-D5 commits требуют support. Reference implementation может принять external
`evidence_refs` или embedded structured `MemoryContent.evidence`. Embedded
support должен пройти threshold до commit: D3 >= 0.5 confidence, D4 >= 0.7
confidence, D5 >= 0.8 confidence с явным `source_ref`.

Жизненный цикл: observed -> candidate -> clarifying -> confirmed -> active ->
deprecated -> superseded -> forgotten.

### Structured Evidence

`MemoryContent.evidence` — путь reference implementation для typed evidence,
привязанного к encrypted memory. Он оставляет adapter-specific parsing на
границе и даёт generic memory-call loop стабильную форму:

- `evidence_kind`
- `claim`
- `value`
- `source_ref`
- `confidence`
- `scope`
- optional dimensions: `participant`, `day`, `slot`, `order`,
  `trajectory_step`

Core memory_calls не должны зависеть от benchmark-specific text markers.
Importers или adapters могут парсить внешние форматы, но перед generic retrieval
и context building они должны записывать structured evidence. Domain-specific
evidence selection должен жить в selector/adapters, а не в memory-call
orchestrator.

### Retrieval Contract

v0.2.8 определяет retrieval как provider contract поверх уже authorized
`MemoryRecord` objects. Reference baseline детерминированный:

- policy-first filtering выполняется до provider ranking или evidence extraction;
- `LexicalRetrievalProvider` ранжирует по token overlap, depth и stable memory id;
- `StructuredEvidenceRetrievalProvider` ранжирует typed `MemoryContent.evidence`
  без benchmark-specific text parsing;
- `EmbeddingRetrievalProvider` disabled by default и не требуется для
  conformance.

Portable retrieval conformance выражен через
`schemas/retrieval_query.schema.json`, `schemas/retrieval_result.schema.json` и
fixtures в `conformance/fixtures/`. Storage access использует
`schemas/storage_selector.schema.json`: selector records содержат filters,
ordered field/direction pairs и limits вместо backend-specific SQL.

### Encrypted Record Health

По умолчанию `memory query` и `context build` в reference implementation
деградируют мягко. Если authorized memory row не расшифровывается или не
декодируется, OACS пропускает эту строку, возвращает пригодный результат и
добавляет structured warning `UnreadableMemoryRecord` только с безопасными
metadata: `record_id`, `scope`, `namespace`, `memory_type`, `created_at`.
Encrypted content в warning не попадает. Diagnostics context build возвращаются
рядом с capsule в reference CLI/API; они не являются полями portable
`ContextCapsule` standard record. Для fail-fast проверок используйте `--strict`
в `acs memory query` или `acs context build`.

Health и recovery commands:

- `acs status` показывает `memory_decrypt_health`, когда key unlocked.
- `acs doctor` и `acs memory doctor` завершаются ошибкой, если active memory
  rows unreadable.
- `acs memory quarantine <id>` помечает плохую row как `quarantined`, чтобы
  обычные reads её пропускали без удаления данных.
- `acs memory export-readable` экспортирует только decryptable memories и
  warnings.
- `acs memory purge-unreadable --dry-run` показывает unreadable rows; `--apply`
  используйте только после проверки ids.

Read/write boundaries при degraded memory health:

- Требуют memory decrypt: `memory read`, `memory query`, `memory export`,
  `context build`, loop runs, которые строят context, и memory update commands,
  сначала читающие существующую memory (`commit`, `correct`, `deprecate`,
  `supersede`, `forget`, `blur`, `sharpen`).
- Не требуют decrypt old memories: `memory observe`, `memory propose`,
  `memory import`, `tool ingest-result`, evidence list/inspect, audit list/tail,
  rule/skill/tool registration и checkpoint append commands. Они могут
  предупреждать о degraded memory health, но не должны блокироваться
  unreadable old rows.
