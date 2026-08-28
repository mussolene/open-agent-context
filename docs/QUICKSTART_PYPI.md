# PyPI Quickstart / Быстрый старт через PyPI

[Documentation / Документация](README.md)

## EN

Install the current Python reference release of OACS v1.0. Requires Python
3.11 or later; no model server or API key is needed. Commands use a POSIX shell.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install oacs==1.0.21

export OACS_DB=./.oacs/oacs.db

acs init --json
acs key init --json
```

Create and retrieve one scoped memory:

```bash
CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "In project Alpha reports are generated with make report-safe." --json \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha report" --scope project --json
acs context build --intent answer_project_question --query "Alpha report" \
  --scope project --budget 4000 --json
```

`--intent` sets the categorical capsule purpose. `--query` is the text used by
the Python reference retriever. The default lexical provider returns no memory
when there is no text overlap instead of filling the capsule with zero-score
records.

The default key provider stores local key material beside the database. Keep
`.oacs/` private and untracked. See [Security](SECURITY.md) for passphrase
wrapping and strict permission mode.

To run the offline demo, first follow the
[source installation guide](../CONTRIBUTING.md#development-setup):

```bash
python examples/killer_demo/run_demo.py --out .oacs/killer-demo
```

## RU

Установка текущего релиза эталонной реализации OACS v1.0 на Python. Нужен
Python 3.11 или новее; сервер модели и ключ API не требуются. Команды
рассчитаны на POSIX shell.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install oacs==1.0.21

export OACS_DB=./.oacs/oacs.db

acs init --json
acs key init --json
```

Создать и найти запись памяти в области проекта:

```bash
CANDIDATE_ID=$(acs memory propose --type procedure --depth 2 --scope project \
  --text "В проекте Alpha отчёты генерируются через make report-safe." --json \
  | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')

acs memory commit "$CANDIDATE_ID" --json
acs memory query --query "Alpha отчёты" --scope project --json
acs context build --intent answer_project_question --query "Alpha отчёты" \
  --scope project --budget 4000 --json
```

`--intent` задаёт категорию задачи, `--query` передаёт текст поиска в
реализацию на Python. Если совпадений по тексту нет, лексический поиск по
умолчанию не заполняет капсулу записями с нулевой оценкой.

По умолчанию ключ хранится рядом с локальной базой. Не публикуйте `.oacs/`
и ограничьте доступ к каталогу. Защита ключа парольной фразой и строгий режим
разрешений описаны в [руководстве безопасности](SECURITY.md).

Для демонстрации без сети сначала выполните
[установку из исходников](../CONTRIBUTING.md):

```bash
python examples/killer_demo/run_demo.py --out .oacs/killer-demo
```
