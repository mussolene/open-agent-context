## OACS / ACS Repository Workflow

Use OACS/ACS for substantial repository work as the governed local context,
evidence, and checkpoint layer. OACS records facts and proof; it does not choose
or run tools for the assistant.

Required loop:

1. State scope and acceptance criteria before implementation.
2. Decide whether OACS context is needed. Use it for durable project memory,
   previous decisions, policy, evidence, checkpoints, or long-running state.
   Skip context build for simple visible-file edits where current files and the
   user request are sufficient.
3. Build context only when prior memory or evidence matters:
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
- OACS context was selected only when it added project memory, policy,
  evidence, or prior-decision value.
- No `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`, `.agent/oacs`,
  `.oacs`, keys, passphrases, local databases, or private agent state are read,
  printed, or committed.
