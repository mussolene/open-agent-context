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
acs capability grant-evidence \
  --subject agent_retriever \
  --tool external_search \
  --json

acs tool ingest-result \
  --actor agent_retriever \
  --tool-id external_search \
  --tool-name "External Search" \
  --output '{"answer":"OACS stores governed context."}' \
  --source-uri https://example.test/search/123 \
  --json
```

This writes the same `tool_result` evidence shape and an
`evidence.ingest_tool_result` audit event. OACS governs provenance, scope,
hashing, and later context projection; it does not choose or schedule the tool.
For non-bootstrap actors, evidence ingestion is tool-scoped: grant
`evidence.ingest` through `acs capability grant-evidence --tool <tool-id>` or an
equivalent `acs capability grant --operation evidence.ingest --tool <tool-id>`.
`acs capability grant-tool` grants `tool.call` for executing a tool; it does not
authorize ingesting a result that another orchestrator already produced.

Canonical retrieval pattern for external knowledge:

```text
external retrieval tool -> tool ingest-result -> EvidenceRef -> memory sharpen -> context build
```

For example, a 1C documentation retriever can run outside OACS, pass the
retrieved canonical snippet through `acs tool ingest-result`, receive an
`EvidenceRef`, attach that ref to a distilled memory through
`acs memory sharpen --evidence <ev_...>`, and then use `acs context build`.
The raw tool-call evidence does not enter `ContextCapsule.evidence_refs` by
itself. Context build projects evidence refs from included memories, so the
sharpening step is the bridge from external canonical evidence to task context.

Debug evidence refs during proof-loop work:

```bash
acs evidence list --kind tool_result --json
acs evidence inspect <ev_...> --json
```

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
acs capability grant-evidence \
  --subject agent_retriever \
  --tool external_search \
  --json

acs tool ingest-result \
  --actor agent_retriever \
  --tool-id external_search \
  --tool-name "External Search" \
  --output '{"answer":"OACS stores governed context."}' \
  --source-uri https://example.test/search/123 \
  --json
```

Это пишет тот же `tool_result` evidence shape и audit event
`evidence.ingest_tool_result`. OACS отвечает за provenance, scope, hashing и
последующую projection в context; он не выбирает и не планирует tool.
Для non-bootstrap actors evidence ingestion ограничен конкретными tools:
выдавайте `evidence.ingest` через
`acs capability grant-evidence --tool <tool-id>` или эквивалентный
`acs capability grant --operation evidence.ingest --tool <tool-id>`.
`acs capability grant-tool` выдаёт `tool.call` для выполнения tool; он не
разрешает ingest результата, который уже произвёл другой orchestrator.

Canonical retrieval pattern для внешних знаний:

```text
external retrieval tool -> tool ingest-result -> EvidenceRef -> memory sharpen -> context build
```

Например, retriever справки 1С может работать вне OACS, передать найденный
canonical snippet через `acs tool ingest-result`, получить `EvidenceRef`,
привязать этот ref к distilled memory через
`acs memory sharpen --evidence <ev_...>`, а затем вызвать `acs context build`.
Raw tool-call evidence сам по себе не попадает в
`ContextCapsule.evidence_refs`. Context build проецирует evidence refs из
включённых memories, поэтому sharpening step является мостом от внешнего
canonical evidence к task context.

Evidence refs можно смотреть во время proof-loop/debugging:

```bash
acs evidence list --kind tool_result --json
acs evidence inspect <ev_...> --json
```

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
