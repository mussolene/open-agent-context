# v1.0 Release Checklist / Чеклист релиза v1.0

## EN
This checklist blocks an OACS v1.0 release. It verifies the portable standard
surface first and the Python package as one reference implementation second.

Release blockers:

- Freeze manifest drift: every checked-in schema appears in
  `docs/FREEZE_PREP.md` with exactly one status.
- Stable schema drift: every `stable_candidate` schema has a positive fixture,
  strict top-level shape, portable field descriptions, and expected negative
  coverage when it has semantic or adapter-boundary rejection rules.
- Fixture drift: `conformance/fixtures/` and `conformance/negative/` validate
  with the reference checker, and negative fixtures remain language-neutral JSON
  rejection examples rather than Python object snapshots.
- Compatibility drift: `docs/COMPATIBILITY.md` states which schemas are stable,
  which remain draft support, and which are reference-only.
- Standard boundary drift: public docs keep Python, SQLite, HTTP, MCP stdio,
  hosted APIs, benchmark harnesses, and export envelopes as reference or adapter
  behavior unless a stable schema/spec section explicitly requires them.
- Local gate failure: lint, type checks, unit tests, conformance validation,
  package build, and package metadata checks must pass from a clean checkout.
- Published package smoke failure: after publishing, a fresh environment must
  install the exact version and run `acs --version` plus
  `acs conformance validate --json`.
- Secret scan failure: release artifacts and checked-in docs, schemas,
  fixtures, tests, and package code must not contain private keys, provider
  tokens, or plaintext protected values outside intentional conformance
  sentinels.
- OACS proof gap: release evidence must include command outputs for local gate,
  published package smoke, and leak/secret scan, and a checkpoint must reference
  those evidence records.

Reference local gate for the Python package:

```bash
python3 -m ruff check .
python3 -m mypy oacs
python3 -m pytest -q
python3 -m oacs.cli.main conformance validate --json
python3 -m build
python3 -m twine check dist/*
rg -n '(-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,})' docs conformance tests schemas oacs README.md CHANGELOG.md pyproject.toml
```

Reference published-package smoke:

```bash
python3 -m venv /tmp/oacs-v1-smoke
/tmp/oacs-v1-smoke/bin/python -m pip install --upgrade pip
/tmp/oacs-v1-smoke/bin/python -m pip install oacs==<version>
/tmp/oacs-v1-smoke/bin/acs --version
/tmp/oacs-v1-smoke/bin/acs conformance validate --json
```

## RU
Этот checklist блокирует релиз OACS v1.0. Сначала он проверяет portable
standard surface, а Python package рассматривает как одну reference
implementation.

Release blockers:

- Freeze manifest drift: каждая checked-in schema указана в
  `docs/FREEZE_PREP.md` ровно с одним status.
- Stable schema drift: каждая `stable_candidate` schema имеет positive fixture,
  strict top-level shape, portable field descriptions и expected negative
  coverage, если у неё есть semantic или adapter-boundary rejection rules.
- Fixture drift: `conformance/fixtures/` и `conformance/negative/` проходят
  reference checker, а negative fixtures остаются language-neutral JSON
  rejection examples, не Python object snapshots.
- Compatibility drift: `docs/COMPATIBILITY.md` фиксирует, какие schemas stable,
  какие остаются draft support и какие reference-only.
- Standard boundary drift: public docs оставляют Python, SQLite, HTTP, MCP
  stdio, hosted APIs, benchmark harnesses и export envelopes reference или
  adapter behavior, если stable schema/spec section явно не требует их.
- Local gate failure: lint, type checks, unit tests, conformance validation,
  package build и package metadata checks проходят из clean checkout.
- Published package smoke failure: после публикации fresh environment
  устанавливает точную version и запускает `acs --version` плюс
  `acs conformance validate --json`.
- Secret scan failure: release artifacts и checked-in docs, schemas, fixtures,
  tests и package code не содержат private keys, provider tokens или plaintext
  protected values вне intentional conformance sentinels.
- OACS proof gap: release evidence включает command outputs для local gate,
  published package smoke и leak/secret scan, а checkpoint ссылается на эти
  evidence records.

Reference local gate для Python package:

```bash
python3 -m ruff check .
python3 -m mypy oacs
python3 -m pytest -q
python3 -m oacs.cli.main conformance validate --json
python3 -m build
python3 -m twine check dist/*
rg -n '(-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{20,})' docs conformance tests schemas oacs README.md CHANGELOG.md pyproject.toml
```

Reference published-package smoke:

```bash
python3 -m venv /tmp/oacs-v1-smoke
/tmp/oacs-v1-smoke/bin/python -m pip install --upgrade pip
/tmp/oacs-v1-smoke/bin/python -m pip install oacs==<version>
/tmp/oacs-v1-smoke/bin/acs --version
/tmp/oacs-v1-smoke/bin/acs conformance validate --json
```
