---
name: oacs-repo-memory
description: Use OACS/ACS during substantial repository work to build governed context, record command results as evidence, and checkpoint iterations.
---

# OACS Repo Context

This is a Cursor-facing client skill for repositories that use OACS/ACS. It is
not part of the OACS standard.

## Start

1. Define task scope and acceptance criteria.
2. Check current repository state:

```bash
git status --short
acs status --json
```

3. Build context:

```bash
acs context build --intent repo_development --scope project --json
```

## During Work

- Run project tools directly (`pytest`, `npm test`, `flutter test`, CI checks,
  deployment commands, retrieval tools, etc.).
- Record canonical results:

```bash
acs tool ingest-result \
  --tool-id local_verification \
  --tool-name local_verification \
  --tool-type external \
  --status completed \
  --input '{"commands":["<command>"]}' \
  --output '{"status":"PASS","summary":"<short factual summary>"}' \
  --json
```

- Inspect evidence refs that matter:

```bash
acs evidence inspect <ev_...> --json
```

- Turn evidence into durable memory only after review. Keep D1 episodes cheap;
  D2+ facts/procedures and D3-D5 patterns need explicit evidence-backed review.

## Finish

1. Run current verification.
2. Run leak/secret checks appropriate for the repository.
3. Ingest both results as evidence.
4. Add a checkpoint:

```bash
acs checkpoint add \
  --task "<task-id>" \
  --summary "<what changed and why>" \
  --next "<next step or Done>" \
  --evidence <ev_...> \
  --json
```

5. Final response must name checks run, residual risks, and any OACS blocker.

## Guardrails

- OACS is not the tool orchestrator.
- Do not replace OACS context build with a local heuristic for substantial
  repository work.
- Standalone tool evidence is not projected into context unless a reviewed
  memory references it.
- Preserve attribution roles in distilled memory.
- Never read, print, or commit `.agent/oacs/key.json`,
  `.agent/oacs/unlocked.key`, `.agent/oacs`, `.oacs`, key material,
  passphrases, local databases, or private agent state.
