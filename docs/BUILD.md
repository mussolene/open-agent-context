# Build Pipeline / Сборочная линия

## EN
The repository uses GitHub Actions in `.github/workflows/ci.yml`.

CI runs on pushes and pull requests to `main`:

- install `.[dev,crypto]`
- `ruff check .`
- `mypy oacs`
- `pytest -q`
- build sdist and wheel with `python -m build`
- upload `dist/*` as CI artifacts
- install the built wheel in a clean virtual environment
- smoke-test `acs --help`, `acs init`, and `acs key init`

Local equivalent:

```bash
python3 -m pip install -e ".[dev,crypto]"
ruff check .
mypy oacs
pytest -q
rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
python3 -m pip install build
python3 -m build
SMOKE_DIR="${TMPDIR:-.}/oacs-wheel-smoke"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
```

## RU
Репозиторий использует GitHub Actions в `.github/workflows/ci.yml`.

CI запускается на push и pull request в `main`:

- установка `.[dev,crypto]`
- `ruff check .`
- `mypy oacs`
- `pytest -q`
- сборка sdist и wheel через `python -m build`
- загрузка `dist/*` как CI artifacts
- установка wheel в чистое virtual environment
- smoke-test `acs --help`, `acs init`, `acs key init`

Локальный эквивалент:

```bash
python3 -m pip install -e ".[dev,crypto]"
ruff check .
mypy oacs
pytest -q
rm -rf dist build
find . -maxdepth 1 -name "*.egg-info" -exec rm -rf {} +
python3 -m pip install build
python3 -m build
SMOKE_DIR="${TMPDIR:-.}/oacs-wheel-smoke"
python3 -m venv "$SMOKE_DIR"
"$SMOKE_DIR/bin/python" -m pip install dist/*.whl
"$SMOKE_DIR/bin/acs" --help
```
