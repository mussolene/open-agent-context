## OACS Repo Development Workflow

For substantial features, refactors, bug fixes, and release work in this
repository, dogfood OACS instead of writing a parallel sidecar task-artifact
tree.

Required sequence:

1. State the task scope and explicit acceptance criteria (`AC1`, `AC2`, ...)
   before implementation.
2. Build or inspect repo context through OACS when prior project memory matters:
   `acs context build --intent repo_development --scope project --json`.
3. Treat command outputs, external retrieval, CI results, package publication
   results, and other canonical project facts as evidence:
   `acs tool ingest-result ...`.
4. Use `acs evidence inspect <ev_...>` and
   `acs evidence list --kind tool_result --json` for proof/debugging.
5. If evidence should become durable project knowledge, distill it into memory
   and attach the evidence ref with `acs memory sharpen`.
6. For each completed iteration, record an OACS checkpoint/commit with the
   relevant evidence refs, next step, and outcome.
7. Run a fresh verification pass and a leak/secret check against the current
   codebase, then ingest both results as evidence.
8. Rerun failed checks after fixes.
9. If verification is not `PASS`, explain the problem, apply the smallest safe
   fix, and reverify.

Hard rules:

- Do not claim completion unless every acceptance criterion is `PASS`.
- Do not claim completion unless the iteration has OACS evidence for checks,
  checkpoint/commit state, and leak/secret review.
- Verifiers judge current code and current command results, not prior chat
  claims.
- Fixes should be the smallest defensible diff.
- OACS is not the tool orchestrator. It records external tool results as
  governed evidence/context for agents to use.
- Standalone tool-result evidence does not enter `ContextCapsule.evidence_refs`
  by itself. It is projected only through included memories that reference it.
- Keep this root `AGENTS.md` lean. Put expanded guidance in docs instead of
  recreating a parallel task-artifact system.
