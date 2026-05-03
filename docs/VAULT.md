# Protected Values and Vault Boundary / Граница Protected Values и Vault

## EN
OACS treats secrets and non-public infrastructure facts as protected values,
not ordinary memory. The standard boundary is the JSON shape and capability
semantics for `SecretRecord`, `SensitiveFact`, and `ProtectedRef`; the bundled
Python vault is only one reference implementation of that boundary.

Protected value classes:

- `SecretRecord`: API keys, tokens, passwords, private keys, certificates, and
  environment secrets.
- `SensitiveFact`: internal IPs, private hostnames, private URLs, topology, and
  non-public repo or deployment paths.
- `ProtectedRef`: a redacted reference that may appear in memory, context,
  tool bindings, audit metadata, or adapter payloads without exposing the value.

Access is split deliberately:

- `protected.use`: allow a tool or adapter to use a protected value without
  revealing plaintext to the agent.
- `protected.read` / `secret.read`: explicitly reveal plaintext and should be
  rare.
- `protected.list`: list redacted refs.
- `protected.create` / `secret.create`: create encrypted protected records.
- `protected.revoke` / `secret.revoke`: revoke protected records.

Portable pipeline:

```text
ingest protected value
-> classify secret / sensitive_fact / public
-> encrypt at rest
-> expose only ProtectedRef in OACS records
-> require CapabilityGrant for use/read/list/revoke
-> audit access with ids, scopes, hashes, and status
-> never persist plaintext in ContextCapsule, ToolCallResult, EvidenceRef, or AuditEvent
```

The Python reference CLI:

```bash
acs vault put --label prod_token --kind token --value "$TOKEN" --scope project --json
acs vault list --scope project --json
acs vault use sec_... --json
acs vault use sec_... --reveal --json
acs vault revoke sec_... --json
```

`vault use` is redacted by default. `--reveal` requires explicit
`secret.read` or `protected.read`; `protected.use` alone is not enough.

## RU
OACS рассматривает secrets и непубличные infrastructure facts как protected
values, а не как обычную memory. Граница стандарта - JSON shape и capability
semantics для `SecretRecord`, `SensitiveFact` и `ProtectedRef`; встроенный
Python vault является только одной reference implementation этой границы.

Классы protected values:

- `SecretRecord`: API keys, tokens, passwords, private keys, certificates и
  environment secrets.
- `SensitiveFact`: internal IPs, private hostnames, private URLs, topology и
  непубличные repo/deployment paths.
- `ProtectedRef`: redacted reference, которую можно помещать в memory, context,
  tool bindings, audit metadata или adapter payloads без раскрытия значения.

Доступ разделён намеренно:

- `protected.use`: разрешить tool или adapter использовать protected value без
  раскрытия plaintext агенту.
- `protected.read` / `secret.read`: явно раскрыть plaintext; это должно быть
  редким разрешением.
- `protected.list`: показать redacted refs.
- `protected.create` / `secret.create`: создать encrypted protected records.
- `protected.revoke` / `secret.revoke`: отозвать protected records.

Portable pipeline:

```text
ingest protected value
-> classify secret / sensitive_fact / public
-> encrypt at rest
-> expose only ProtectedRef in OACS records
-> require CapabilityGrant for use/read/list/revoke
-> audit access with ids, scopes, hashes, and status
-> never persist plaintext in ContextCapsule, ToolCallResult, EvidenceRef, or AuditEvent
```

Python reference CLI:

```bash
acs vault put --label prod_token --kind token --value "$TOKEN" --scope project --json
acs vault list --scope project --json
acs vault use sec_... --json
acs vault use sec_... --reveal --json
acs vault revoke sec_... --json
```

`vault use` по умолчанию redacted. `--reveal` требует явный `secret.read` или
`protected.read`; одного `protected.use` недостаточно.
