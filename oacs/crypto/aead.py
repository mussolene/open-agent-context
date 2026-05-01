from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def encrypt_json_bytes(key: bytes, plaintext: bytes, aad: bytes = b"") -> tuple[bytes, bytes]:
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt_json_bytes(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
