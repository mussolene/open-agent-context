# OACS v1.0.0 Release Notes

OACS v1.0.0 freezes the portable Open Agent Context Standard contract for
agent memory, context, permissions, audit, evidence, protected references, and
operation traces.

## Standard Surface

- Stable JSON contracts cover `ContextCapsule`, `MemoryRecord`,
  `CapabilityGrant`, `RuleManifest`, `SkillManifest`, `ToolBinding`,
  `McpBinding`, `EvidenceRef`, `AuditEvent`, `ProtectedRef`,
  `MemoryOperation`, `ContextOperation`, `memory_call`, `MemoryLoopRun`,
  `ToolCallResult`, `StorageSelector`, `RetrievalQuery`, and
  `RetrievalResult`.
- Positive fixtures are language-neutral examples that conforming
  implementations should accept.
- Negative fixtures are required rejection examples for semantic and
  adapter-boundary checks.
- `actor` and `context_capsule_export` remain draft support, not v1.0 stable
  portable records.

## Reference Implementation

- The Python package, `acs` CLI, FastAPI API, SQLite backend, encryption layer,
  registries, memory loop, and validation adapters are the bundled reference
  implementation.
- Python, SQLite, CLI/API UX, MCP stdio execution, LM Studio, benchmarks, repo
  dogfood, and hosted API choices do not expand the OACS standard unless a
  stable schema or spec section explicitly requires them.
- The package is published to PyPI as `oacs==1.0.0`.

## Verification

- Local release gate passed: ruff, mypy, pytest, conformance validation, package
  build, and twine metadata checks.
- Fresh PyPI smoke passed: `acs --version` reported `acs 1.0.0`, and
  `acs conformance validate --json` accepted all positive fixtures and rejected
  all negative fixtures.
- Release proof was recorded in OACS evidence and checkpoint memory.
