# Repo Dogfood / Использование OACS в этом репозитории

## EN
OACS can now record its own development iterations as encrypted repo-scoped
memory.

```bash
export OACS_DB=./.agent/oacs/oacs.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json

acs repo capture --task "implement repo dogfood" \
  --summary "Added repo capture/context commands for OACS self-development." --json

acs repo context --task "continue OACS development" --json

acs repo proof-capture --task-id "subagent-shared-memory" --phase build \
  --summary "Implemented scoped shared memory and proof-loop adapter." --json

acs repo proof-context --task-id "subagent-shared-memory" --json
acs repo proof-status --task-id "subagent-shared-memory" --json
```

`repo capture` writes a committed D1 episode with git branch, commit, dirty
state, and structured evidence. `repo context` builds a Context Capsule from
the repo scope so the next agent pass can start from explicit memory rather than
conversation history alone.

`repo proof-*` is the OACS proof-loop adapter. It records bounded proof-loop
phases as encrypted D1 episodes, scopes them to `repo:<name>` and `task:<id>`,
and builds task capsules for parent agents or subagents. Grant subagents scoped
access with `acs capability grant-shared-memory --subject <actor> --scope
task:<id> --scope repo:<name> --json`.

## RU
OACS теперь может записывать собственные development iterations как encrypted
repo-scoped memory.

```bash
export OACS_DB=./.agent/oacs/oacs.db
export OACS_PASSPHRASE="<local-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json

acs repo capture --task "implement repo dogfood" \
  --summary "Added repo capture/context commands for OACS self-development." --json

acs repo context --task "continue OACS development" --json

acs repo proof-capture --task-id "subagent-shared-memory" --phase build \
  --summary "Implemented scoped shared memory and proof-loop adapter." --json

acs repo proof-context --task-id "subagent-shared-memory" --json
acs repo proof-status --task-id "subagent-shared-memory" --json
```

`repo capture` пишет committed D1 episode с git branch, commit, dirty state и
structured evidence. `repo context` строит Context Capsule из repo scope, чтобы
следующий agent pass начинался с явной памяти, а не только с истории диалога.

`repo proof-*` - OACS adapter для proof-loop. Он пишет bounded proof-loop phases
как encrypted D1 episodes, ограничивает их областями `repo:<name>` и
`task:<id>` и строит task capsules для parent agents или subagents. Дайте
subagent scoped access командой `acs capability grant-shared-memory --subject
<actor> --scope task:<id> --scope repo:<name> --json`.
