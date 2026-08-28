# Build and Verification / Сборка и проверки

[Documentation / Документация](README.md)

## EN

[GitHub Actions CI](../.github/workflows/ci.yml) runs on pushes and pull requests
to `main`. The quality job installs `.[dev,crypto]` and runs Ruff, Mypy, and
Pytest on Python 3.11 and 3.12. After it passes, a Python 3.11 job builds the
sdist and wheel, installs the wheel in a fresh environment, and checks CLI
help, database initialization, and passphrase key initialization.

CI does not publish packages or upload distribution artifacts. Publishing is
handled by the [release workflow](../.github/workflows/release.yml); follow
[Release](RELEASE.md) when preparing a version.

### Local checks

From an activated [development environment](../CONTRIBUTING.md#development-setup):

```bash
python -m ruff check .
python -m mypy oacs
python -m pytest -q
acs conformance validate --json
```

The last command explicitly checks portable fixtures. Pytest also includes
conformance, documentation, and packaging checks. LM Studio is not required
for the default suite.

### Build and inspect the package

Use a fresh temporary directory so an older wheel cannot enter the smoke test:

```bash
BUILD_DIR=$(mktemp -d)
python -m build --outdir "$BUILD_DIR/dist"
python -m twine check "$BUILD_DIR"/dist/*
python -m venv "$BUILD_DIR/smoke"
"$BUILD_DIR/smoke/bin/python" -m pip install "$BUILD_DIR"/dist/*.whl
"$BUILD_DIR/smoke/bin/acs" --version
"$BUILD_DIR/smoke/bin/acs" --help
"$BUILD_DIR/smoke/bin/acs" init --db "$BUILD_DIR/smoke.db" --json
"$BUILD_DIR/smoke/bin/acs" key init --db "$BUILD_DIR/smoke.db" --passphrase smoke-pass --json
"$BUILD_DIR/smoke/bin/acs" conformance validate --json
```

`smoke-pass` is a synthetic test value. These commands need network access to
install build and runtime dependencies. Inspect and remove your temporary build
directory when finished; no repository database or existing `dist/` is removed.

## RU

[GitHub Actions CI](../.github/workflows/ci.yml) запускается при отправке изменений
и запросах на включение в `main`. Задание качества устанавливает `.[dev,crypto]`
и запускает Ruff, Mypy и Pytest на Python 3.11 и 3.12. После успеха отдельное
задание на Python 3.11 собирает sdist и wheel, устанавливает wheel в чистое
окружение и проверяет справку CLI, создание базы и ключа с парольной фразой.

CI не публикует пакеты и не загружает артефакты сборки. Публикацией управляет
[процесс релиза](../.github/workflows/release.yml); подготовка версии описана в
[руководстве](RELEASE.md).

### Локальные проверки

В активированном [окружении разработки](../CONTRIBUTING.md):

```bash
python -m ruff check .
python -m mypy oacs
python -m pytest -q
acs conformance validate --json
```

Последняя команда явно проверяет переносимые примеры соответствия стандарту.
Pytest также проверяет соответствие, документацию и упаковку. Основной набор
тестов не требует LM Studio.

### Сборка и проверка пакета

Используйте новый временный каталог, чтобы не установить старый wheel:

```bash
BUILD_DIR=$(mktemp -d)
python -m build --outdir "$BUILD_DIR/dist"
python -m twine check "$BUILD_DIR"/dist/*
python -m venv "$BUILD_DIR/smoke"
"$BUILD_DIR/smoke/bin/python" -m pip install "$BUILD_DIR"/dist/*.whl
"$BUILD_DIR/smoke/bin/acs" --version
"$BUILD_DIR/smoke/bin/acs" --help
"$BUILD_DIR/smoke/bin/acs" init --db "$BUILD_DIR/smoke.db" --json
"$BUILD_DIR/smoke/bin/acs" key init --db "$BUILD_DIR/smoke.db" --passphrase smoke-pass --json
"$BUILD_DIR/smoke/bin/acs" conformance validate --json
```

`smoke-pass` является вымышленным тестовым значением. Для установки зависимостей
сборки и пакета нужна сеть. После проверки удалите созданный временный каталог;
команды не удаляют базу проекта или существующий `dist/`.
