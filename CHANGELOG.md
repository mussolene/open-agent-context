# Changelog

## 0.3.0a1 - Unreleased

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
