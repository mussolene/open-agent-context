from __future__ import annotations

from pathlib import Path

import pytest

from oacs.app import services
from oacs.core.errors import LockedKeyError


def test_memory_plaintext_not_in_sqlite(db: Path):
    svc = services(str(db))
    mem = svc.memory.propose("fact", 2, "plaintext-never-in-db", None, ["project"])
    svc.memory.commit(mem.id, None)
    assert b"plaintext-never-in-db" not in db.read_bytes()


def test_wrong_passphrase_fails(tmp_path: Path):
    db = tmp_path / "oacs.db"
    svc = services(str(db), require_key=False)
    svc.key_provider.generate("right")
    svc.key_provider.lock()
    with pytest.raises(LockedKeyError):
        services(str(db), passphrase="wrong")


def test_key_rotation_keeps_records_readable(db: Path):
    svc = services(str(db))
    mem = svc.memory.propose("fact", 2, "rotation readable", None, ["project"])
    svc.memory.commit(mem.id, None)
    svc.key_provider.rotate("unit-example-phrase")
    assert services(str(db)).memory.read(mem.id, None).content.text == "rotation readable"
