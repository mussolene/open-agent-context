## OACS / ACS Repository Workflow

For substantial features, refactors, bug fixes, investigations, and release
work, use OACS/ACS as the governed local context, evidence, and checkpoint
layer. Do not create a parallel private task-artifact tree unless the user asks
for one.

Required sequence:

1. State task scope and explicit acceptance criteria (`AC1`, `AC2`, ...).
2. Decide whether OACS context is needed before building it. Use OACS for
   durable project memory, previous decisions, policy, evidence, checkpoints,
   or long-running state. Skip OACS context for simple visible-file edits where
   current files and user instructions are sufficient.
3. Build or inspect repository context through OACS only when prior project
   memory or evidence matters:
   `acs context build --intent repo_development --scope project --json`.
4. Run external tools normally. OACS does not schedule tools; it records their
   canonical results as governed evidence.
5. Treat command outputs, external retrieval, CI results, package publication,
   deployment results, and manual verification as evidence:
   `acs tool ingest-result ...`.
6. Inspect important evidence with `acs evidence inspect <ev_...> --json`.
7. If evidence should become durable project knowledge, distill it into memory
   and attach the evidence ref with the memory lifecycle commands.
8. Record a checkpoint for each completed iteration with outcome, evidence
   refs, and next step:
   `acs checkpoint add ... --evidence <ev_...> --json`.
9. Run current verification and a leak/secret check before claiming completion.

Hard rules:

- Do not claim completion unless every acceptance criterion is `PASS`.
- Do not claim completion unless current verification, OACS evidence, and an
  OACS checkpoint exist for the iteration.
- Verifiers judge current files and current command results, not chat claims.
- OACS is not the tool orchestrator; it is the governed memory/context/evidence
  layer.
- Do not prepend OACS context unconditionally. Context should be selected for
  tasks that need durable memory, policy, evidence, or prior decisions.
- Standalone tool-result evidence does not enter `ContextCapsule.evidence_refs`
  by itself. It is projected only through included memories that reference it.
- Preserve attribution when distilling memory: user instructions, agent
  decisions, tool observations, project policies, human approvals, derived
  memory, and system policy are different roles.
- Do not read, print, or commit `.agent/oacs/key.json`,
  `.agent/oacs/unlocked.key`, `.agent/oacs`, `.oacs`, local databases,
  passphrases, or private agent state.
