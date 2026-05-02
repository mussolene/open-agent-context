# OACS v0.1 draft - Open Agent Context Standard

## EN
OACS is an open lower-layer draft contract for agent memory and context:
`MemoryRecord`, `ContextCapsule`, `CapabilityGrant`, `EvidenceRef`, auditable
`memory_calls`, and adapter boundaries. The bundled `acs` CLI is the reference
local interface to that contract.

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

### Core Contracts

The core draft is intentionally small:

- `MemoryRecord`: lifecycle, depth, scope, encrypted content, and evidence.
- `ContextCapsule`: portable governed context for one task.
- `CapabilityGrant`: actor-scoped permission record.
- `EvidenceRef` and structured evidence items: support for memory and context decisions.
- `MemoryOperation`, `ContextOperation`, `MemoryLoopRun`, and `memory_call`:
  auditable operation envelopes.

Benchmarks, LM Studio, MCP execution, repo dogfood, and task packs are reference
adapters. They validate or exercise the contract but do not expand it.

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

Current technical reports:

- `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`
- `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md`

### Killer Demo

The local killer demo proves the public product story without a hosted service,
network access, LM Studio, or a running model. It writes one scoped memory,
builds and exports a Context Capsule, validates the export envelope, records
`memory_calls`, imports MCP metadata as an adapter boundary, verifies the audit
chain, and links the checked-in full-context benchmark comparison.

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```

Raw artifacts are written to the output directory; start with `SUMMARY.md` and
`summary.json`.

### Development Dogfood

Optional source-checkout dogfood lives in the removable
`repo_development_memory` skill under `examples/skills/`. It is not part of the
standard surface or the minimal installed-package path:

```bash
acs skill scan examples/skills --json
acs skill run repo_development_memory \
  --payload '{"action":"capture","task":"tighten memory_calls","summary":"Removed benchmark-specific shortcuts and kept selector metadata typed.","cwd":"."}' --json
acs skill run repo_development_memory \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' --json
```

The dogfood skill is a source-checkout adapter. Auto mode commits only D1 repo
episodes; D2/D3 memory remains explicit review.

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
CLI smoke checks. Public prerelease publishing uses trusted publishing and the
checklist in `docs/RELEASE.md`; see `docs/BUILD.md` for local build parity.

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
OACS - open lower-layer draft contract для агентской памяти и контекста:
`MemoryRecord`, `ContextCapsule`, `CapabilityGrant`, `EvidenceRef`, auditable
`memory_calls` и adapter boundaries. Встроенный CLI `acs` является reference
local interface к этому contract.

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

### Core Contracts

Core draft намеренно небольшой:

- `MemoryRecord`: lifecycle, depth, scope, encrypted content и evidence.
- `ContextCapsule`: переносимый управляемый контекст для одной задачи.
- `CapabilityGrant`: actor-scoped permission record.
- `EvidenceRef` и structured evidence items: поддержка memory/context decisions.
- `MemoryOperation`, `ContextOperation`, `MemoryLoopRun` и `memory_call`:
  auditable operation envelopes.

Benchmarks, LM Studio, MCP execution, repo dogfood и task packs являются
reference adapters. Они валидируют или упражняют contract, но не расширяют его.

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

Текущие technical reports:

- `examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md`
- `examples/benchmarks/full_context_gemma_e2b_2026-05-02.md`

### Killer Demo

Локальное killer demo доказывает публичный product story без hosted service,
network access, LM Studio или запущенной модели. Оно пишет одну scoped memory,
строит и экспортирует Context Capsule, валидирует export envelope, записывает
`memory_calls`, импортирует MCP metadata как adapter boundary, проверяет audit
chain и ссылается на checked-in full-context benchmark comparison.

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```

Raw artifacts пишутся в output directory; начинать стоит с `SUMMARY.md` и
`summary.json`.

### Development dogfood

Optional source-checkout dogfood живёт в отключаемом
`repo_development_memory` skill в `examples/skills/`. Это не часть standard
surface и не minimal installed-package path:

```bash
acs skill scan examples/skills --json
acs skill run repo_development_memory \
  --payload '{"action":"capture","task":"tighten memory_calls","summary":"Removed benchmark-specific shortcuts and kept selector metadata typed.","cwd":"."}' --json
acs skill run repo_development_memory \
  --payload '{"action":"context","task":"continue OACS development","cwd":"."}' --json
```

Dogfood skill является source-checkout adapter. Auto mode коммитит только D1
repo episodes; D2/D3 memory остаётся под явным review.

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
CLI smoke checks. Публичные prerelease публикации используют trusted publishing
и checklist в `docs/RELEASE.md`; локальный build parity описан в
`docs/BUILD.md`.

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
