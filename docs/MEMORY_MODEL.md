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
