# Security / Безопасность

## EN
Threats addressed in the POC: plaintext memory exposure, accidental capability
leaks, hidden memory writes, fuzzy memory used as fact, and unaudited access.

Memory and capsule payloads use envelope-style AEAD encryption at rest. The
local passphrase provider wraps a master key; an unlocked session key can be
stored locally for development and removed with `acs key lock`.

Audit events store operation metadata and hashes, not secret content.

Capsule integrity is checksum- and MAC-based. Raw capsules carry a
deterministic checksum for tamper detection. Export envelopes add
`integrity.payload_checksum` and `integrity.signature`; despite the field name,
`signature` is an HMAC-SHA256 tag using the local master key, not asymmetric
cryptographic signing. It should not be documented as non-repudiation,
certificate-backed identity, or third-party-verifiable provenance.

Required audit events: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) and context build/export/import/explain/
reduce/expand/lock. Audit metadata may include counts, ids, query hashes, and
content hashes; it must not include keys, passphrases, or plaintext sensitive
memory.

Subagent memory sharing uses normal `CapabilityGrant` records. Non-bootstrap
actors must have matching operation, scope, namespace, and depth grants before
they can query, read, or build capsules from shared memory.

Tool and skill adapters are also deny-by-default. `tool.call` and `skill.run`
must be granted together with explicit `tools_allowed` or `skills_allowed`
entries, plus namespace and scope constraints. Audit chain verification detects
local tampering with recorded operations.

## RU
POC закрывает риски: хранение памяти в открытом виде, случайные утечки
capability, скрытые записи памяти, использование fuzzy memory как факта и
доступ без аудита.

Payload памяти и capsules шифруются AEAD. Локальный passphrase provider
оборачивает master key; unlock-сессия может храниться локально для разработки
и удаляется через `acs key lock`.

Audit events содержат metadata и хэши, но не секретный контент.

Integrity capsules основана на checksum и MAC. Raw capsules содержат
deterministic checksum для tamper detection. Export envelopes добавляют
`integrity.payload_checksum` и `integrity.signature`; несмотря на имя поля,
`signature` является HMAC-SHA256 tag на local master key, а не asymmetric
cryptographic signing. Это нельзя описывать как non-repudiation,
certificate-backed identity или third-party-verifiable provenance.

Обязательные audit events: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) и context build/export/import/explain/
reduce/expand/lock. Audit metadata может содержать counts, ids, query hashes и
content hashes; она не должна содержать keys, passphrases или plaintext
sensitive memory.

Shared memory для subagents использует обычные `CapabilityGrant` records.
Non-bootstrap actors должны иметь matching operation, scope, namespace и depth
grants перед query, read или build capsules из shared memory.

Tool и skill adapters тоже deny-by-default. `tool.call` и `skill.run` должны
быть выданы вместе с explicit `tools_allowed` или `skills_allowed`, а также с
namespace и scope constraints. Audit chain verification помогает обнаружить
локальное изменение записанных операций.
