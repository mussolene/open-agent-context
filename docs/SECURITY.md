# Security / Безопасность

## EN
Threats addressed in the POC: plaintext memory exposure, accidental capability
leaks, hidden memory writes, fuzzy memory used as fact, and unaudited access.

Memory and capsule payloads use envelope-style AEAD encryption at rest. The
local passphrase provider wraps a master key; an unlocked session key can be
stored locally for development and removed with `acs key lock`.

Audit events store operation metadata and hashes, not secret content.

## RU
POC закрывает риски: хранение памяти в открытом виде, случайные утечки
capability, скрытые записи памяти, использование fuzzy memory как факта и
доступ без аудита.

Payload памяти и capsules шифруются AEAD. Локальный passphrase provider
оборачивает master key; unlock-сессия может храниться локально для разработки
и удаляется через `acs key lock`.

Audit events содержат metadata и хэши, но не секретный контент.
