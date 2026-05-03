# Changelog

## 0.3.5a1 - 2026-05-03

### Added

- Protected value and vault boundary schemas for `SecretRecord`,
  `SensitiveFact`, and `ProtectedRef`.
- Negative conformance fixtures that reject plaintext protected values in
  Context Capsules, ToolCallResult output, EvidenceRef public payloads, and
  AuditEvent metadata.
- Reference `acs vault put/list/use/revoke` commands backed by encrypted SQLite
  storage and capability-gated `protected.use` / `protected.read` semantics.
- `docs/VAULT.md` for the standard boundary and Python reference pipeline.

### Changed

- Extended conformance validation to include protected value fixtures and
  plaintext leak rejection examples.

## 0.3.4a1 - 2026-05-03

### Added

- Conformance fixtures for `RuleManifest`, `SkillManifest`, `ToolBinding`,
  `McpBinding`, and `AuditEvent`.
- Negative conformance fixtures for audit hash mismatch, capability depth
  overflow, implicit wildcard scope/namespace grants, and HTTP tool bindings
  without explicit network opt-in.

### Changed

- Tightened manifest, binding, and audit event schemas with explicit status/risk
  enums, additional-property rejection, and reference-runtime extension fields.
- Extended `acs conformance validate` to check audit hashes, explicit wildcard
  semantics, and HTTP adapter opt-in semantics.

## 0.3.3a1 - 2026-05-03

### Added

- Language-neutral conformance fixtures under `conformance/fixtures/`.
- Negative adapter-boundary fixtures under `conformance/negative/`.
- Retrieval and storage selector conformance schemas and fixtures.
- `acs conformance validate` reference checker for bundled conformance fixtures.
- Schema-only conformance tests that validate fixtures without importing OACS
  Python models.
- `docs/INTEROPERABILITY.md` checklist for non-Python runtimes and adapters.

### Changed

- Marked Python, SQLite, CLI/API, benchmark, LM Studio, and repo dogfood
  behavior as reference-only unless promoted by the spec or JSON schemas.
- Included conformance artifacts in wheel and sdist builds.

## 0.3.2a2 - 2026-05-03

### Added

- `acs --version` / `acs -V` for CLI and release smoke checks.

## 0.3.2a1 - 2026-05-03

### Added

- Agent Workflow UX commands: `acs status`, `acs resume`, `acs checkpoint`,
  and `acs run`.
- Project-local database discovery for `.agent/oacs/oacs.db` and
  `.oacs/oacs.db`.
- `acs init --project` for repo-local `.agent/oacs/oacs.db` setup.
- `acs policy add-deny-pattern` with blocking/warn-only checks for memory
  proposals, evidence ingest, governed command evidence, and checkpoints.
- `docs/AGENT_WORKFLOW.md` for long agent development sessions.

### Notes

- Workflow UX remains reference CLI/adapters and does not expand the OACS v0.1
  draft core conformance surface or make OACS an orchestrator.

## 0.3.1a2 - 2026-05-02

### Added

- `acs evidence list` and `acs evidence inspect` for proof-loop/debugging.
- Canonical retrieval pattern documentation for external retrieval tools:
  `tool ingest-result` -> `EvidenceRef` -> `memory sharpen` -> `context build`.

### Changed

- Clarified that standalone tool-result evidence is not projected into
  `ContextCapsule.evidence_refs` until attached to an included memory.
- Updated PyPI quickstart and roadmap references for `0.3.1a2`.

## 0.3.1a1 - 2026-05-02

### Added

- Generic `ToolRunner` execution boundary for `ToolBinding`.
- `ToolCallResult` envelope and schema.
- Tool result evidence capture through `tool_result` `EvidenceRef` records.
- JSON schema validation for declared tool inputs and outputs.
- External tool result ingest for already-executed tools, with governed
  `EvidenceRef` capture, audit, CLI/API entry points, and Context Capsule
  projection through linked memory.

## 0.3.0a1 - 2026-05-02

Initial public prerelease candidate for the OACS v0.1 draft reference
implementation.

### Added

- OACS v0.1 draft documentation and JSON schemas.
- Python reference implementation with `acs` CLI and FastAPI API.
- Encrypted SQLite memory storage with local passphrase key provider.
- Context Capsule build/export/import/validation.
- Capability-scoped memory, context, tool, skill, and MCP adapter operations.
- Deterministic `memory_calls` and memory-loop execution.
- Script-backed skill execution through `acs skill scan` / `acs skill run`.
- Benchmark validation adapters and LM Studio-compatible benchmark execution.
- CI build, package build, wheel smoke tests, and release workflow.

### Notes

- This is an alpha prerelease of a draft standard reference implementation.
- Public benchmark adapters are validation artifacts, not OACS conformance.
- Repo dogfood lives in `examples/skills/repo_development_memory` and is not
  part of the installed core package surface.
