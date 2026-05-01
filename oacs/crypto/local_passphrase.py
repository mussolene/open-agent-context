from __future__ import annotations

import base64
import json
import os
from contextlib import suppress
from pathlib import Path

from cryptography.exceptions import InvalidTag

from oacs.core.errors import LockedKeyError
from oacs.crypto.aead import decrypt_json_bytes, encrypt_json_bytes, generate_key
from oacs.crypto.kdf import derive_key, new_salt
from oacs.crypto.key_provider import KeyProvider, KeyStatus


class LocalPassphraseKeyProvider(KeyProvider):
    def __init__(self, key_file: Path, unlocked_file: Path):
        self.key_file = key_file
        self.unlocked_file = unlocked_file
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

    def generate(self, passphrase: str) -> dict[str, object]:
        master_key = generate_key()
        metadata = self.wrap_key(master_key, passphrase)
        self._write_unlocked(master_key)
        return metadata

    def wrap_key(self, master_key: bytes, passphrase: str) -> dict[str, object]:
        salt = new_salt()
        wrapping_key, kdf = derive_key(passphrase, salt)
        nonce, ciphertext = encrypt_json_bytes(wrapping_key, master_key, b"oacs-master-key")
        metadata: dict[str, object] = {
            "provider": "local_passphrase",
            "algorithm_name": "AES-256-GCM",
            "algorithm_version": "v0.1",
            "kdf": kdf,
            "salt": _b64(salt),
            "nonce": _b64(nonce),
            "wrapped_master_key": _b64(ciphertext),
        }
        self.key_file.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
        return metadata

    def unwrap_key(self, passphrase: str) -> bytes:
        if not self.key_file.exists():
            raise LockedKeyError("key provider is not initialized")
        metadata = json.loads(self.key_file.read_text(encoding="utf-8"))
        salt = _unb64(metadata["salt"])
        wrapping_key, _ = derive_key(passphrase, salt)
        try:
            master = decrypt_json_bytes(
                wrapping_key,
                _unb64(metadata["nonce"]),
                _unb64(metadata["wrapped_master_key"]),
                b"oacs-master-key",
            )
        except InvalidTag as exc:
            raise LockedKeyError("wrong passphrase or corrupted key metadata") from exc
        self._write_unlocked(master)
        return master

    def load_unlocked(self) -> bytes:
        if not self.unlocked_file.exists():
            raise LockedKeyError("master key is locked; run acs key unlock")
        return _unb64(self.unlocked_file.read_text(encoding="utf-8").strip())

    def lock(self) -> None:
        if self.unlocked_file.exists():
            self.unlocked_file.unlink()

    def export_public(self) -> dict[str, object]:
        if not self.key_file.exists():
            raise LockedKeyError("key provider is not initialized")
        metadata = json.loads(self.key_file.read_text(encoding="utf-8"))
        return {
            "provider": metadata["provider"],
            "algorithm_name": metadata["algorithm_name"],
            "algorithm_version": metadata["algorithm_version"],
            "kdf": metadata["kdf"],
        }

    def rotate(self, passphrase: str) -> dict[str, object]:
        master = self.unwrap_key(passphrase)
        return self.wrap_key(master, passphrase)

    def status(self) -> KeyStatus:
        return KeyStatus(
            provider="local_passphrase",
            available=self.key_file.exists(),
            unlocked=self.unlocked_file.exists(),
            algorithm_name="AES-256-GCM",
            message="ready" if self.key_file.exists() else "not initialized",
        )

    def _write_unlocked(self, master_key: bytes) -> None:
        self.unlocked_file.write_text(_b64(master_key), encoding="utf-8")
        with suppress(OSError):
            os.chmod(self.unlocked_file, 0o600)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.b64decode(text.encode("ascii"))
