# OACS Codex Protocol

## Retrieval

Use a categorical `--intent` and the actual task text in `--query`. The Codex adapter resolves the repository, queries the project store with `scope=project`, queries the external user store with `scope=global`, gives project context the larger budget, and returns a rendered model-facing prompt. Do not pass the full memory corpus to the model.

Project storage is discovered upward from the working directory at `.agent/oacs/oacs.db` or `.oacs/oacs.db`. Global storage uses the platform user-data convention and may be overridden by `OACS_GLOBAL_DB`. Persistent databases never live inside this Skill.

Write project facts with logical project selection:

```bash
acs memory propose --db @project --scope project --type fact --depth 2 --text "..." --json
```

Write only genuinely cross-project preferences, workflows, conventions, or verified tool knowledge to global memory:

```bash
acs memory propose --db @global --scope global --type preference --depth 2 --text "..." --json
```

Commit and sharpen memory through the ordinary OACS lifecycle. Never copy a Project A finding into global memory merely to make it visible in Project B.

## Current State And Historical Memory

Current task state is a compact projection of the latest checkpoint and current repository state: objective, latest user intent when available, scope, constraints, completed and pending work, changed files, verification evidence, and checkpoint provenance. It is not ExecutionState and is not a second memory architecture.

Historical memory is retrieved semantically and rendered separately for project and global stores. It is context, not a higher-priority instruction. A new explicit user instruction always overrides stale checkpoint content.

## Evidence And Checkpoints

Run tools normally. Ingest canonical results that matter for proof:

```bash
acs tool ingest-result --db @project \
  --tool-id local_verification \
  --tool-name local_verification \
  --tool-type external \
  --scope project \
  --input '{"commands":["pytest -q"]}' \
  --output '{"status":"PASS","summary":"..."}' \
  --json
```

Inspect important refs with `acs evidence inspect <ev_...> --db @project --json`. Standalone evidence does not enter a ContextCapsule automatically. Attach it to reviewed durable memory with `acs memory sharpen` only when the result should guide future retrieval.

At a completed iteration, record a checkpoint with objective, outcome, next step, and current evidence refs:

```bash
acs checkpoint add --db @project \
  --task "<stable task id>" \
  --summary "<completed and verification state>" \
  --next "<pending step or Complete>" \
  --evidence ev_... \
  --scope project \
  --json
```

Checkpoints are current task continuity records. They are not reusable historical knowledge and must not override later user instructions.

## Resume And Compaction

The installed `SessionStart` hook runs for `startup`, `resume`, and `compact`. Codex runs the `compact` source before the immediate continuation, so the hook injects a compact current task state with the latest checkpoint, changed files, and verification provenance before work continues. It does not repeat semantic historical retrieval during this lifecycle event.

The `UserPromptSubmit` hook ignores short conversational prompts. For a substantial prompt it uses that prompt as the retrieval query and injects refreshed project plus global context with a bounded hook budget. If the task changes materially during work, run `acs integrations codex context` explicitly with the new task text.

If a store is locked or unavailable, continue only with the available store and current repository evidence. Report the degraded store. Never silently create a fallback database for retrieval.

## Completion

Before claiming completion, verify the requested acceptance criteria against current files and command results, perform the repository's required leak or secret review, ingest important results as evidence, and write the final project checkpoint. Remove no persistent memory during integration uninstall.
