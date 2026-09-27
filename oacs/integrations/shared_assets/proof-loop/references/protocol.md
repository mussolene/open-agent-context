# Proof Loop Protocol

## 1. Freeze

Preserve the current user request and write explicit acceptance criteria labeled `AC1`,
`AC2`, and so on. Record constraints, non-goals, assumptions that can affect correctness,
and the planned proof for each criterion.

If OACS is available, retrieve relevant project context with the actual task as the query.
Use global context only for relevant cross-project practices. Store the compact objective,
scope, constraints, completed and pending work, changed files, and verification state in an
OACS checkpoint. Do not let recovered state override the current request.

## 2. Build

Inspect repository guidance and existing implementation before editing. Reuse or extend
the existing capability when it substantially covers the task. Implement the smallest
coherent change that can satisfy the frozen criteria. Keep unrelated changes untouched.

The builder may run focused checks while working, but its report is not the final verdict.
When OACS is available, ingest important command results and canonical external facts as
evidence. Evidence must identify the command or source, result, time, and relevant scope.

## 3. Prove

For each acceptance criterion, choose the cheapest proof that actually establishes it:

1. current source or configuration inspection;
2. static validation, schema validation, or linting;
3. focused unit or component tests;
4. integration or runtime tests;
5. end-to-end or user-interface tests when behavior crosses those boundaries.

Do not substitute a lower proof level when the criterion concerns runtime or visible
behavior. Do not run an expensive level when a cheaper level fully proves the criterion.

Keep large raw output in its native artifact or external system. Put only compact results
and references into OACS. Promote a result to durable memory only when it is reusable
project knowledge, not merely current task output.

## 4. Verify Freshly

The verifier is not the implementer. It must evaluate the current repository and rerun the
relevant checks. Prior summaries, historical memory, and sibling-agent reports are leads,
not proof.

For every criterion return exactly one status:

- `PASS`: current evidence proves it;
- `FAIL`: current evidence contradicts it or implementation is incomplete;
- `UNKNOWN`: it cannot be verified with the available environment or authority.

For every non-PASS result, include a minimal reproduction and the smallest defensible fix.
The verifier does not modify production code.

## 5. Fix and Close

The fixer reconfirms each reported gap, makes the smallest safe correction, reruns affected
checks, and returns the result to a fresh verification pass. Do not preserve the failed
implementation as an implicit fallback unless the user explicitly requires compatibility.

Before completion:

- every acceptance criterion is `PASS`;
- repository-required tests and leak or secret checks are current;
- important results are recorded as OACS evidence when OACS is available;
- the final OACS checkpoint records outcome, changed files, verification status, evidence
  references, and the next step or `Complete`;
- no obsolete helper, import, branch, or temporary artifact introduced by the work remains.

If any criterion remains `FAIL` or `UNKNOWN`, report that status plainly instead of claiming
completion.

## Origins

This generic protocol was refactored from the Apache-2.0
[`onec-atomic-proof-loop`](https://github.com/mussolene/onec-workflow-proof)
workflow, which in turn credits
[`repo-task-proof-loop`](https://github.com/DenisSergeevitch/repo-task-proof-loop)
and `andrej-karpathy-skills`. Domain-specific 1C routing remains in the specialized Skill.
