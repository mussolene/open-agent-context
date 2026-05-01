# OACS v0.1 draft - Open Agent Context Standard

## EN
OACS is a local proof-of-concept for an open lower layer for agent context:
memory, context capsules, rules, skills, tools, identity, capabilities, audit,
and a memory loop. The CLI is `acs`, the Agent Context Shell.

OACS is not a replacement for MCP. MCP describes tool/server interoperability.
OACS describes how an agent assembles and governs context before a model or MCP
tool is used.

It is also not an agent framework, model backend, vector database, or benchmark
harness. Those systems can sit above or beside OACS and call its memory,
context, capability, and audit operations.

### Standard Draft vs Reference Implementation

- **OACS v0.1 draft spec:** terminology, lifecycle, capsule format, security
  model, and JSON contracts in `docs/` and `schemas/`.
- **Python reference implementation:** local `oacs` package, `acs` CLI, FastAPI
  API, SQLite backend, encryption layer, registries, memory loop, and validation
  adapters.
  Storage goes through a thin `StorageBackend` protocol; SQLite is the bundled
  reference backend.

The draft can change before v1.0. See `docs/COMPATIBILITY.md` for breaking
change policy.

### Quickstart

This path reaches the first useful OACS result: commit a memory, retrieve it,
and build an explainable Context Capsule.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,crypto]"

export OACS_DB=./.oacs/oacs.db
export OACS_PASSPHRASE="<choose-a-local-dev-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs actor create --type human --name "User" --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "In project Alpha reports are generated with make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha report" --scope project --json
acs context build --intent answer_project_question --scope project --budget 4000 --json
```

Expected result: `memory query` returns the committed procedure and
`context build` returns a `ctx_...` capsule with that memory included.

### Validation Adapters

```bash
acs benchmark generate --suite memory_critical --count 20 --json
acs benchmark run --mode baseline_no_memory --json
acs benchmark run --mode oacs_memory_call_loop --json
acs benchmark compare --json
```

Benchmarks are validation fixtures for the memory/context contract, not the
purpose of OACS. `oacs_memory_call_loop` records deterministic OACS
`memory_calls` such as `memory.query` and `memory.extract_evidence`; benchmark
scoring stays in the benchmark adapter. Task pack import/download is schema and
checksum validated; downloads require explicit `--allow-network`.

Current technical report:
`examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### Development Dogfood

Optional local dogfood uses generic OACS memory/context operations for this
repository. It is not part of the standard surface:

```bash
acs repo capture --task "tighten memory_calls" \
  --summary "Removed benchmark-specific shortcuts and kept selector metadata typed." --json

acs repo context --task "continue OACS development" --json
```

`repo capture` stores a committed D1 episode. `repo context` builds an
explainable capsule over the repo scope.

### LM Studio

Start LM Studio with an OpenAI-compatible server at `http://localhost:1234/v1`.
The model name is configurable:

```bash
export OACS_LMSTUDIO_BASE_URL=http://localhost:1234/v1
export OACS_LMSTUDIO_MODEL=gemma-4-e2b
acs benchmark run --mode oacs_memory_call_loop --provider lmstudio --model "$OACS_LMSTUDIO_MODEL" --json
```

Unit tests do not require LM Studio; integration tests skip when the server is
unavailable.

### Build Pipeline

GitHub Actions runs lint, typecheck, tests, package build, wheel install, and
CLI smoke checks. See `docs/BUILD.md`.

### Security Model

Memory and sensitive capsule payloads are encrypted before they are written to
SQLite. The default provider is passphrase-based envelope encryption. PQC is a
key-wrapping integration point only; no fake post-quantum claims are made when
optional PQ libraries are absent.

### Limitations

This is a local POC, not a hosted multi-tenant system. MCP execution is modeled
through typed bindings and imported tool metadata, with optional stdio execution
guarded by `tool.call` capabilities. Retrieval is pluggable, but deterministic
lexical/structured retrieval is the baseline. Embeddings are optional adapters,
not a core requirement. Tiny tasks can show OACS overhead; medium and long
memory tasks are the current strength.

