# Contributing / Участие в разработке

[Project overview / О проекте](README.md) | [Documentation / Документация](docs/README.md)

## EN

OACS v1.0 is a memory and context standard with a Python reference
implementation. Keep portable contracts small. Integration, model execution,
repository workflows, and benchmarks belong in adapters or examples.

### Development setup

Use Python 3.11 or later. CI tests Python 3.11 and 3.12.

```bash
git clone https://github.com/mussolene/open-agent-context.git
cd open-agent-context
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,crypto,release]"
```

The project also includes `uv.lock` for reproducible development:
`uv sync --extra dev --extra crypto --extra release --locked`.
Choose one installation method for the environment. See [Build](docs/BUILD.md)
for package checks. Core tests do not require a model server or API credentials.

### Before opening a pull request

```bash
python -m ruff check .
python -m mypy oacs
python -m pytest -q
acs conformance validate --json
```

Explain the change, its reason, and how you verified it. Extend existing tests
for changed behavior. Run the [package checks](docs/BUILD.md) when changing
packaging or public documentation. Do not bump the package version for routine
changes; record user-visible changes under `Unreleased` in [CHANGELOG](CHANGELOG.md).

### Repository map

| Path | Responsibility |
| --- | --- |
| `oacs/` | Python reference runtime, CLI, API, storage, and adapters |
| `schemas/` | JSON contracts |
| `conformance/` | Portable positive and negative fixtures |
| `docs/` | Standard, implementation, and maintenance guides |
| `tests/` | Runtime, contract, documentation, and package checks |
| `examples/` | Demonstrations, consumer packs, skills, and measured reports |
| `benchmarks/`, `benchmark_results/` | Benchmark definitions and checked-in results |
| `.github/workflows/` | CI and release publishing |

### Compatibility and documentation

Follow the [v1.0 compatibility policy](docs/COMPATIBILITY.md). Do not assume
that breaking changes are allowed because an earlier release was a draft.
Name compatibility changes in documentation and tests. Do not add fallback
implementations or compatibility shims without an explicit requirement.

Keep user-facing standard documentation bilingual in English and Russian.
Link new guides from the [documentation index](docs/README.md). Update the
[roadmap](docs/ROADMAP.md) only when scope or implementation stage changes.

For substantial agent-assisted work, follow [AGENTS.md](AGENTS.md) and
[Dogfood](docs/DOGFOOD.md): define acceptance criteria, build OACS context,
record command evidence, verify changes and leaks, and save a checkpoint.
Do not create a parallel task-artifact directory.

### Publication hygiene

Do not commit local databases, keys, credentials, logs, caches, or generated
build output. `.env.example` contains placeholders and may be tracked; actual
`.env` files must stay private. Use synthetic values in examples and fixtures.
Review the diff and run a leak/secret check before publishing. See
[Security](docs/SECURITY.md) and [Release](docs/RELEASE.md).

## RU

OACS v1.0 является стандартом памяти и контекста с эталонной реализацией на
Python. Сохраняйте переносимые контракты небольшими. Интеграции, вызовы моделей,
работа с репозиторием и измерения относятся к адаптерам или примерам.

### Подготовка окружения

Нужен Python 3.11 или новее. CI проверяет Python 3.11 и 3.12.

```bash
git clone https://github.com/mussolene/open-agent-context.git
cd open-agent-context
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,crypto,release]"
```

Для воспроизводимой установки также есть `uv.lock`:
`uv sync --extra dev --extra crypto --extra release --locked`.
Выберите один способ установки для окружения. Проверки пакета описаны в
[руководстве по сборке](docs/BUILD.md). Основные тесты не требуют сервера модели
или ключей API.

### Перед запросом на включение изменений

```bash
python -m ruff check .
python -m mypy oacs
python -m pytest -q
acs conformance validate --json
```

Опишите, что изменилось, зачем и как это проверено. Дополняйте существующие
тесты для изменённого поведения. При изменении упаковки или публичной
документации выполните [проверки пакета](docs/BUILD.md). Не меняйте версию пакета
для обычных правок; значимые для пользователя изменения запишите в раздел
`Unreleased` файла [CHANGELOG](CHANGELOG.md).

### Структура репозитория

| Путь | Назначение |
| --- | --- |
| `oacs/` | Реализация на Python: CLI, API, хранилище и адаптеры |
| `schemas/` | Контракты JSON |
| `conformance/` | Переносимые примеры допустимых и недопустимых данных |
| `docs/` | Стандарт, реализация и сопровождение |
| `tests/` | Проверки поведения, контрактов, документации и пакета |
| `examples/` | Демонстрации, пакеты интеграции, навыки и отчёты |
| `benchmarks/`, `benchmark_results/` | Описания измерений и сохранённые результаты |
| `.github/workflows/` | CI и публикация релизов |

### Совместимость и документация

Следуйте [политике совместимости v1.0](docs/COMPATIBILITY.md). Статус ранних
черновиков не разрешает несовместимые изменения сейчас. Отражайте изменения
совместимости в документации и тестах. Не добавляйте запасные реализации или
слои совместимости без явного требования.

Пользовательская документация стандарта должна быть на английском и русском.
Добавляйте ссылки на новые руководства в [оглавление](docs/README.md).
Обновляйте [дорожную карту](docs/ROADMAP.md), только когда меняется объём
стандарта или стадия реализации.

При существенной работе с агентом следуйте [AGENTS.md](AGENTS.md) и
[руководству Dogfood](docs/DOGFOOD.md): задайте критерии готовности, соберите
контекст OACS, запишите результаты команд, проверьте изменения и утечки,
сохраните контрольную точку. Не создавайте параллельный каталог артефактов задач.

### Подготовка к публикации

Не включайте в коммиты локальные базы, ключи, учётные данные, журналы, кеши и
результаты сборки. `.env.example` содержит заглушки и может храниться в Git;
настоящие файлы `.env` должны оставаться приватными. Используйте вымышленные
значения в примерах и тестовых данных. Перед публикацией просмотрите изменения
и проверьте утечки. См. [безопасность](docs/SECURITY.md) и [релизы](docs/RELEASE.md).
