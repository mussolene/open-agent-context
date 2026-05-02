# Release Process / Процесс релиза

## EN
OACS is currently an alpha-quality reference implementation for the OACS v0.1 draft.
Prefer prerelease tags until the schemas and conformance fixtures are ready for
v1.0 compatibility guarantees.

Recommended first public release:

```bash
git tag -a v0.3.0a1 -m "OACS 0.3.0 alpha 1"
git push origin v0.3.0a1
```

Before tagging:

```bash
ruff check .
mypy oacs
pytest -q
rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
python3 -m pip install -e ".[dev,crypto,release]"
python3 -m build
python3 -m twine check dist/*
```

Installed wheel smoke:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-wheel-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

TestPyPI smoke after the release workflow succeeds:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-testpypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install \
  cryptography fastapi httpx jsonschema pydantic rich typer uvicorn
"$SMOKE_DIR/bin/python" -m pip install --no-deps \
  --index-url https://test.pypi.org/simple/ \
  oacs==0.3.0a1
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

Do not make TestPyPI the dependency source. TestPyPI can contain unrelated
packages with names that shadow production dependencies.

Publishing uses GitHub trusted publishing through `.github/workflows/release.yml`.
Configure PyPI and TestPyPI projects for the repository before publishing. Do
not store PyPI API tokens in the repository.

Release flow:

1. Push an alpha/rc tag such as `v0.3.0a1`. Alpha, beta, and release-candidate
   tags publish to TestPyPI automatically.
2. Confirm the release workflow publishes to TestPyPI.
3. Install from TestPyPI in a clean environment and run the smoke commands.
4. Promote to PyPI manually with the `Release` workflow dispatch target `pypi`
   only after TestPyPI passes.
5. Create a GitHub Release with the changelog notes.

## RU
OACS сейчас является alpha-quality reference implementation для OACS v0.1 draft.
До стабилизации schemas и conformance fixtures лучше использовать prerelease
tags.

Рекомендуемый первый публичный релиз:

```bash
git tag -a v0.3.0a1 -m "OACS 0.3.0 alpha 1"
git push origin v0.3.0a1
```

Перед tag:

```bash
ruff check .
mypy oacs
pytest -q
rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
python3 -m pip install -e ".[dev,crypto,release]"
python3 -m build
python3 -m twine check dist/*
```

Smoke test установленного wheel:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-wheel-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

Smoke test после успешной публикации в TestPyPI:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-testpypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install \
  cryptography fastapi httpx jsonschema pydantic rich typer uvicorn
"$SMOKE_DIR/bin/python" -m pip install --no-deps \
  --index-url https://test.pypi.org/simple/ \
  oacs==0.3.0a1
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

Не используйте TestPyPI как источник dependencies. На TestPyPI могут быть
посторонние packages, которые перекрывают production dependencies по имени.

Публикация использует GitHub trusted publishing через
`.github/workflows/release.yml`. До публикации нужно настроить PyPI и TestPyPI
projects для этого repository. Не храните PyPI API tokens в репозитории.

Release flow:

1. Push alpha/rc tag, например `v0.3.0a1`. Alpha, beta и release-candidate tags
   автоматически публикуются в TestPyPI.
2. Убедиться, что release workflow публикует в TestPyPI.
3. Установить пакет из TestPyPI в чистом окружении и запустить smoke commands.
4. Публиковать в PyPI вручную через `Release` workflow dispatch target `pypi`
   только после успешного TestPyPI.
5. Создать GitHub Release с changelog notes.
