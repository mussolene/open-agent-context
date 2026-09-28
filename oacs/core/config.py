from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OacsConfig:
    db_path: Path
    base_dir: Path
    passphrase: str | None = None
    encryption: str | None = None

    @classmethod
    def from_values(cls, db: str | None = None, passphrase: str | None = None) -> OacsConfig:
        db_value = resolve_db_selector(
            db or os.getenv("OACS_DB") or discover_project_db() or "./.oacs/oacs.db"
        )
        db_path = Path(db_value).expanduser()
        return cls(
            db_path=db_path,
            base_dir=db_path.parent,
            passphrase=passphrase or os.getenv("OACS_PASSPHRASE"),
            encryption=os.getenv("OACS_ENCRYPTION"),
        )

    @property
    def key_file(self) -> Path:
        return self.base_dir / "key.json"

    @property
    def unlocked_file(self) -> Path:
        return self.base_dir / "unlocked.key"


def discover_project_db(start: Path | None = None) -> str | None:
    current = (start or Path.cwd()).resolve()
    project_root = discover_project_root(current)
    for folder in (current, *current.parents):
        for candidate in (
            folder / ".agent" / "oacs" / "oacs.db",
            folder / ".oacs" / "oacs.db",
        ):
            if candidate.exists():
                return str(candidate)
        if folder == project_root:
            break
    return None


def project_db_path(start: Path | None = None) -> Path:
    discovered = discover_project_db(start)
    if discovered:
        return Path(discovered)
    root = discover_project_root(start) or (start or Path.cwd()).resolve()
    return root / ".agent" / "oacs" / "oacs.db"


def discover_project_root(start: Path | None = None) -> Path | None:
    current = (start or Path.cwd()).resolve()
    for folder in (current, *current.parents):
        if (folder / ".git").exists():
            return folder
    return None


def global_db_path() -> Path:
    explicit = os.getenv("OACS_GLOBAL_DB")
    if explicit:
        return Path(explicit).expanduser()
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.getenv("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.getenv("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return base / "oacs" / "global" / "oacs.db"


def resolve_db_selector(value: str) -> str:
    if value == "@global":
        return str(global_db_path())
    if value == "@project":
        return str(project_db_path())
    return value
