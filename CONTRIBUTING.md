# Contributing / Участие

## EN
OACS is an **OACS v0.1 draft** memory/context standard with a Python reference
implementation. Contributions should keep the standard small: memory records,
context capsules, capabilities, rules, skills/tools metadata, audit, and
deterministic operation traces.

Please do not turn the core into an agent framework, vector database, benchmark
harness, MCP replacement, or repository workflow system. Integration and
benchmark code belongs in adapters and examples.

Before opening a PR:

```bash
ruff check .
mypy oacs
pytest -q
python3 -m pip wheel --no-deps . -w /tmp/oacs-wheel-check
```

Publication hygiene:

- Do not commit `.env*`, local databases, SQLite WAL files, keys, certs, logs,
  caches, or generated build artifacts.
- Use placeholders in docs and examples.
- Keep docs bilingual EN/RU when they describe user-facing standard behavior.
- Update `docs/ROADMAP.md` only when the standard scope or implementation stage
  changes.

Compatibility:

- Before v1.0, schema and CLI/API breaking changes are allowed when they make
  the draft cleaner.
- Breaking changes must be named in docs and tests.
- Avoid compatibility shims unless there is an explicit migration requirement.

## RU
OACS - это **OACS v0.1 draft** стандарта memory/context с Python reference
implementation. Вклад должен сохранять стандарт небольшим: memory records,
context capsules, capabilities, rules, metadata для skills/tools, audit и
deterministic operation traces.

Не превращайте core в agent framework, vector database, benchmark harness,
замену MCP или систему workflow для репозитория. Integration и benchmark code
должны жить в adapters и examples.

Перед PR:

```bash
ruff check .
mypy oacs
pytest -q
python3 -m pip wheel --no-deps . -w /tmp/oacs-wheel-check
```

Publication hygiene:

- Не коммитьте `.env*`, локальные базы, SQLite WAL файлы, keys, certificates,
  logs, caches или generated build artifacts.
- Используйте placeholders в docs и examples.
- Для user-facing поведения стандарта держите документацию bilingual EN/RU.
- Обновляйте `docs/ROADMAP.md` только когда меняется scope стандарта или стадия
  implementation.

Compatibility:

- До v1.0 breaking changes в schemas и CLI/API допустимы, если они делают draft
  чище.
- Breaking changes должны быть явно названы в docs и tests.
- Не добавляйте compatibility shims без явного migration requirement.
