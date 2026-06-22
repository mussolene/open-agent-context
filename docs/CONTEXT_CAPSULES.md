# Context Capsules / Context Capsules

## EN
A Context Capsule is the portable object passed to an agent. It contains purpose,
task, actor, agent, scope, token budget, included memory/rule/skill/tool IDs,
evidence refs, forbidden assumptions, permissions, expiry, audit refs, and a
checksum. Sensitive fields are encrypted in storage and exported as JSON when
authorized.

Capsule export can use a `context_capsule_export` envelope containing
`capsule` and `integrity`. This envelope is draft support for reference
import/export packaging, not part of the v1.0 stable portable schema set. The
capsule `checksum` is SHA-256 over canonical JSON excluding the `checksum`
field. Export `integrity.payload_checksum` is SHA-256 over the exported capsule
payload. `integrity.mac` is an HMAC-SHA256 tag computed with the local master
key; `integrity.signature` is accepted as a deprecated compatibility alias for
the same value. The MAC proves the export was produced by a holder of that local
key, but it is not a public-key signature and does not prove author identity to
third parties.

Prompt rendering is a reference adapter concern, not a new stable capsule
schema. Consumers should avoid flattening a capsule into neutral prose before a
model sees it. A runtime adapter should preserve the roles of facts, hypotheses,
evidence refs, tool observations, rules, permissions, and forbidden assumptions
on the prompt surface. See `docs/CONTEXT_PROMPTING.md` and
`examples/context_prompting/` for the reference renderer and bad/good examples.

## RU
Context Capsule — переносимый объект, передаваемый агенту. Он содержит purpose,
task, actor, agent, scope, token budget, ID включённой памяти/правил/skills/tools,
evidence refs, запрещённые предположения, permissions, expiry, audit refs и
checksum. Чувствительные поля шифруются в хранилище и экспортируются в JSON
только при наличии прав.

Capsule export может использовать envelope
`context_capsule_export` с полями `capsule` и `integrity`. Этот envelope
является draft support для reference import/export packaging, а не частью v1.0
stable portable schema set. Capsule `checksum` - это SHA-256 по canonical JSON
без поля `checksum`. Export `integrity.payload_checksum` - SHA-256 по exported
capsule payload. `integrity.mac` - HMAC-SHA256 tag, вычисленный с local
master key; `integrity.signature` принимается как deprecated compatibility alias
для того же значения. MAC показывает, что export создан держателем этого local
key, но не является public-key signature и не доказывает author identity третьим
сторонам.

Prompt rendering является задачей reference adapter, а не новой stable capsule
schema. Consumers не должны превращать capsule в нейтральную прозу перед
передачей модели. Runtime adapter должен сохранять роли facts, hypotheses,
evidence refs, tool observations, rules, permissions и forbidden assumptions на
prompt surface. См. `docs/CONTEXT_PROMPTING.md` и
`examples/context_prompting/` для reference renderer и bad/good examples.
