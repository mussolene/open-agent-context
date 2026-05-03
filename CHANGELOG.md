# Changelog

## Unreleased

## 1.0.4 - 2026-05-03

### Fixed

- Stabilized the `acs tool ingest-result` denial-message test across GitHub
  Actions terminal width and ANSI rendering differences.

## 1.0.3 - 2026-05-03

### Added

- Added `acs capability grant-evidence` for tool-scoped `evidence.ingest`
  grants used by `acs tool ingest-result`.

### Changed

- `acs tool ingest-result` now reports a clear capability error with the
  matching `grant-evidence` command instead of exposing a raw traceback.
- Documented that `grant-tool` authorizes `tool.call`, while ingesting results
  produced by another orchestrator requires tool-scoped `evidence.ingest`.

## 1.0.2 - 2026-05-03

### Changed

- Kept unreadable-memory context-build diagnostics outside the portable
  `ContextCapsule` standard schema; Python CLI/API now return those warnings as
  reference-side metadata beside the capsule.
- Removed defensive status fallback that could mask an unlocked-key memory
  decrypt health failure.

## 1.0.1 - 2026-05-03

### Added

- Added DB decrypt health diagnostics in `acs status`, `acs doctor`, and
  `acs memory doctor`.
- Added memory repair workflows: `acs memory quarantine`,
  `acs memory export-readable`, and `acs memory purge-unreadable`.

### Changed

- Made `acs memory query` and `acs context build` skip unreadable encrypted
  memory records by default, emit structured warnings, and support `--strict`
  fail-fast behavior.
- Replaced raw AES-GCM decrypt tracebacks with `MemoryDecryptError` domain
  errors that expose safe record metadata without encrypted content.
- Documented which commands require decrypting existing memories and which
  append-only commands can operate while memory health is degraded.
- Removed CI/release workflow dependency on `actions/upload-artifact` and
  `actions/download-artifact` while those actions still declare a deprecated
  Node.js runtime; trusted-publishing jobs now build and check distributions
  directly before publishing.
- Added GitHub Release creation to the stable tag publishing path.
- Updated roadmap and glossary language for the post-1.0 state while preserving
  Python as one reference implementation rather than the standard itself.

## 1.0.0 - 2026-05-03

### Added

- v1.0 stable standard release checklist in `docs/V1_RELEASE_CHECKLIST.md`.
- Freeze-prep manifest closure with no remaining open freeze-prep work.
- Semantic negative conformance fixtures for adapter-boundary checks that are
  not fully expressible as JSON Schema constraints.

### Changed

- Promoted the public package metadata to stable `1.0.0`.
- Froze the v1.0 stable-candidate schema surface with strict top-level shape,
  portable field descriptions, positive fixtures, and required negative
  coverage.
- Kept `actor` and `context_capsule_export` as draft support for v1.0: stable
  records reference actor IDs, raw `ContextCapsule` JSON remains the portable
  context record, and export envelopes remain reference packaging.

### Notes

- The Python package remains one reference implementation of the OACS standard,
  not the only conforming runtime or transport.
- SQLite, FastAPI, CLI UX, MCP stdio execution, hosted APIs, LM Studio,
  benchmarks, and repo dogfood remain reference or adapter behavior unless a
  stable schema or spec section explicitly requires them.

## 0.3.5a1 - 2026-05-03

### Added

- External vault boundary schema for `ProtectedRef`.
- Negative conformance fixtures that reject plaintext protected values in
  Context Capsules, ToolCallResult output, EvidenceRef public payloads, and
  AuditEvent metadata.
- Negative conformance fixtures that reject masked protected value fragments and
  suffix hints in context, tool, audit, and evidence surfaces.
- `docs/VAULT.md` for the external-vault pipeline.

### Changed

- Extended conformance validation to include protected value fixtures and
  plaintext and masked leak rejection examples.
- Tightened `ProtectedRef` so secret references require an external provider
  and URI, and portable projections persist only `ref_only` or `redacted`.
- Kept vault storage, rotation, revocation, and provider-specific secret
  handling outside the `acs` reference implementation.
- Kept `acs vault` outside the reference CLI surface; vault access belongs to
  external adapters.

### Notes

- This is still an alpha draft/reference-implementation release, not a v1.0
  schema freeze.
- OACS intentionally has no built-in vault. The standard records external
  `ProtectedRef` values; vault storage and plaintext release stay in external
  adapters.

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
- Repo dogfood lives in `examples/skills/codex_oacs_runtime` and is not
  part of the installed core package surface.
