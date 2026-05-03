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
payload. `integrity.signature` is an HMAC-SHA256 tag computed with the local
master key; it proves the export was produced by a holder of that local key, but
it is not a public-key signature and does not prove author identity to third
parties.

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
capsule payload. `integrity.signature` - HMAC-SHA256 tag, вычисленный с local
master key; он показывает, что export создан держателем этого local key, но не
является public-key signature и не доказывает author identity третьим сторонам.
