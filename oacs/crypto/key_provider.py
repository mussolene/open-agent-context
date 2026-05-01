from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class KeyStatus:
    provider: str
    available: bool
    unlocked: bool
    algorithm_name: str
    message: str


class KeyProvider(ABC):
    @abstractmethod
    def generate(self, passphrase: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def wrap_key(self, master_key: bytes, passphrase: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def unwrap_key(self, passphrase: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def export_public(self) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def rotate(self, passphrase: str) -> dict[str, object]:
        raise NotImplementedError

    @abstractmethod
    def status(self) -> KeyStatus:
        raise NotImplementedError
