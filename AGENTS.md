## OACS Project Policy

For substantial repository work, use the globally installed `oacs` Skill for
durable context and the `proof-loop` Skill for delivery verification. This
repository dogfoods OACS project memory and must not duplicate either general
Codex operating protocol here.

Project-specific requirements:

1. Record canonical verification and release results as OACS evidence.
2. Close each completed iteration with an OACS checkpoint that references the
   relevant evidence and names the next step.
3. Run the repository leak and secret check before completion.

Hard rules:

- Do not claim completion unless the iteration has OACS evidence for checks,
  checkpoint/commit state, and leak/secret review.
- OACS is not the tool orchestrator. It records external tool results as
  governed evidence/context for agents to use.
- Standalone tool-result evidence does not enter `ContextCapsule.evidence_refs`
  by itself. It is projected only through included memories that reference it.
- Keep this root `AGENTS.md` lean. The installed Skills own the general OACS
  and proof-loop workflows; project documentation should contain only
  repository-specific guidance.
