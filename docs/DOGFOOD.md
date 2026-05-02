# Development Dogfood / Использование OACS в этом репозитории

## EN
This document is an internal validation note for the reference implementation.
It is not part of the OACS v0.1 draft standard surface. It shows that ordinary
OACS memory/context operations can record development iterations as encrypted
repo-scoped memory.

Agent workflow in this repository:

1. State task scope and acceptance criteria before implementation.
2. Build OACS context when prior repo memory matters.
3. Record canonical command outputs, external retrieval, CI, and release results
   as evidence with `acs tool ingest-result`.
4. Inspect proof with `acs evidence list` / `acs evidence inspect`.
5. Attach durable evidence to project memory with `acs memory sharpen`.
6. Rebuild context and verify against the current codebase before claiming
   completion.

```bash
export OACS_DB=./.oacs/dogfood.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs skill scan examples/skills --json

acs skill run repo_development_memory \
  --payload '{"action":"capture","task":"implement repo dogfood","summary":"Added repo dogfood skill for OACS self-development.","cwd":"."}' \
  --json

acs skill run repo_development_memory \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' \
  --json
```

The removable `repo_development_memory` skill writes committed D1 episodes and
builds Context Capsules from repo scope so another local agent pass can start
from explicit memory rather than conversation history alone.

For controlled auto-memory during local development:

```bash
acs skill run repo_development_memory \
  --payload '{"action":"auto_start","task":"implement next OACS slice","cwd":"."}' \
  --json

acs skill run repo_development_memory \
  --payload '{"action":"autorun","task":"verify next OACS slice","command":"pytest -q","cwd":"."}' \
  --json

acs skill run repo_development_memory \
  --payload '{"action":"auto_finish","task":"implement next OACS slice","summary":"Added and verified the next OACS slice.","outcome":"implemented","cwd":"."}' \
  --json
```

`auto-start` only builds context and records audit metadata; it does not write
memory. `auto-finish` and `autorun` commit only D1 repo episodes. D2 facts,
procedures, rules, and D3-D5 patterns still require explicit OACS
`memory propose` / `memory commit` review.

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

## RU
Этот документ - internal validation note для reference implementation. Он не
является частью OACS v0.1 draft standard surface. Он показывает, что ordinary
OACS memory/context operations могут записывать development iterations как
encrypted repo-scoped memory.

Agent workflow в этом репозитории:

1. Зафиксировать scope задачи и acceptance criteria до implementation.
2. Собрать OACS context, если важна предыдущая repo memory.
3. Записывать canonical command outputs, external retrieval, CI и release
   results как evidence через `acs tool ingest-result`.
4. Проверять proof через `acs evidence list` / `acs evidence inspect`.
5. Привязывать durable evidence к project memory через `acs memory sharpen`.
6. Пересобирать context и проверять текущий код перед claim completion.

```bash
export OACS_DB=./.oacs/dogfood.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs skill scan examples/skills --json

acs skill run repo_development_memory \
  --payload '{"action":"capture","task":"implement repo dogfood","summary":"Added repo dogfood skill for OACS self-development.","cwd":"."}' \
  --json

acs skill run repo_development_memory \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' \
  --json
```

Отключаемый `repo_development_memory` skill пишет committed D1 episodes и
строит Context Capsules из repo scope, чтобы другой local agent pass начинался
с явной памяти, а не только с истории диалога.

Для controlled auto-memory во время локальной разработки:

```bash
acs skill run repo_development_memory \
  --payload '{"action":"auto_start","task":"implement next OACS slice","cwd":"."}' \
  --json

acs skill run repo_development_memory \
  --payload '{"action":"autorun","task":"verify next OACS slice","command":"pytest -q","cwd":"."}' \
  --json

acs skill run repo_development_memory \
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
