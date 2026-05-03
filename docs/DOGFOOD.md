# Development Dogfood / Использование OACS в этом репозитории

## EN
This document is an internal validation note for the reference implementation.
It is not part of the OACS v1.0 standard surface. It shows that ordinary
OACS memory/context operations can record development iterations as encrypted
repo-scoped memory.

Agent workflow in this repository:

1. State task scope and acceptance criteria before implementation.
2. Build OACS context when prior repo memory matters.
3. Record canonical command outputs, external retrieval, CI, and release results
   as evidence with `acs tool ingest-result`.
4. Inspect proof with `acs evidence list` / `acs evidence inspect`.
5. Attach durable evidence to project memory with `acs memory sharpen`.
6. Close every iteration with an OACS checkpoint/commit that references the
   relevant evidence refs and records next steps.
7. Run verification and a leak/secret check against the current codebase before
   claiming completion, then ingest both command results as evidence.

```bash
export OACS_DB=./.oacs/dogfood.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs skill scan examples/skills --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"capture","task":"implement repo dogfood","summary":"Added repo dogfood skill for OACS self-development.","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' \
  --json
```

The removable `codex_oacs_runtime` skill writes committed D1 episodes and
builds Context Capsules from repo scope so another local agent pass can start
from explicit memory rather than conversation history alone.

For controlled auto-memory during local development:

```bash
acs skill run codex_oacs_runtime \
  --payload '{"action":"auto_start","task":"implement next OACS slice","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"autorun","task":"verify next OACS slice","command":"pytest -q","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"auto_finish","task":"implement next OACS slice","summary":"Added and verified the next OACS slice.","outcome":"implemented","cwd":"."}' \
  --json
```

`auto-start` only builds context and records audit metadata; it does not write
memory. `auto-finish` and `autorun` commit only D1 repo episodes. D2 facts,
procedures, rules, and D3-D5 patterns still require explicit OACS
`memory propose` / `memory commit` review.

When running dogfood in `OACS_POLICY_MODE=strict`, grant the active actor
ordinary memory/query/read, `context.build`, `context.explain`, evidence,
checkpoint, and audit permissions first. The dogfood skill is a reference
adapter and must not depend on bootstrap authority in strict mode.

Canonical proof outputs should be ingested as evidence:

```bash
acs tool ingest-result \
  --tool-id repo_check \
  --tool-name "Repository check" \
  --output '{"command":"pytest -q","status":"pass","summary":"102 passed"}' \
  --source-uri "repo://checks/pytest" \
  --json

acs evidence list --kind tool_result --json
acs evidence inspect <ev_...> --json
```

Per-iteration closeout should leave both task state and leak/secret review in
OACS:

```bash
acs run --label "secret scan" -- <project-secret-scanner-command>

acs checkpoint add \
  --task "implement next OACS slice" \
  --summary "Iteration verified and secret scan passed." \
  --next "Continue with the next roadmap slice." \
  --evidence ev_... \
  --json
```

The secret scan can be `gitleaks`, a CI secret scanner, or a project-specific
deny-pattern check. The important contract for this repository is that the
result is captured as OACS evidence for every iteration.

## RU
Этот документ - internal validation note для reference implementation. Он не
является частью OACS v1.0 standard surface. Он показывает, что ordinary
OACS memory/context operations могут записывать development iterations как
encrypted repo-scoped memory.

Agent workflow в этом репозитории:

1. Зафиксировать scope задачи и acceptance criteria до implementation.
2. Собрать OACS context, если важна предыдущая repo memory.
3. Записывать canonical command outputs, external retrieval, CI и release
   results как evidence через `acs tool ingest-result`.
4. Проверять proof через `acs evidence list` / `acs evidence inspect`.
5. Привязывать durable evidence к project memory через `acs memory sharpen`.
6. Закрывать каждую итерацию OACS checkpoint/commit с relevant evidence refs и
   next steps.
7. Запускать verification и leak/secret check по текущему codebase перед claim
   completion, затем ingest оба результата как evidence.

```bash
export OACS_DB=./.oacs/dogfood.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs skill scan examples/skills --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"capture","task":"implement repo dogfood","summary":"Added repo dogfood skill for OACS self-development.","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' \
  --json
```

Отключаемый `codex_oacs_runtime` skill пишет committed D1 episodes и
строит Context Capsules из repo scope, чтобы другой local agent pass начинался
с явной памяти, а не только с истории диалога.

Для controlled auto-memory во время локальной разработки:

```bash
acs skill run codex_oacs_runtime \
  --payload '{"action":"auto_start","task":"implement next OACS slice","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"autorun","task":"verify next OACS slice","command":"pytest -q","cwd":"."}' \
  --json

acs skill run codex_oacs_runtime \
  --payload '{"action":"auto_finish","task":"implement next OACS slice","summary":"Added and verified the next OACS slice.","outcome":"implemented","cwd":"."}' \
  --json
```

`auto-start` только строит context и пишет audit metadata; memory он не
записывает. `auto-finish` и `autorun` коммитят только D1 repo episodes. D2
facts, procedures, rules и D3-D5 patterns по-прежнему требуют явного review
через OACS `memory propose` / `memory commit`.

Canonical proof outputs нужно ingest как evidence:

```bash
acs tool ingest-result \
  --tool-id repo_check \
  --tool-name "Repository check" \
  --output '{"command":"pytest -q","status":"pass","summary":"102 passed"}' \
  --source-uri "repo://checks/pytest" \
  --json

acs evidence list --kind tool_result --json
acs evidence inspect <ev_...> --json
```

Per-iteration closeout должен оставлять в OACS и task state, и leak/secret
review:

```bash
acs run --label "secret scan" -- <project-secret-scanner-command>

acs checkpoint add \
  --task "implement next OACS slice" \
  --summary "Iteration verified and secret scan passed." \
  --next "Continue with the next roadmap slice." \
  --evidence ev_... \
  --json
```

Secret scan может быть `gitleaks`, CI secret scanner или project-specific
deny-pattern check. Важный contract для этого репозитория: результат должен
быть записан как OACS evidence на каждой итерации.
