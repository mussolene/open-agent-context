# OACS v0.1 draft — Open Agent Context Standard

## EN
OACS v0.1 draft is a local proof-of-concept for an open lower layer for agent context:
memory, context capsules, rules, skills, tools, identity, capabilities, audit,
and a memory loop. The CLI is `acs`, the Agent Context Shell.

OACS is not a replacement for MCP. MCP describes tool/server interoperability.
OACS describes how an agent assembles and governs context before a model or MCP
tool is used.

### Standard Draft vs Reference Implementation

- **OACS v0.1 draft spec:** the terminology, lifecycle, capsule format,
  security model, and JSON contracts documented in `docs/` and `schemas/`.
- **Python reference implementation:** the local `oacs` package, `acs` CLI,
  FastAPI API, SQLite backend, encryption layer, registries, memory loop, and
  benchmark runner.

The draft can change before v1.0. See `docs/COMPATIBILITY.md` for what counts
as a breaking change.

### Quickstart: local deterministic proof

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,crypto]"

acs init --db ./.oacs/oacs.db
ACS_PASSPHRASE="<choose-a-local-dev-passphrase>"
acs key init --passphrase "$ACS_PASSPHRASE"
acs actor create --type human --name "User" --json
acs actor create --type agent --name "GemmaLocalAgent" --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "In project Alpha reports are generated with make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha report" --scope project --json

CAPSULE_ID=$(acs context build --intent answer_project_question \
  --scope project --budget 4000 --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs context explain "$CAPSULE_ID" --json
```

This proves the basic OACS path: explicit memory proposal, explicit commit,
retrieval, capsule build, and capsule explanation.

### Quickstart: benchmark proof

```bash
acs benchmark generate --suite memory_critical --count 20 --json

acs benchmark run --mode baseline_no_memory --model gemma-4-e2b --json
acs benchmark run --mode oacs_memory_loop --model gemma-4-e2b --json
acs benchmark compare --json
```

Expected shape:

```json
{
  "baseline_average": 1.0,
  "oacs_average": 5.0,
  "improvement": 4.0
}
```

Exact scores can vary as the benchmark evolves, but `oacs_memory_loop` should
outperform `baseline_no_memory` on memory-critical tasks.

### Quickstart: encryption check

```bash
SECRET_ID=$(acs memory propose --type fact --depth 2 --scope project \
  --text "sensitive-memory-plaintext-proof" --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$SECRET_ID" --json

if grep -a "sensitive-memory-plaintext-proof" ./.oacs/oacs.db; then
  echo "FAIL: plaintext found"
else
  echo "PASS: plaintext absent from SQLite"
fi
```

### LM Studio

Start LM Studio with an OpenAI-compatible server at `http://localhost:1234/v1`.
The default model name is `gemma-4-e2b`, but it is configurable with
`--model` or `OACS_LMSTUDIO_MODEL`. Unit tests do not require LM Studio;
integration tests skip when the server is unavailable.

The benchmark commands above are deterministic by default. To run a real model
proof, use the `LMStudioClient` integration or the LM Studio integration test:

```bash
export OACS_LMSTUDIO_BASE_URL=http://localhost:1234/v1
export OACS_LMSTUDIO_MODEL=gemma-4-e2b
pytest -q tests/integration_test_lmstudio.py
```

The important distinction:

- `baseline_no_memory`: the model receives only the task.
- `oacs_memory_loop`: OACS retrieves memory, builds a Context Capsule, applies
  rules/capabilities, and gives the model a governed context.

### Security Model

Memory and sensitive capsule payloads are encrypted before they are written to
SQLite. The default provider is passphrase-based envelope encryption. PQC is a
key-wrapping integration point only; no fake post-quantum claims are made when
optional PQ libraries are absent.

### Limitations

This is a local POC, not a hosted multi-tenant system. MCP execution is modeled
through typed bindings and imported tool metadata. Vector search is pluggable,
with deterministic lexical search implemented by default.

## RU
OACS v0.1 draft — локальный proof-of-concept открытого нижнего слоя агентского контекста:
memory, context capsules, rules, skills, tools, identity, capabilities, audit и
memory loop. CLI называется `acs` — Agent Context Shell.

OACS не заменяет MCP. MCP описывает совместимость tools/server. OACS описывает,
как агент собирает и контролирует контекст до вызова модели или MCP tool.

### Draft стандарта и reference implementation

- **OACS v0.1 draft spec:** терминология, lifecycle, формат capsule,
  security model и JSON contracts в `docs/` и `schemas/`.
- **Python reference implementation:** локальный пакет `oacs`, CLI `acs`,
  FastAPI API, SQLite backend, encryption layer, registries, memory loop и
  benchmark runner.

До v1.0 draft может меняться. Что считается breaking change, описано в
`docs/COMPATIBILITY.md`.

### Быстрый старт: локальная детерминированная проверка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,crypto]"

acs init --db ./.oacs/oacs.db
ACS_PASSPHRASE="<choose-a-local-dev-passphrase>"
acs key init --passphrase "$ACS_PASSPHRASE"
acs actor create --type human --name "User" --json
acs actor create --type agent --name "GemmaLocalAgent" --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "В проекте Alpha отчёты генерируются через make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha отчёты" --scope project --json

CAPSULE_ID=$(acs context build --intent answer_project_question \
  --scope project --budget 4000 --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs context explain "$CAPSULE_ID" --json
```

Этот путь показывает базовую механику OACS: явное предложение памяти, явный
commit, retrieval, сборка Context Capsule и объяснение, почему контекст включён.

### Быстрый старт: проверка benchmark

```bash
acs benchmark generate --suite memory_critical --count 20 --json
acs benchmark run --mode baseline_no_memory --model gemma-4-e2b --json
acs benchmark run --mode oacs_memory_loop --model gemma-4-e2b --json
acs benchmark compare --json
```

Ожидаемая форма результата:

```json
{
  "baseline_average": 1.0,
  "oacs_average": 5.0,
  "improvement": 4.0
}
```

Точные числа могут меняться по мере развития benchmark, но
`oacs_memory_loop` должен выигрывать у `baseline_no_memory` на memory-critical
задачах.

### Быстрый старт: проверка шифрования

```bash
SECRET_ID=$(acs memory propose --type fact --depth 2 --scope project \
  --text "sensitive-memory-plaintext-proof" --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$SECRET_ID" --json

if grep -a "sensitive-memory-plaintext-proof" ./.oacs/oacs.db; then
  echo "FAIL: plaintext found"
else
  echo "PASS: plaintext absent from SQLite"
fi
```

### LM Studio

Запустите LM Studio с OpenAI-compatible server на `http://localhost:1234/v1`.
Имя модели по умолчанию `gemma-4-e2b`, но его можно поменять через `--model` или
`OACS_LMSTUDIO_MODEL`. Unit tests не требуют LM Studio; integration tests
пропускаются, если server недоступен.

Benchmark commands выше по умолчанию deterministic. Для проверки реальной
модели используйте `LMStudioClient` integration или integration test:

```bash
export OACS_LMSTUDIO_BASE_URL=http://localhost:1234/v1
export OACS_LMSTUDIO_MODEL=gemma-4-e2b
pytest -q tests/integration_test_lmstudio.py
```

Разница режимов:

- `baseline_no_memory`: модель получает только задачу.
- `oacs_memory_loop`: OACS достаёт память, строит Context Capsule, применяет
  rules/capabilities и даёт модели управляемый контекст.

### Ограничения

Это локальный POC, не hosted multi-tenant service. MCP execution представлен
typed bindings и импортированной metadata. Vector search расширяемый; по
умолчанию реализован deterministic lexical search.
