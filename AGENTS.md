## OACS Project Policy

For substantial repository work, use the globally installed `oacs` Skill. This
repository dogfoods OACS project memory and must not duplicate the general
Codex operating protocol here.

Project-specific requirements:

1. State the task scope and explicit acceptance criteria (`AC1`, `AC2`, ...)
   before implementation.
2. Record canonical verification and release results as OACS evidence.
3. Close each completed iteration with an OACS checkpoint that references the
   relevant evidence and names the next step.
4. Run fresh verification and a leak/secret check before completion.

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
- Keep this root `AGENTS.md` lean. The installed Skill owns the general OACS
  workflow; project documentation should contain only repository-specific
  guidance.
