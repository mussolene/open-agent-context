# PyPI Quickstart / Быстрый старт через PyPI

## EN
This is the shortest public install path for the OACS v1.0 reference
implementation.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install oacs==1.0.0

export OACS_DB=./.oacs/oacs.db
export OACS_PASSPHRASE="<choose-a-local-dev-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs actor create --type human --name "User" --json
```

Create and retrieve one scoped memory:

```bash
CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "In project Alpha reports are generated with make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha report" --scope project --json
acs context build --intent answer_project_question --scope project --budget 4000 --json
```

Run the local proof demo from a source checkout:

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```

## RU
Это самый короткий публичный путь установки для OACS v1.0 reference
implementation.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install oacs==1.0.0

export OACS_DB=./.oacs/oacs.db
export OACS_PASSPHRASE="<choose-a-local-dev-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs actor create --type human --name "User" --json
```

Создать и найти одну scoped memory:

```bash
CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "В проекте Alpha отчёты генерируются через make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha отчёты" --scope project --json
acs context build --intent answer_project_question --scope project --budget 4000 --json
```

Запустить локальное proof demo из source checkout:

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```
