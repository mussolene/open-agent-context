# Release Process / Процесс релиза

## EN
OACS uses SemVer as the human release policy and PEP 440 spelling for Python
packages. The Git tag is the release trigger.

### Version Policy

- Stable release: SemVer `0.4.0`, PyPI version `0.4.0`, tag `v0.4.0`.
- Alpha release: SemVer `0.4.0-alpha.1`, PyPI version `0.4.0a1`, tag
  `v0.4.0a1`.
- Beta release: SemVer `0.4.0-beta.1`, PyPI version `0.4.0b1`, tag
  `v0.4.0b1`.
- Release candidate: SemVer `0.4.0-rc.1`, PyPI version `0.4.0rc1`, tag
  `v0.4.0rc1`.

Prerelease tags publish to TestPyPI. Stable tags publish to PyPI. Manual
workflow dispatch remains available for recovery/debugging and for explicitly
publishing a prerelease package to PyPI after TestPyPI smoke checks pass, but
the normal path is tag-driven.

### Normal Release

1. Update `pyproject.toml`, `oacs/__init__.py`, and `CHANGELOG.md`.
2. Run the local gate:

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

3. Smoke-test the local wheel:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-wheel-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

4. Commit the release changes.
5. Create and push the tag:

```bash
VERSION="$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
TAG="v${VERSION}"
git tag -a "$TAG" -m "OACS ${VERSION}"
git push origin main
git push origin "$TAG"
```

6. Watch `.github/workflows/release.yml`.
7. Confirm the workflow created or refreshed the GitHub Release entry for the
   tag. Stable releases use GitHub Releases plus PyPI publication; prerelease
   tags publish packages according to the target index policy.
8. Smoke-test the published package.

For TestPyPI prereleases:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-testpypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install \
  cryptography fastapi httpx jsonschema pydantic rich typer uvicorn
"$SMOKE_DIR/bin/python" -m pip install --no-cache-dir --no-deps \
  --index-url https://test.pypi.org/simple/ \
  "oacs==${VERSION}"
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

For stable PyPI releases:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-pypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install --no-cache-dir "oacs==${VERSION}"
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

For an approved PyPI alpha, rerun the release workflow with
`workflow_dispatch.target=pypi` for the same checked version after the TestPyPI
smoke test passes.

Do not make TestPyPI the dependency source. TestPyPI can contain unrelated
packages that shadow production dependencies.

Publishing uses GitHub trusted publishing through `.github/workflows/release.yml`.
Configure PyPI and TestPyPI projects for this repository before publishing. Do
not store PyPI API tokens in the repository.

### Release Automation Maintenance

Keep release automation free of deprecated action runtimes. The workflow builds
distributions inside the selected trusted-publishing job instead of passing
artifacts between jobs, so it does not depend on `actions/upload-artifact` or
`actions/download-artifact` while those actions use a deprecated Node.js
runtime. If artifact handoff returns, verify the referenced action versions use
the current GitHub Actions runtime before cutting a release.

## RU
OACS использует SemVer как человеческую release policy и PEP 440 spelling для
Python packages. Git tag является release trigger.

### Version Policy

- Stable release: SemVer `0.4.0`, PyPI version `0.4.0`, tag `v0.4.0`.
- Alpha release: SemVer `0.4.0-alpha.1`, PyPI version `0.4.0a1`, tag
  `v0.4.0a1`.
- Beta release: SemVer `0.4.0-beta.1`, PyPI version `0.4.0b1`, tag
  `v0.4.0b1`.
- Release candidate: SemVer `0.4.0-rc.1`, PyPI version `0.4.0rc1`, tag
  `v0.4.0rc1`.

Prerelease tags публикуются в TestPyPI. Stable tags публикуются в PyPI. Manual
workflow dispatch остаётся для recovery/debugging и для явной публикации
prerelease package в PyPI после успешного TestPyPI smoke check, но обычный путь
остаётся tag-driven.

### Обычный релиз

1. Обновить `pyproject.toml`, `oacs/__init__.py` и `CHANGELOG.md`.
2. Запустить локальный gate:

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

3. Smoke-test локального wheel:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-wheel-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

4. Закоммитить release changes.
5. Создать и отправить tag:

```bash
VERSION="$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"
TAG="v${VERSION}"
git tag -a "$TAG" -m "OACS ${VERSION}"
git push origin main
git push origin "$TAG"
```

6. Проверить `.github/workflows/release.yml`.
7. Подтвердить, что workflow создал или обновил GitHub Release entry для tag.
   Stable releases используют GitHub Releases вместе с PyPI publication;
   prerelease tags публикуют packages согласно target index policy.
8. Smoke-test опубликованного package.

Для TestPyPI prereleases:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-testpypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install \
  cryptography fastapi httpx jsonschema pydantic rich typer uvicorn
"$SMOKE_DIR/bin/python" -m pip install --no-cache-dir --no-deps \
  --index-url https://test.pypi.org/simple/ \
  "oacs==${VERSION}"
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

Для stable PyPI releases:

```bash
SMOKE_DIR="${TMPDIR:-/tmp}/oacs-pypi-smoke"
rm -rf "$SMOKE_DIR"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install --no-cache-dir "oacs==${VERSION}"
"$SMOKE_DIR/bin/acs" --help
"$SMOKE_DIR/bin/acs" init --db "$SMOKE_DIR/oacs.db" --json
"$SMOKE_DIR/bin/acs" key init --db "$SMOKE_DIR/oacs.db" --passphrase smoke-pass --json
```

Для одобренной PyPI alpha повторно запустите release workflow с
`workflow_dispatch.target=pypi` для той же checked version после успешного
TestPyPI smoke test.

Не используйте TestPyPI как dependency source. На TestPyPI могут быть
посторонние packages, которые перекрывают production dependencies по имени.

Публикация использует GitHub trusted publishing через
`.github/workflows/release.yml`. До публикации нужно настроить PyPI и TestPyPI
projects для этого repository. Не храните PyPI API tokens в репозитории.

### Release Automation Maintenance

Release automation не должна зависеть от deprecated action runtimes. Workflow
собирает distributions внутри selected trusted-publishing job вместо передачи
artifacts между jobs, поэтому он не зависит от `actions/upload-artifact` или
`actions/download-artifact`, пока эти actions используют deprecated Node.js
runtime. Если artifact handoff вернётся, перед релизом нужно проверить, что
referenced action versions используют текущий GitHub Actions runtime.
