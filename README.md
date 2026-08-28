# OACS: Open Agent Context Standard

[![CI](https://github.com/mussolene/open-agent-context/actions/workflows/ci.yml/badge.svg)](https://github.com/mussolene/open-agent-context/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/oacs)](https://pypi.org/project/oacs/)
[![Python](https://img.shields.io/pypi/pyversions/oacs)](https://pypi.org/project/oacs/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Portable, governed memory and context for AI agents.**

[English](#en) | [Русский](#ru) | [Documentation / Документация](docs/README.md) | [Changelog](CHANGELOG.md)

## EN

OACS defines how agents store memory, retrieve evidence, and assemble context
with explicit permissions and an audit trail. This repository contains the
**OACS v1.0 standard** and its **Python reference implementation**: the `oacs`
package and `acs` CLI, backed by SQLite with a FastAPI interface.

Use it to preserve project knowledge between sessions, build explainable
context capsules, and attach tool results as evidence. OACS complements MCP:
MCP connects tools and servers; OACS governs the memory and context an agent
uses around those calls. It is not an agent framework, model provider, or vault.

### Standard vs Reference Implementation

| Layer | What lives here |
| --- | --- |
| Portable standard | Memory lifecycle, context capsules, capability grants, evidence, audit semantics, and [JSON schemas](schemas/). |
| Python reference implementation | CLI, HTTP API, SQLite storage, encryption, lexical retrieval, and context prompt rendering. |
| Adapters and examples | Tools, skills, MCP bindings, repository workflows, and benchmark fixtures. These do not expand the standard. |

Start with the [specification](docs/SPEC.md) and
[compatibility policy](docs/COMPATIBILITY.md) when implementing OACS in another
runtime. The standard version and Python package release version are separate;
see [releases](https://github.com/mussolene/open-agent-context/releases) for
package changes.

### Quickstart

Requires Python 3.11 or later. No model server or API key is needed.
The commands below use a POSIX shell; on Windows, activate the virtual
environment and set environment variables using your shell's syntax.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install oacs

export OACS_DB=./.oacs/oacs.db
acs init --json
acs key init --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "In project Alpha reports are generated with make report-safe." --json \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha report" --scope project --json
acs context build --intent answer_project_question --query "Alpha report" \
  --scope project --budget 4000 --json
```

Expected result: the query finds the committed procedure, and the `ctx_...`
capsule includes its memory reference. `--intent` describes the task category;
`--query` supplies retrieval text. The reference budget limits selected memory
lines, not the total tokens of a later model request.

For an exact package version and more detail, use the
[PyPI quickstart](docs/QUICKSTART_PYPI.md). For editable installation and checks,
see [Contributing](CONTRIBUTING.md).

### Core concepts

- **MemoryRecord**: scoped memory with lifecycle, depth, encrypted content, and
  evidence. D0-D2 records and D3-D5 hypotheses have different evidence rules.
- **ContextCapsule**: portable context selected for a task, with permissions,
  evidence references, and forbidden assumptions.
- **CapabilityGrant**: actor permissions constrained by operation, scope,
  namespace, and memory depth.
- **EvidenceRef**: provenance for observations and decisions. Tool results
  enter capsule evidence through included memories that reference them.
- **ProtectedRef**: a reference to an external secret or protected value;
  plaintext and vault state remain outside OACS.
- **memory_calls**: auditable memory operation traces, not final model answers.

### Try the local demo

From a [source checkout](CONTRIBUTING.md#development-setup):

```bash
python examples/killer_demo/run_demo.py --out .oacs/killer-demo
```

The demo writes a memory, builds and exports a capsule, checks the export,
records memory operations, imports MCP metadata, and verifies the audit chain.
It runs offline without LM Studio or a model. Read the generated `SUMMARY.md`
and `summary.json`; see the [demo guide](examples/killer_demo/README.md).

### Documentation

| Goal | Guide |
| --- | --- |
| Understand memory and context | [Memory model](docs/MEMORY_MODEL.md), [capsules](docs/CONTEXT_CAPSULES.md), [memory loop](docs/MEMORY_LOOP.md) |
| Pass context to a model | [Context prompting](docs/CONTEXT_PROMPTING.md) |
| Integrate tools and services | [API](docs/API.md), [tools](docs/TOOL_BINDINGS.md), [MCP](docs/MCP_BINDINGS.md), [skills](docs/SKILLS.md) |
| Use OACS during repository work | [Agent workflow](docs/AGENT_WORKFLOW.md), [consumer packs](docs/CONSUMER_PACKS.md), [dogfood](docs/DOGFOOD.md) |
| Evaluate the implementation | [Conformance](conformance/README.md), [benchmarks](docs/BENCHMARK.md) |
| Develop or release | [Contributing](CONTRIBUTING.md), [build](docs/BUILD.md), [release](docs/RELEASE.md), [roadmap](docs/ROADMAP.md) |

The [documentation index](docs/README.md) covers all guides and reference material.

### Security and limits

Memory and sensitive capsule payloads are encrypted at rest. The default local
key provider, `local_unlocked`, stores key material beside the local database;
encryption does not protect against someone who can read both. Keep `.oacs/`
private and out of version control. Passphrase wrapping is available.

Local setup uses development bootstrap permissions. Use
`OACS_POLICY_MODE=strict` with explicit grants when bootstrap access is not
appropriate. Read [Security](docs/SECURITY.md) and the
[external vault boundary](docs/VAULT.md) before handling sensitive data.

This is a local reference implementation, not a hosted multi-tenant service.
Retrieval is deterministic and lexical by default; embeddings and model
execution are optional adapters. Benchmark results describe specific fixtures
and models, not a general performance guarantee. Post-quantum key wrapping is
an optional integration, not a default security claim.

## RU

OACS определяет, как агенты сохраняют память, находят подтверждающие данные и
собирают контекст с явными разрешениями и журналом аудита. Репозиторий содержит
**стандарт OACS v1.0** и **эталонную реализацию на Python**: пакет `oacs`, CLI
`acs`, хранилище SQLite и интерфейс FastAPI.

OACS помогает сохранять знания о проекте между сессиями, объяснять состав
контекста и связывать результаты инструментов с доказательствами. MCP отвечает
за связь инструментов и серверов, OACS управляет памятью и контекстом вокруг
этих вызовов. Это не агентский фреймворк, поставщик моделей или хранилище секретов.

### Стандарт и эталонная реализация

| Уровень | Содержимое |
| --- | --- |
| Переносимый стандарт | Жизненный цикл памяти, капсулы контекста, разрешения, доказательства, семантика аудита и [схемы JSON](schemas/). |
| Реализация на Python | CLI, HTTP API, SQLite, шифрование, лексический поиск и подготовка контекста для модели. |
| Адаптеры и примеры | Инструменты, навыки, привязки MCP, работа с репозиторием и тестовые наборы. Они не расширяют стандарт. |

Для реализации OACS в другой среде начните со
[спецификации](docs/SPEC.md) и [политики совместимости](docs/COMPATIBILITY.md).
Версия стандарта и версия пакета Python различаются; изменения пакета указаны
в [релизах](https://github.com/mussolene/open-agent-context/releases).

### Быстрый старт

Нужен Python 3.11 или новее. Сервер модели и ключ API не требуются.
Команды рассчитаны на POSIX shell. В Windows используйте синтаксис своей
оболочки для активации окружения и переменных среды.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install oacs

export OACS_DB=./.oacs/oacs.db
acs init --json
acs key init --json

CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "В проекте Alpha отчёты генерируются через make report-safe." --json \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha отчёты" --scope project --json
acs context build --intent answer_project_question --query "Alpha отчёты" \
  --scope project --budget 4000 --json
```

Запрос должен найти сохранённую процедуру, а капсула `ctx_...` включить ссылку
на неё. `--intent` задаёт категорию задачи, `--query` передаёт текст поиска.
Бюджет ограничивает выбранные строки памяти, а не весь будущий запрос к модели.

Установка конкретной версии описана в [руководстве PyPI](docs/QUICKSTART_PYPI.md).
Установка из исходников и проверки: [участие в разработке](CONTRIBUTING.md).

### Основные понятия

- **MemoryRecord**: память с областью действия, жизненным циклом, глубиной,
  зашифрованным содержимым и доказательствами. Для D0-D2 и гипотез D3-D5
  действуют разные правила использования доказательств.
- **ContextCapsule**: контекст задачи с разрешениями, ссылками на доказательства
  и запрещёнными предположениями.
- **CapabilityGrant**: разрешения участника по операциям, области действия,
  пространству имён и глубине памяти.
- **EvidenceRef**: происхождение наблюдений и решений. Результаты инструментов
  попадают в доказательства капсулы через включённые записи памяти со ссылками
  на эти результаты.
- **ProtectedRef**: ссылка на внешний секрет или защищённое значение без
  переноса открытого содержимого и состояния хранилища в OACS.
- **memory_calls**: журнал операций с памятью, а не готовые ответы модели.

### Локальная демонстрация

После [установки из исходников](CONTRIBUTING.md):

```bash
python examples/killer_demo/run_demo.py --out .oacs/killer-demo
```

Пример сохраняет память, собирает и экспортирует капсулу, проверяет экспорт,
записывает операции памяти, импортирует метаданные MCP и проверяет цепочку
аудита. Он работает без сети, LM Studio и модели. Результат находится в
`SUMMARY.md` и `summary.json`; подробнее в [руководстве](examples/killer_demo/README.md).

### Документация

| Задача | Руководство |
| --- | --- |
| Разобраться в памяти и контексте | [Модель памяти](docs/MEMORY_MODEL.md), [капсулы](docs/CONTEXT_CAPSULES.md), [цикл памяти](docs/MEMORY_LOOP.md) |
| Передать контекст модели | [Подготовка контекста](docs/CONTEXT_PROMPTING.md) |
| Подключить инструменты и сервисы | [API](docs/API.md), [инструменты](docs/TOOL_BINDINGS.md), [MCP](docs/MCP_BINDINGS.md), [навыки](docs/SKILLS.md) |
| Применить OACS в репозитории | [Работа агента](docs/AGENT_WORKFLOW.md), [пакеты интеграции](docs/CONSUMER_PACKS.md), [проверка на собственном проекте](docs/DOGFOOD.md) |
| Проверить реализацию | [Соответствие стандарту](conformance/README.md), [измерения](docs/BENCHMARK.md) |
| Разрабатывать и выпускать версии | [Участие](CONTRIBUTING.md), [сборка](docs/BUILD.md), [релиз](docs/RELEASE.md), [планы](docs/ROADMAP.md) |

Полный список руководств: [оглавление документации](docs/README.md).

### Безопасность и ограничения

Память и чувствительные данные капсул шифруются перед сохранением. Локальный
поставщик ключей `local_unlocked` по умолчанию хранит ключ рядом с базой:
шифрование не защищает от того, кто может прочитать оба файла. Не публикуйте
`.oacs/` и ограничьте доступ к этому каталогу. Доступна защита ключа парольной
фразой.

Локальный запуск использует начальные разрешения режима разработки. Если они
не подходят, используйте `OACS_POLICY_MODE=strict` и явные разрешения.
Перед работой с чувствительными данными прочитайте
[модель безопасности](docs/SECURITY.md) и
[границу внешнего хранилища секретов](docs/VAULT.md).

Это локальная эталонная реализация, не сервис для нескольких клиентов.
Поиск по умолчанию лексический и детерминированный; векторный поиск и вызовы
моделей относятся к необязательным адаптерам. Результаты измерений относятся к
конкретным наборам и моделям и не гарантируют общего ускорения. Постквантовая
защита ключей доступна как необязательная интеграция, не как свойство по умолчанию.

## License / Лицензия

[Apache License 2.0](LICENSE).
