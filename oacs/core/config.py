from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OacsConfig:
    db_path: Path
    base_dir: Path
    passphrase: str | None = None

    @classmethod
    def from_values(cls, db: str | None = None, passphrase: str | None = None) -> OacsConfig:
        db_value = db or os.getenv("OACS_DB") or discover_project_db() or "./.oacs/oacs.db"
        db_path = Path(db_value).expanduser()
        return cls(
            db_path=db_path,
            base_dir=db_path.parent,
            passphrase=passphrase or os.getenv("OACS_PASSPHRASE"),
        )

    @property
    def key_file(self) -> Path:
        return self.base_dir / "key.json"

    @property
    def unlocked_file(self) -> Path:
        return self.base_dir / "unlocked.key"


def discover_project_db(start: Path | None = None) -> str | None:
    current = (start or Path.cwd()).resolve()
    for folder in (current, *current.parents):
        for candidate in (
            folder / ".agent" / "oacs" / "oacs.db",
            folder / ".oacs" / "oacs.db",
        ):
            if candidate.exists():
                return str(candidate)
    return None
