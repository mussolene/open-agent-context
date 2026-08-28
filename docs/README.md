# Documentation / Документация

[Project overview / О проекте](../README.md)

## EN

Start with the quickstart to use the package, or the specification to implement
OACS elsewhere. The portable standard is v1.0; Python package releases have
their own version history in the [changelog](../CHANGELOG.md). Adapter guides
describe the reference implementation, not additional conformance requirements.

| Area | Documents |
| --- | --- |
| Getting started | [PyPI quickstart](QUICKSTART_PYPI.md), [local demo](../examples/killer_demo/README.md), [glossary](GLOSSARY.md) |
| Standard and architecture | [Specification](SPEC.md), [architecture](ARCHITECTURE.md), [compatibility](COMPATIBILITY.md), [interoperability](INTEROPERABILITY.md), [schemas](../schemas/) |
| Memory and context | [Memory model](MEMORY_MODEL.md), [context capsules](CONTEXT_CAPSULES.md), [memory loop](MEMORY_LOOP.md), [context prompting](CONTEXT_PROMPTING.md), [prompt examples](../examples/context_prompting/README.md) |
| Policy and security | [Security](SECURITY.md), [external vault boundary](VAULT.md), [rules](RULES.md), [optional post-quantum integration](PQ_CRYPTO.md) |
| Integration | [HTTP API](API.md), [tool bindings](TOOL_BINDINGS.md), [MCP bindings](MCP_BINDINGS.md), [skills](SKILLS.md) |
| Repository workflows | [Agent workflow](AGENT_WORKFLOW.md), [consumer packs](CONSUMER_PACKS.md), [pack installation](../examples/consumer_packs/oacs_repo_development/README.md), [dogfood evidence workflow](DOGFOOD.md) |
| Validation | [Conformance guide](../conformance/README.md), [benchmark guide](BENCHMARK.md) |
| Development and releases | [Contributing](../CONTRIBUTING.md), [build checks](BUILD.md), [release process](RELEASE.md), [roadmap](ROADMAP.md), [changelog](../CHANGELOG.md) |
| v1.0 release records | [Release notes](V1_RELEASE_NOTES.md), [freeze manifest](FREEZE_PREP.md), [release checklist](V1_RELEASE_CHECKLIST.md) |

The freeze manifest retains its original `stable_candidate` labels for schema
coverage checks. Use the compatibility policy for the current stable contract
and the release process for subsequent package releases.

### Measured reports

These reports describe particular fixtures and model runs, not universal
performance guarantees:

- [Memory calls](../examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md)
- [Full-context comparison](../examples/benchmarks/full_context_gemma_e2b_2026-05-02.md)
- [Community memory tasks](../examples/benchmarks/community_memory_gemma_e2b_2026-05-02.md)

## RU

Для использования пакета начните с быстрого старта, для собственной реализации
OACS со спецификации. Версия переносимого стандарта: v1.0. История версий
пакета Python ведётся отдельно в [журнале изменений](../CHANGELOG.md).
Руководства по адаптерам описывают эталонную реализацию и не вводят новых
требований соответствия стандарту.

| Раздел | Документы |
| --- | --- |
| Начало работы | [Установка через PyPI](QUICKSTART_PYPI.md), [локальный пример](../examples/killer_demo/README.md), [глоссарий](GLOSSARY.md) |
| Стандарт и архитектура | [Спецификация](SPEC.md), [архитектура](ARCHITECTURE.md), [совместимость](COMPATIBILITY.md), [взаимодействие реализаций](INTEROPERABILITY.md), [схемы](../schemas/) |
| Память и контекст | [Модель памяти](MEMORY_MODEL.md), [капсулы](CONTEXT_CAPSULES.md), [цикл памяти](MEMORY_LOOP.md), [подготовка контекста](CONTEXT_PROMPTING.md), [примеры](../examples/context_prompting/README.md) |
| Правила и безопасность | [Безопасность](SECURITY.md), [внешнее хранилище секретов](VAULT.md), [правила](RULES.md), [необязательная постквантовая интеграция](PQ_CRYPTO.md) |
| Интеграция | [HTTP API](API.md), [инструменты](TOOL_BINDINGS.md), [MCP](MCP_BINDINGS.md), [навыки](SKILLS.md) |
| Работа с репозиторием | [Работа агента](AGENT_WORKFLOW.md), [пакеты интеграции](CONSUMER_PACKS.md), [установка пакета](../examples/consumer_packs/oacs_repo_development/README.md), [запись доказательств](DOGFOOD.md) |
| Проверки | [Соответствие стандарту](../conformance/README.md), [измерения](BENCHMARK.md) |
| Разработка и релизы | [Участие](../CONTRIBUTING.md), [сборка](BUILD.md), [релизы](RELEASE.md), [дорожная карта](ROADMAP.md), [журнал изменений](../CHANGELOG.md) |
| Материалы релиза v1.0 | [Примечания к релизу](V1_RELEASE_NOTES.md), [манифест фиксации схем](FREEZE_PREP.md), [контрольный список](V1_RELEASE_CHECKLIST.md) |

Манифест сохраняет исходные метки `stable_candidate` для проверок покрытия
схем. Действующий стабильный контракт описан в политике совместимости;
последующие версии пакета выпускаются по руководству релизов.

### Отчёты измерений

Отчёты относятся к конкретным наборам и запускам моделей и не гарантируют
одинаковый результат в других условиях:

- [Операции памяти](../examples/benchmarks/memory_calls_gemma_e2b_2026-05-01.md)
- [Сравнение с полным контекстом](../examples/benchmarks/full_context_gemma_e2b_2026-05-02.md)
- [Задачи на память из внешних наборов](../examples/benchmarks/community_memory_gemma_e2b_2026-05-02.md)
