# Interoperability Checklist / Interoperability Checklist

## EN
This checklist is for runtimes and adapters that produce or consume OACS v1.0
records without depending on the Python reference implementation.

Portable contract requirements:

1. Emit JSON records that validate against the matching schema in `schemas/`.
2. Treat the examples in `conformance/fixtures/` as language-neutral fixtures,
   not Python object snapshots; treat `conformance/negative/` as required
   rejection examples for adapter-boundary checks.
3. Preserve `ContextCapsule.checksum` semantics: SHA-256 over canonical JSON
   with sorted keys, compact separators, UTF-8 encoding, and the `checksum`
   field excluded.
4. Enforce scope semantics before content access: requested operation scope must
   be a subset of both grant scope and resource scope; wildcard access requires
   explicit `*`.
5. Treat context operations as separate grants: `context.read`, `context.explain`,
   `context.export`, `context.import`, `context.reduce`, `context.expand`,
   `context.lock`, `context.mount`, and `context.unmount` must not imply each
   other unless a grant explicitly includes multiple operations.
6. Enforce namespace, depth, lifecycle, and status filters before retrieval
   ranking or evidence extraction.
7. Use backend-neutral storage selectors: filters, ordered field/direction
   pairs, and limits. Do not expose SQL fragments as standard selector data.
8. Treat D3-D5 memory as hypothesis/ranking context, not factual evidence. D3-D5
   active memory must cite `evidence_refs` or meet the embedded structured
   evidence threshold documented in `docs/MEMORY_MODEL.md`.
9. Keep tool outputs as `tool_result` `EvidenceRef` records unless a selected
   memory explicitly references that evidence.
10. Keep adapter execution boundaries explicit: tool, skill, MCP, model, storage,
   and benchmark behavior may vary by implementation, but the records they
   produce must preserve the OACS contract.
11. Record auditable operation envelopes for memory/context work without
   requiring plaintext sensitive content in operation metadata.
12. Document which behaviors are runtime-specific extensions rather than core
    OACS conformance behavior.
13. Represent secrets and non-public infrastructure values with `ProtectedRef`
    records. Keep plaintext, ciphertext, and vault state in external vaults or
    runtime adapters; project only the `ProtectedRef`, not plaintext or masked
    value fragments, into context, evidence, tool results, and audit metadata.

Reference-only behavior:

- The `acs` CLI and FastAPI server are Python reference interfaces.
- `acs conformance validate` is a reference checker for bundled fixtures, not a
  required OACS transport or runtime feature.
- SQLite is the bundled reference backend, not a required backend.
- `StorageBackend`, `ToolRunner`, LM Studio adapters, benchmark runners, repo
  dogfood, and agent workflow commands are reference implementation choices.
- HTTP, local CLI, stdio MCP execution, and model-provider integrations are
  adapter behaviors, not required standard runtime features.

## RU
Этот checklist предназначен для runtimes и adapters, которые produce или consume
OACS v1.0 records без зависимости от Python reference implementation.

Portable contract requirements:

1. Выпускать JSON records, которые валидируются matching schema из `schemas/`.
2. Считать examples в `conformance/fixtures/` language-neutral fixtures, а не
   snapshots Python objects; считать `conformance/negative/` обязательными
   rejection examples для adapter-boundary checks.
3. Сохранять semantics `ContextCapsule.checksum`: SHA-256 по canonical JSON с
   sorted keys, compact separators, UTF-8 encoding и исключённым полем
   `checksum`.
4. Применять scope semantics до доступа к content: requested operation scope
   должен быть subset of grant scope и resource scope; wildcard access требует
   явного `*`.
5. Считать context operations отдельными grants: `context.read`,
   `context.explain`, `context.export`, `context.import`, `context.reduce`,
   `context.expand`, `context.lock`, `context.mount` и `context.unmount` не
   должны imply друг друга, если grant явно не содержит несколько operations.
6. Применять namespace, depth, lifecycle и status filters до retrieval ranking
   или evidence extraction.
7. Использовать backend-neutral storage selectors: filters, ordered
   field/direction pairs и limits. Не раскрывать SQL fragments как standard
   selector data.
8. Считать D3-D5 memory hypothesis/ranking context, а не factual evidence.
   Active D3-D5 memory должна ссылаться на `evidence_refs` или пройти embedded
   structured evidence threshold из `docs/MEMORY_MODEL.md`.
9. Хранить outputs tools как `tool_result` `EvidenceRef`, пока выбранная memory
   явно не ссылается на это evidence.
10. Держать adapter execution boundaries явными: tool, skill, MCP, model,
   storage и benchmark behavior могут отличаться по implementation, но records
   должны сохранять OACS contract.
11. Записывать auditable operation envelopes для memory/context work без
   требования plaintext sensitive content в operation metadata.
12. Документировать, какие behaviors являются runtime-specific extensions, а не
    core OACS conformance behavior.
13. Представлять secrets и непубличные infrastructure values через records
    `ProtectedRef`. Хранить plaintext, ciphertext и vault state во внешних
    vaults или runtime adapters; проецировать только `ProtectedRef`, а не
    plaintext или masked фрагменты value, в context, evidence, tool results и
    audit metadata.

Reference-only behavior:

- `acs` CLI и FastAPI server являются Python reference interfaces.
- `acs conformance validate` является reference checker для bundled fixtures, а
  не обязательным OACS transport или runtime feature.
- SQLite является bundled reference backend, а не обязательным backend.
- `StorageBackend`, `ToolRunner`, LM Studio adapters, benchmark runners, repo
  dogfood и agent workflow commands являются choices reference implementation.
- HTTP, local CLI, stdio MCP execution и model-provider integrations являются
  adapter behaviors, а не обязательными standard runtime features.