## RU
OACS - локальный proof-of-concept открытого нижнего слоя агентского контекста:
memory, context capsules, rules, skills, tools, identity, capabilities, audit и
memory loop. CLI называется `acs` - Agent Context Shell.

OACS не заменяет MCP. MCP описывает совместимость tools/server. OACS описывает,
как агент собирает и контролирует контекст до вызова модели или MCP tool.

Также это не agent framework, model backend, vector database или benchmark
harness. Такие системы могут находиться выше или рядом с OACS и вызывать его
memory, context, capability и audit operations.

### Draft стандарта и reference implementation

- **OACS v0.1 draft spec:** терминология, lifecycle, формат capsule, security
  model и JSON contracts в `docs/` и `schemas/`.
- **Python reference implementation:** локальный пакет `oacs`, CLI `acs`,
  FastAPI API, SQLite backend, encryption layer, registries, memory loop и
  validation adapters.
  Storage идёт через тонкий `StorageBackend` protocol; SQLite является
  bundled reference backend.

До v1.0 draft может меняться. Compatibility policy описана в
`docs/COMPATIBILITY.md`.

### Quickstart

Этот путь даёт первый полезный результат OACS: записать memory, найти её и
построить explainable Context Capsule.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,crypto]"

export OACS_DB=./.oacs/oacs.db
export OACS_PASSPHRASE="<choose-a-local-dev-passphrase>"

acs init --json
acs key init --passphrase "$OACS_PASSPHRASE" --json
acs actor create --type human --name "User" --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "В проекте Alpha отчёты генерируются через make report-safe." --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha отчёты" --scope project --json
acs context build --intent answer_project_question --scope project --budget 4000 --json
```

Ожидаемый результат: `memory query` возвращает committed procedure, а
`context build` возвращает capsule `ctx_...` с этой memory внутри.

### Validation adapters

```bash
acs benchmark generate --suite memory_critical --count 20 --json
acs benchmark run --mode baseline_no_memory --json
acs benchmark run --mode oacs_memory_call_loop --json
acs benchmark compare --json
```

Benchmarks - это validation fixtures для memory/context contract, а не цель
OACS. `oacs_memory_call_loop` записывает deterministic OACS `memory_calls`,
например `memory.query` и `memory.extract_evidence`; scoring остаётся в
benchmark adapter. Import/download task packs валидируется по schema и
checksum; downloads требуют явный `--allow-network`.

Текущий technical report:
`examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`.

### Development dogfood

Optional local dogfood использует generic OACS memory/context operations для
этого репозитория. Это не часть standard surface:

```bash
acs repo capture --task "tighten memory_calls" \
  --summary "Removed benchmark-specific shortcuts and kept selector metadata typed." --json

acs repo context --task "continue OACS development" --json
```

`repo capture` сохраняет committed D1 episode. `repo context` строит explainable
capsule по repo scope.

### LM Studio

Запустите LM Studio с OpenAI-compatible server на `http://localhost:1234/v1`.
Модель настраивается:

```bash
export OACS_LMSTUDIO_BASE_URL=http://localhost:1234/v1
export OACS_LMSTUDIO_MODEL=gemma-4-e2b
acs benchmark run --mode oacs_memory_call_loop --provider lmstudio --model "$OACS_LMSTUDIO_MODEL" --json
```

Unit tests не требуют LM Studio; integration tests пропускаются, если server
недоступен.

### Сборочная линия

GitHub Actions запускает lint, typecheck, tests, package build, wheel install и
CLI smoke checks. См. `docs/BUILD.md`.

### Security model

Memory и sensitive capsule payloads шифруются до записи в SQLite. Default
provider использует passphrase-based envelope encryption. PQC - только
integration point для key wrapping; если optional PQ libraries отсутствуют,
проект не делает fake post-quantum claims.

### Ограничения

Это локальный POC, не hosted multi-tenant service. MCP execution представлен
typed bindings и импортированной metadata, а optional stdio execution защищён
`tool.call` capabilities. Retrieval расширяемый, но baseline - deterministic
lexical/structured retrieval. Embeddings являются optional adapters, а не core
requirement. Tiny tasks могут показывать OACS overhead; medium и long memory
tasks сейчас являются сильной стороной.
