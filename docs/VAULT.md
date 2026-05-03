# External Vault Boundary / Внешняя граница Vault

## EN
OACS is not a vault. It does not define secret storage, key rotation,
revocation, recovery, provider policy, or plaintext release workflows.

OACS defines only the boundary needed to use secrets and non-public
infrastructure values safely inside context and adapter records:

- `ProtectedRef`: a redacted reference to a value held by an external vault or
  runtime adapter.
- `protected.use`: an adapter may resolve and use a protected value without
  exposing plaintext through OACS records.
- `protected.read` / `secret.read`: an external vault adapter may explicitly
  reveal plaintext. These capabilities should be rare and tightly scoped.
- Leak-prevention conformance: Context Capsules, ToolCallResult output,
  EvidenceRef public payloads, and AuditEvent metadata must not persist
  plaintext protected values.

External vault examples include 1Password, HashiCorp Vault, AWS Secrets
Manager, GCP Secret Manager, Azure Key Vault, SOPS, Doppler, Infisical, and OS
keychains.

Portable pipeline:

```text
external vault stores secret or sensitive fact
-> OACS stores/projects only ProtectedRef
-> tool adapter checks CapabilityGrant and resolves the ref outside OACS
-> adapter injects value ephemerally into env/header/file descriptor
-> ToolCallResult, EvidenceRef, AuditEvent, and ContextCapsule stay redacted
```

Example `ProtectedRef`:

```json
{
  "id": "pref_prod_api_token",
  "protected_type": "secret",
  "label": "production API token",
  "sensitivity": "restricted",
  "provider": "1password",
  "uri": "op://project/prod_api/token",
  "projection": "ref_only",
  "scope": ["project"],
  "allowed_tools": ["tool_deploy_status"],
  "status": "active"
}
```

The bundled Python package is a reference implementation of OACS records and
checks. It intentionally does not include a built-in vault.

## RU
OACS не является vault. Он не определяет secret storage, key rotation,
revocation, recovery, provider policy или workflows раскрытия plaintext.

OACS определяет только границу, нужную для безопасного использования secrets и
непубличных infrastructure values внутри context и adapter records:

- `ProtectedRef`: redacted reference на значение, которое хранится во внешнем
  vault или runtime adapter.
- `protected.use`: adapter может resolve и использовать protected value без
  раскрытия plaintext через OACS records.
- `protected.read` / `secret.read`: внешний vault adapter может явно раскрыть
  plaintext. Эти capabilities должны быть редкими и узко ограниченными.
- Leak-prevention conformance: Context Capsules, ToolCallResult output,
  EvidenceRef public payloads и AuditEvent metadata не должны сохранять
  plaintext protected values.

Примеры внешних vault: 1Password, HashiCorp Vault, AWS Secrets Manager, GCP
Secret Manager, Azure Key Vault, SOPS, Doppler, Infisical и OS keychains.

Portable pipeline:

```text
external vault stores secret or sensitive fact
-> OACS stores/projects only ProtectedRef
-> tool adapter checks CapabilityGrant and resolves the ref outside OACS
-> adapter injects value ephemerally into env/header/file descriptor
-> ToolCallResult, EvidenceRef, AuditEvent, and ContextCapsule stay redacted
```

Пример `ProtectedRef`:

```json
{
  "id": "pref_prod_api_token",
  "protected_type": "secret",
  "label": "production API token",
  "sensitivity": "restricted",
  "provider": "1password",
  "uri": "op://project/prod_api/token",
  "projection": "ref_only",
  "scope": ["project"],
  "allowed_tools": ["tool_deploy_status"],
  "status": "active"
}
```

Bundled Python package является reference implementation OACS records и checks.
Он намеренно не включает встроенный vault.
