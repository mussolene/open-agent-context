from __future__ import annotations

from pathlib import Path

import pytest

from oacs.app import services


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    path = tmp_path / "oacs.db"
    svc = services(str(path), require_key=False)
    svc.key_provider.generate("unit-example-phrase")
    return path


@pytest.fixture()
def svc(db: Path):
    return services(str(db))
