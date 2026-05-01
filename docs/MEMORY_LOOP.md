# Memory Loop / Memory Loop

## EN
The memory loop executes: observe -> classify intent -> retrieve memory -> build
capsule -> apply rules -> select skills/tools -> act -> evaluate -> propose
memory -> policy check -> commit/discard -> audit.

The POC uses deterministic local behavior by default and can call LM Studio when
explicitly configured.

In v0.2.6, memory operations can be represented as `memory_calls`. A
`memory_call` is similar in shape to a model tool call, but it is executed by
OACS rather than delegated to backend-specific tool-calling support.
`MemoryLoopEngine`, CLI `acs loop run`, API `/v1/loop/run`, and the reference
benchmark can emit calls such as `memory.query`, `memory.read`, and
`memory.extract_evidence`. Evidence selection is pluggable: the core memory-call
loop records calls and builds the projection, while selectors interpret typed
evidence dimensions. The adaptive context policy keeps tiny low-pressure tasks
on compact capsules, uses `memory_calls` for structured evidence and
medium/large contexts, and keeps deepening explicit, caller-configurable, and
filtered by the actor's scoped memory grants.

## RU
Memory loop выполняет: observe -> classify intent -> retrieve memory -> build
capsule -> apply rules -> select skills/tools -> act -> evaluate -> propose
memory -> policy check -> commit/discard -> audit.

По умолчанию POC детерминированный и локальный; LM Studio вызывается только при
явной настройке.

В v0.2.6 memory operations могут быть представлены как `memory_calls`.
`memory_call` похож по форме на model tool call, но выполняется OACS, а не
backend-specific tool-calling support. `MemoryLoopEngine`, CLI `acs loop run`,
API `/v1/loop/run` и reference benchmark могут emit calls например
`memory.query`, `memory.read` и `memory.extract_evidence`. Evidence selection
расширяемый: core memory-call loop записывает calls и строит projection, а
selectors интерпретируют typed evidence dimensions. Adaptive context policy
оставляет tiny low-pressure tasks на compact capsules, использует
`memory_calls` для structured evidence и medium/large contexts, а deepening
остаётся явным, управляемым caller configuration и filtered через scoped memory
grants actor.
