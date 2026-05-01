# Memory Loop / Memory Loop

## EN
The memory loop executes: observe -> classify intent -> retrieve memory -> build
capsule -> apply rules -> select skills/tools -> act -> evaluate -> propose
memory -> policy check -> commit/discard -> audit.

The POC uses deterministic local behavior by default and can call LM Studio when
explicitly configured.

In v0.2.0, memory operations can be represented as `memory_calls`. A
`memory_call` is similar in shape to a model tool call, but it is executed by
OACS rather than delegated to backend-specific tool-calling support. The current
reference benchmark emits calls such as `memory.query` and
`memory.extract_evidence`.

## RU
Memory loop выполняет: observe -> classify intent -> retrieve memory -> build
capsule -> apply rules -> select skills/tools -> act -> evaluate -> propose
memory -> policy check -> commit/discard -> audit.

По умолчанию POC детерминированный и локальный; LM Studio вызывается только при
явной настройке.

В v0.2.0 memory operations могут быть представлены как `memory_calls`.
`memory_call` похож по форме на model tool call, но выполняется OACS, а не
backend-specific tool-calling support. Текущий reference benchmark emits calls
например `memory.query` и `memory.extract_evidence`.
