# Agent Workflow UX / Агентский workflow UX

## EN

OACS remains a small memory/context contract. The commands below are reference
CLI conveniences for long agent development sessions; they do not make OACS an
orchestrator or scheduler.

Project-local setup:

```bash
acs init --project --json
acs status --json
```

`acs status` reports the discovered database, key state, and high-level record
counts. Database discovery checks `OACS_DB`, then searches upward for
`.agent/oacs/oacs.db` or `.oacs/oacs.db`, and falls back to `./.oacs/oacs.db`.

Checkpoint temporary task state:

```bash
acs checkpoint add --task "release 0.3.2a1" \
  --summary "CLI UX implemented" \
  --next "run verification" \
  --evidence ev_... \
  --json

acs checkpoint latest --task "release 0.3.2a1" --json
```

Checkpoints are task traces, not reusable verified memory. Use memory only for
durable facts, procedures, rules, and reusable patterns.

Resume after context compaction:

```bash
acs resume --scope project --json
```

`acs resume` aggregates the latest checkpoint, recent tool-result evidence,
recent memory metadata, recent Context Capsules, and recent audit events.

Governed command evidence:

```bash
acs run --label "pytest" -- pytest -q
```

`acs run` executes only the command supplied by the caller and records stdout,
stderr, exit code, and provenance as a `tool_result` `EvidenceRef`. It does not
choose, schedule, or plan commands.

Project-local deny patterns:

```bash
acs policy add-deny-pattern "passphrase|license|/Users/" --json
```

Deny-pattern rules are checked by `memory propose`, `tool ingest-result`,
`acs run`, and checkpoint capture. Use them to block or warn on project-specific
leak risks.

Per-iteration closeout:

```bash
acs run --label "verification" -- pytest -q
acs run --label "secret scan" -- <project-secret-scanner-command>

acs checkpoint add --task "next OACS slice" \
  --summary "Verified current iteration and secret scan passed" \
  --next "Continue with the next roadmap slice" \
  --evidence ev_... \
  --json
```

Each development iteration should leave OACS evidence for verification,
leak/secret review, and the checkpoint/commit state. This is repository
workflow policy for developing the reference implementation; it is not a core
runtime requirement of the OACS standard.

## RU

OACS остаётся небольшим memory/context contract. Команды ниже являются
reference CLI conveniences для длинных agent development sessions; они не
делают OACS orchestrator или scheduler.

Project-local setup:

```bash
acs init --project --json
acs status --json
```

`acs status` показывает найденную базу, состояние ключа и общие counts записей.
Discovery проверяет `OACS_DB`, затем ищет вверх `.agent/oacs/oacs.db` или
`.oacs/oacs.db`, и иначе использует `./.oacs/oacs.db`.

Временное состояние задачи:

```bash
acs checkpoint add --task "release 0.3.2a1" \
  --summary "CLI UX implemented" \
  --next "run verification" \
  --evidence ev_... \
  --json

acs checkpoint latest --task "release 0.3.2a1" --json
```

Checkpoint - это task trace, а не reusable verified memory. Memory используйте
только для durable facts, procedures, rules и reusable patterns.

Resume после context compaction:

```bash
acs resume --scope project --json
```

`acs resume` собирает latest checkpoint, recent tool-result evidence, metadata
последних memories, Context Capsules и audit events.

Governed command evidence:

```bash
acs run --label "pytest" -- pytest -q
```

`acs run` выполняет только команду, которую передал caller, и записывает stdout,
stderr, exit code и provenance как `tool_result` `EvidenceRef`. Он не выбирает,
не планирует и не schedules команды.

Project-local deny patterns:

```bash
acs policy add-deny-pattern "passphrase|license|/Users/" --json
```

Deny-pattern rules проверяются в `memory propose`, `tool ingest-result`,
`acs run` и checkpoint capture. Используйте их для блокировки или предупреждений
по project-specific leak risks.

Per-iteration closeout:

```bash
acs run --label "verification" -- pytest -q
acs run --label "secret scan" -- <project-secret-scanner-command>

acs checkpoint add --task "next OACS slice" \
  --summary "Verified current iteration and secret scan passed" \
  --next "Continue with the next roadmap slice" \
  --evidence ev_... \
  --json
```

Каждая development iteration должна оставлять в OACS evidence для verification,
leak/secret review и checkpoint/commit state. Это workflow policy репозитория
для разработки reference implementation, а не core runtime requirement стандарта
OACS.
