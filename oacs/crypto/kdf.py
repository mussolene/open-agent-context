from __future__ import annotations

import importlib
import os
from typing import Any

try:
    _argon2_low_level: Any = importlib.import_module("argon2.low_level")
    argon2_hash_secret_raw: Any = _argon2_low_level.hash_secret_raw
    Argon2Type: Any = _argon2_low_level.Type
except Exception:  # pragma: no cover - optional dependency path
    argon2_hash_secret_raw = None
    Argon2Type = None

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def new_salt() -> bytes:
    return os.urandom(16)


def derive_key(passphrase: str, salt: bytes) -> tuple[bytes, str]:
    secret = passphrase.encode("utf-8")
    if argon2_hash_secret_raw is not None and Argon2Type is not None:
        raw_hash: Any = argon2_hash_secret_raw
        argon_type: Any = Argon2Type
        return (
            raw_hash(
                secret=secret,
                salt=salt,
                time_cost=3,
                memory_cost=64 * 1024,
                parallelism=2,
                hash_len=32,
                type=argon_type.ID,
            ),
            "argon2id",
        )
    return (
        Scrypt(salt=salt, length=32, n=2**14, r=8, p=1).derive(secret),
        "scrypt",
    )
