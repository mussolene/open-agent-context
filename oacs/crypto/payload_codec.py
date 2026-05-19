from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, cast

from oacs.core.json import dumps, loads
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes

EncryptionMode = Literal["local_passphrase", "local_unlocked"]


@dataclass(frozen=True)
class EncodedPayload:
    nonce: bytes
    ciphertext: bytes


class PayloadCodec:
    def __init__(self, mode: EncryptionMode, master_key: bytes | None = None):
        self.mode = mode
        self.master_key = master_key

    def encode(self, payload: dict[str, object], aad: bytes) -> EncodedPayload:
        plaintext = dumps(payload).encode("utf-8")
        if self.master_key is None:
            raise ValueError("encrypted payload codec requires master_key")
        nonce, ciphertext = encrypt_json_bytes(self.master_key, plaintext, aad)
        return EncodedPayload(nonce=nonce, ciphertext=ciphertext)

    def decode(self, nonce: object, ciphertext: object, aad: bytes) -> dict[str, object]:
        nonce_bytes = _bytes(nonce)
        ciphertext_bytes = _bytes(ciphertext)
        if self.master_key is None:
            raise ValueError("encrypted payload codec requires master_key")
        return cast(
            dict[str, object],
            loads(decrypt_json_bytes(self.master_key, nonce_bytes, ciphertext_bytes, aad)),
        )


def _bytes(value: object) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise TypeError(f"expected bytes payload, got {type(value).__name__}")
