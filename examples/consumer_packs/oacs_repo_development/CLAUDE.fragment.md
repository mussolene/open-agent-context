## OACS / ACS Repository Workflow

Use OACS/ACS for substantial repository work as the governed local context,
evidence, and checkpoint layer. OACS records facts and proof; it does not choose
or run tools for the assistant.

Required loop:

1. State scope and acceptance criteria before implementation.
2. Ask the reference context gate before building context:
   `acs context gate --intent repo_development --scope project --task "<task>" --json`.
   If the gate returns `decision=build`, build context. Treat `decision=skip`
   as valid only for tiny visible-file edits; when work is substantial,
   ambiguous, domain-heavy, or release/CI/security/tooling related, build
   context or explicitly report that OACS context is unavailable.
3. Build context when the gate says `build`, when prior memory/evidence may
   matter, or when in doubt:
   `acs context build --intent repo_development --scope project --json`.
4. Record canonical command results as evidence with
   `acs tool ingest-result ...`.
5. Inspect evidence with `acs evidence inspect <ev_...> --json` when debugging
   or proving completion.
6. Distill only reviewed evidence-backed facts/procedures into durable memory.
7. Add an OACS checkpoint with evidence refs and next step after each iteration.
8. Run fresh verification and leak/secret checks before finalizing.

Completion bar:

- All acceptance criteria are satisfied.
- Verification is current and passing.
- OACS evidence exists for important command outputs.
- A checkpoint records the outcome and next step.
- `decision=skip` was used only for tiny visible-file edits and did not bypass
  verification, evidence, or checkpoint requirements for substantial work.
- No `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`, `.agent/oacs`,
  `.oacs`, keys, passphrases, local databases, or private agent state are read,
  printed, or committed.
