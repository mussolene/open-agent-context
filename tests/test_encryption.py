from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from typer.testing import CliRunner

from oacs.app import services
from oacs.cli.main import app
from oacs.core.errors import LockedKeyError, MemoryDecryptError


def corrupt_memory_ciphertext(db: Path, memory_id: str) -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            "UPDATE memory_records SET content_ciphertext=? WHERE id=?",
            (b"not-valid-ciphertext", memory_id),
        )
        conn.commit()


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


def test_memory_query_skips_unreadable_records_by_default(db: Path):
    svc = services(str(db))
    good = svc.memory.propose("fact", 2, "healthy searchable memory", None, ["project"])
    svc.memory.commit(good.id, None)
    bad = svc.memory.propose("fact", 2, "corrupt searchable memory", None, ["project"])
    svc.memory.commit(bad.id, None)
    corrupt_memory_ciphertext(db, bad.id)

    result = services(str(db)).memory.query("searchable", None, ["project"])

    assert [mem.id for mem in result] == [good.id]
    svc = services(str(db))
    warnings = svc.memory.query("searchable", None, ["project"])
    assert [mem.id for mem in warnings] == [good.id]
    assert svc.memory.last_warnings[0]["record_id"] == bad.id


def test_memory_query_strict_raises_domain_error(db: Path):
    svc = services(str(db))
    bad = svc.memory.propose("fact", 2, "strict corrupt memory", None, ["project"])
    svc.memory.commit(bad.id, None)
    corrupt_memory_ciphertext(db, bad.id)

    with pytest.raises(MemoryDecryptError) as exc:
        services(str(db)).memory.query("strict", None, ["project"], strict=True)

    assert exc.value.record["record_id"] == bad.id
    assert "content_ciphertext" not in exc.value.record


def test_context_build_tracks_warning_outside_portable_capsule(db: Path):
    svc = services(str(db))
    good = svc.memory.propose("fact", 2, "context healthy memory", None, ["project"])
    svc.memory.commit(good.id, None)
    bad = svc.memory.propose("fact", 2, "context corrupt memory", None, ["project"])
    svc.memory.commit(bad.id, None)
    corrupt_memory_ciphertext(db, bad.id)

    svc = services(str(db))
    capsule = svc.context.build("context memory", None, scope=["project"])

    assert capsule.included_memories == [good.id]
    assert "warnings" not in capsule.model_dump()
    assert svc.context.last_warnings[0]["record_id"] == bad.id
    assert svc.context.last_warnings[0]["type"] == "UnreadableMemoryRecord"


def test_memory_doctor_and_quarantine_cli(db: Path):
    svc = services(str(db))
    bad = svc.memory.propose("fact", 2, "doctor corrupt memory", None, ["project"])
    svc.memory.commit(bad.id, None)
    corrupt_memory_ciphertext(db, bad.id)
    runner = CliRunner()

    doctor = runner.invoke(app, ["memory", "doctor", "--db", str(db), "--json"])
    assert doctor.exit_code == 1
    assert bad.id in doctor.output

    quarantine = runner.invoke(
        app, ["memory", "quarantine", bad.id, "--db", str(db), "--json"]
    )
    assert quarantine.exit_code == 0, quarantine.output
    assert services(str(db)).memory.decrypt_health()["status"] == "PASS"
