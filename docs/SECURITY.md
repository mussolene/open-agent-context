# Security / Безопасность

## EN
Threats addressed by OACS: plaintext memory exposure, accidental capability
leaks, hidden memory writes, fuzzy memory used as fact, and unaudited access.

Memory and capsule payloads use envelope-style AEAD encryption at rest. The
local passphrase provider wraps a master key; an unlocked session key can be
stored locally for development and removed with `acs key lock`.

Audit events store operation metadata and hashes, not secret content.

Capsule integrity is checksum- and MAC-based. Raw capsules carry a
deterministic checksum for tamper detection. Export envelopes add
`integrity.payload_checksum` and `integrity.mac`. `integrity.signature` remains
a deprecated compatibility alias for the same HMAC-SHA256 tag. The MAC uses the
local master key; it is not asymmetric cryptographic signing and should not be
documented as non-repudiation, certificate-backed identity, or
third-party-verifiable provenance.

Policy mode is explicit in the reference implementation. Dev mode preserves the
local bootstrap path for `None`, empty actor, and `system`, and records
`policy.bootstrap_bypass` audit events. `OACS_POLICY_MODE=strict` denies those
bootstrap actors unless they hold ordinary `CapabilityGrant` records.

Context permissions are separated by operation. Runtime read/explain,
export/import, reduce/expand, and mount/lock state changes require their own
`context.*` grants; `context.read` must not imply `context.export`.

Required audit events: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) and context build/read/export/import/
explain/reduce/expand/lock/mount/unmount. Audit metadata may include counts, ids, query hashes, and
content hashes; it must not include keys, passphrases, or plaintext sensitive
memory.

Subagent memory sharing uses normal `CapabilityGrant` records. Non-bootstrap
actors must have matching operation, scope, namespace, and depth grants before
they can query, read, or build capsules from shared memory.

Tool and skill adapters are also deny-by-default. `tool.call` and `skill.run`
must be granted together with explicit `tools_allowed` or `skills_allowed`
entries, plus namespace and scope constraints. Audit chain verification detects
local tampering with recorded operations.

Secrets and non-public infrastructure values use the external protected value
boundary documented in `docs/VAULT.md`. OACS records only `ProtectedRef` and
leak-prevention metadata. Passwords, tokens, private keys, internal IPs,
private hostnames, and private URLs should live in external vaults such as
1Password, HashiCorp Vault, cloud secret managers, SOPS, or an OS keychain.
Prefer `protected.use` for adapter execution; grant `protected.read` or
`secret.read` only when plaintext disclosure is explicitly required.

## RU
OACS закрывает риски: хранение памяти в открытом виде, случайные утечки
capability, скрытые записи памяти, использование fuzzy memory как факта и
доступ без аудита.

Payload памяти и capsules шифруются AEAD. Локальный passphrase provider
оборачивает master key; unlock-сессия может храниться локально для разработки
и удаляется через `acs key lock`.

Audit events содержат metadata и хэши, но не секретный контент.

Integrity capsules основана на checksum и MAC. Raw capsules содержат
deterministic checksum для tamper detection. Export envelopes добавляют
`integrity.payload_checksum` и `integrity.mac`. `integrity.signature` остаётся
deprecated compatibility alias для того же HMAC-SHA256 tag. MAC использует local
master key; это не asymmetric cryptographic signing. Это нельзя описывать как
non-repudiation, certificate-backed identity или third-party-verifiable
provenance.

Policy mode в reference implementation явный. Dev mode сохраняет local
bootstrap path для `None`, empty actor и `system` и записывает audit events
`policy.bootstrap_bypass`. `OACS_POLICY_MODE=strict` запрещает этих bootstrap
actors, если у них нет обычных `CapabilityGrant` records.

Context permissions разделены по операциям. Runtime read/explain,
export/import, reduce/expand и mount/lock state changes требуют собственных
`context.*` grants; `context.read` не должен означать `context.export`.

Обязательные audit events: memory query/read/write operations
(`observe`, `propose`, `commit`, `correct`, `deprecate`, `supersede`, `forget`,
`blur`, `sharpen`, `export`, `import`) и context build/read/export/import/
explain/reduce/expand/lock/mount/unmount. Audit metadata может содержать counts, ids, query hashes и
content hashes; она не должна содержать keys, passphrases или plaintext
sensitive memory.

Shared memory для subagents использует обычные `CapabilityGrant` records.
Non-bootstrap actors должны иметь matching operation, scope, namespace и depth
grants перед query, read или build capsules из shared memory.

Tool и skill adapters тоже deny-by-default. `tool.call` и `skill.run` должны
быть выданы вместе с explicit `tools_allowed` или `skills_allowed`, а также с
namespace и scope constraints. Audit chain verification помогает обнаружить
локальное изменение записанных операций.

Secrets и непубличные infrastructure values используют external protected value
boundary из `docs/VAULT.md`. OACS записывает только `ProtectedRef` и metadata
для предотвращения утечек. Пароли, tokens, private keys, internal IPs, private
hostnames и private URLs должны жить во внешних vaults: 1Password, HashiCorp
Vault, cloud secret managers, SOPS или OS keychain. Предпочитайте
`protected.use` для adapter execution; `protected.read` или `secret.read`
выдавайте только при явной необходимости раскрыть plaintext.
