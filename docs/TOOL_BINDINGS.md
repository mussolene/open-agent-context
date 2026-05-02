# Tool Bindings / Tool Bindings

## EN
`ToolBinding` is a portable governance contract for tools. OACS does not
replace native model or IDE tool-calling. It defines metadata, capability
checks, schema validation, audit, and `EvidenceRef` capture around a tool call.

Minimal local setup:

```bash
acs actor create --type agent --name "ToolAgent" --json

acs capability grant-tool \
  --subject <actor_id> \
  --tool tool_local_echo \
  --json

acs tool call local_echo \
  --actor <actor_id> \
  --payload '{"hello":"world"}' \
  --json
```

Register a local CLI tool:

```bash
acs tool add \
  --name json_cli \
  --type local_cli \
  --command "python3 ./tools/my_tool.py" \
  --output-schema ./schemas/my_tool.output.schema.json \
  --json
```

`local_cli` tools receive the JSON payload on stdin. If stdout is a JSON object,
OACS includes it under `output.json`. Every successful call returns
`ToolCallResult` and writes a `tool_result` `EvidenceRef`.

If another orchestrator already executed a tool, submit the result instead of
asking OACS to run it:

```bash
acs tool ingest-result \
  --tool-id external_search \
  --tool-name "External Search" \
  --output '{"answer":"OACS stores governed context."}' \
  --source-uri https://example.test/search/123 \
  --json
```

This writes the same `tool_result` evidence shape and an
`evidence.ingest_tool_result` audit event. OACS governs provenance, scope,
hashing, and later context projection; it does not choose or schedule the tool.

HTTP tools are disabled by default unless the binding explicitly opts in:

```bash
acs tool add \
  --name local_http_lookup \
  --type http \
  --http-url http://127.0.0.1:8080/query \
  --allow-network \
  --json
```

Keep domain-specific integrations outside the OACS core. They should be
registered as ordinary ToolBindings and Skills.

## RU
`ToolBinding` - переносимый governance contract для tools. OACS не заменяет
native model или IDE tool-calling. Он задаёт metadata, capability checks, schema
validation, audit и capture `EvidenceRef` вокруг tool call.

Минимальная локальная настройка:

```bash
acs actor create --type agent --name "ToolAgent" --json

acs capability grant-tool \
  --subject <actor_id> \
  --tool tool_local_echo \
  --json

acs tool call local_echo \
  --actor <actor_id> \
  --payload '{"hello":"world"}' \
  --json
```

Зарегистрировать local CLI tool:

```bash
acs tool add \
  --name json_cli \
  --type local_cli \
  --command "python3 ./tools/my_tool.py" \
  --output-schema ./schemas/my_tool.output.schema.json \
  --json
```

`local_cli` tools получают JSON payload через stdin. Если stdout является JSON
object, OACS добавляет его в `output.json`. Каждый успешный вызов возвращает
`ToolCallResult` и пишет `tool_result` `EvidenceRef`.

Если другой orchestrator уже выполнил tool, передайте результат, не заставляя
OACS запускать tool:

```bash
acs tool ingest-result \
  --tool-id external_search \
  --tool-name "External Search" \
  --output '{"answer":"OACS stores governed context."}' \
  --source-uri https://example.test/search/123 \
  --json
```

Это пишет тот же `tool_result` evidence shape и audit event
`evidence.ingest_tool_result`. OACS отвечает за provenance, scope, hashing и
последующую projection в context; он не выбирает и не планирует tool.

HTTP tools отключены по умолчанию, пока binding явно не разрешит network:

```bash
acs tool add \
  --name local_http_lookup \
  --type http \
  --http-url http://127.0.0.1:8080/query \
  --allow-network \
  --json
```

Доменные integrations должны оставаться вне OACS core. Их нужно подключать как
обычные ToolBindings и Skills.
