# OACS Killer Demo

## EN
This demo proves the OACS product story with local artifacts:

- write one scoped memory;
- build and export a governed Context Capsule;
- validate the exported capsule;
- run the memory-call loop and keep its trace;
- import MCP server metadata as an adapter boundary;
- verify the audit chain;
- link the checked-in full-context benchmark comparison.

It does not require network access, LM Studio, a hosted service, or a running
model. It uses the local `acs` CLI through `python -m oacs.cli.main`.

Run from the repository root:

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```

The script writes raw JSON artifacts and `SUMMARY.md` into the output directory.
The most important files are:

- `summary.json` and `SUMMARY.md` - product story and proof points.
- `06_memory_query.json` - the committed scoped memory was retrieved.
- `07_context_build.json` - the portable Context Capsule.
- `08_context_export.json` and `09_context_validate.json` - export envelope and
  validation result.
- `10_loop_run.json` - `memory_calls`, selected evidence, compact prompt, and
  operation metrics.
- `12_mcp_import.json` and `13_mcp_list.json` - MCP adapter metadata.
- `14_audit_verify.json` - audit chain verification.
- `api_context_build.json`, `api_context_export.json`, and `api_loop_run.json`
  - API-shaped request/response artifacts for the same flow.

The demo intentionally positions OACS as a draft governed memory/context
contract and adapter boundary. It is not an agent framework, model backend,
vector database, benchmark harness, or MCP replacement.

## RU
Этот demo доказывает продуктовый тезис OACS через локальные артефакты:

- записать одну scoped memory;
- построить и экспортировать governed Context Capsule;
- провалидировать экспортированную capsule;
- запустить memory-call loop и сохранить trace;
- импортировать MCP server metadata как adapter boundary;
- проверить audit chain;
- сослаться на checked-in сравнение против full-context prompting.

Demo не требует network access, LM Studio, hosted service или запущенной модели.
Оно использует локальный `acs` CLI через `python -m oacs.cli.main`.

Запуск из корня репозитория:

```bash
python3 examples/killer_demo/run_demo.py --out .oacs/killer-demo --force
```

Скрипт пишет raw JSON artifacts и `SUMMARY.md` в output directory. Самые важные
файлы:

- `summary.json` и `SUMMARY.md` - product story и proof points.
- `06_memory_query.json` - committed scoped memory была найдена.
- `07_context_build.json` - portable Context Capsule.
- `08_context_export.json` и `09_context_validate.json` - export envelope и
  validation result.
- `10_loop_run.json` - `memory_calls`, selected evidence, compact prompt и
  operation metrics.
- `12_mcp_import.json` и `13_mcp_list.json` - MCP adapter metadata.
- `14_audit_verify.json` - audit chain verification.
- `api_context_build.json`, `api_context_export.json` и `api_loop_run.json` -
  API-shaped request/response artifacts для того же flow.

Demo намеренно позиционирует OACS как draft governed memory/context contract и
adapter boundary. Это не agent framework, model backend, vector database,
benchmark harness или MCP replacement.
