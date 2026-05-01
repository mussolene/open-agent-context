# Security / Безопасность

## EN
Threats addressed in the POC: plaintext memory exposure, accidental capability
leaks, hidden memory writes, fuzzy memory used as fact, and unaudited access.

Memory and capsule payloads use envelope-style AEAD encryption at rest. The
local passphrase provider wraps a master key; an unlocked session key can be
stored locally for development and removed with `acs key lock`.

Audit events store operation metadata and hashes, not secret content.

Required v0.2.6 audit events: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) and context build/export/import/explain/
reduce/expand/lock. Audit metadata may include counts, ids, query hashes, and
content hashes; it must not include keys, passphrases, or plaintext sensitive
memory.

Subagent memory sharing uses normal `CapabilityGrant` records. Non-bootstrap
actors must have matching operation, scope, namespace, and depth grants before
they can query, read, or build capsules from shared memory.

## RU
POC закрывает риски: хранение памяти в открытом виде, случайные утечки
capability, скрытые записи памяти, использование fuzzy memory как факта и
доступ без аудита.

Payload памяти и capsules шифруются AEAD. Локальный passphrase provider
оборачивает master key; unlock-сессия может храниться локально для разработки
и удаляется через `acs key lock`.

Audit events содержат metadata и хэши, но не секретный контент.

Обязательные audit events v0.2.6: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) и context build/export/import/explain/
reduce/expand/lock. Audit metadata может содержать counts, ids, query hashes и
content hashes; она не должна содержать keys, passphrases или plaintext
sensitive memory.

Shared memory для subagents использует обычные `CapabilityGrant` records.
Non-bootstrap actors должны иметь matching operation, scope, namespace и depth
grants перед query, read или build capsules из shared memory.
