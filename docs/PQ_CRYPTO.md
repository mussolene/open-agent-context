# PQ Crypto / PQ Crypto

## EN
OACS v0.1 uses symmetric AEAD for data encryption. The post-quantum-ready layer
is a key wrapping abstraction, not a claim of absolute quantum safety.

`HybridPQCKeyProvider` is crypto-agile. If a maintained ML-KEM/Kyber-compatible
Python binding is unavailable, the provider reports unavailable and tests skip
PQC-specific behavior. It never substitutes RSA/ECC and calls it PQC.

## RU
OACS v0.1 использует симметричное AEAD-шифрование данных. Post-quantum-ready
слой — это абстракция обёртки ключей, а не обещание абсолютной квантовой
безопасности.

`HybridPQCKeyProvider` crypto-agile. Если поддерживаемая ML-KEM/Kyber-compatible
Python-библиотека недоступна, provider честно сообщает unavailable. Он не
подменяет PQC RSA/ECC и не называет это PQC.
