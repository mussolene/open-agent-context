from __future__ import annotations

from pathlib import Path

from oacs.crypto.key_provider import KeyProvider, KeyStatus


class HybridPQCKeyProvider(KeyProvider):
    """Crypto-agile PQC key wrapping adapter.

    The provider is deliberately unavailable unless a real maintained ML-KEM
    binding is installed. It never substitutes RSA/ECC as "post-quantum".
    """

    def __init__(self, metadata_file: Path | None = None):
        self.metadata_file = metadata_file
        try:
            import oqs  # noqa: F401

            self._available = True
        except Exception:
            self._available = False

    def generate(self, passphrase: str) -> dict[str, object]:
        self._raise_unavailable()
        raise AssertionError("unreachable")

    def wrap_key(self, master_key: bytes, passphrase: str) -> dict[str, object]:
        self._raise_unavailable()
        raise AssertionError("unreachable")

    def unwrap_key(self, passphrase: str) -> bytes:
        self._raise_unavailable()
        raise AssertionError("unreachable")

    def export_public(self) -> dict[str, object]:
        return {
            "provider": "hybrid_pqc",
            "available": self._available,
            "message": self.status().message,
        }

    def rotate(self, passphrase: str) -> dict[str, object]:
        self._raise_unavailable()
        raise AssertionError("unreachable")

    def status(self) -> KeyStatus:
        if self._available:
            return KeyStatus(
                provider="hybrid_pqc",
                available=True,
                unlocked=False,
                algorithm_name="ML-KEM-compatible",
                message="PQC binding detected; integration is reserved for optional pq extras",
            )
        return KeyStatus(
            provider="hybrid_pqc",
            available=False,
            unlocked=False,
            algorithm_name="unavailable",
            message="HybridPQCKeyProvider unavailable: install optional pq extras",
        )

    def _raise_unavailable(self) -> None:
        raise RuntimeError(self.status().message)
