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
```

`repo capture` writes a committed D1 episode with git branch, commit, dirty
state, and structured evidence. `repo context` builds a Context Capsule from
the repo scope so the next agent pass can start from explicit memory rather than
conversation history alone.

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
```

`repo capture` пишет committed D1 episode с git branch, commit, dirty state и
structured evidence. `repo context` строит Context Capsule из repo scope, чтобы
следующий agent pass начинался с явной памяти, а не только с истории диалога.
