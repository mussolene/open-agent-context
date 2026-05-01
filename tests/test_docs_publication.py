from __future__ import annotations

import json
import re
from pathlib import Path

from oacs import __version__

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MARKDOWN = [
    ROOT / "README.md",
    *(ROOT / "docs").glob("*.md"),
    *(ROOT / "examples").glob("**/*.md"),
]


def test_publication_docs_have_bilingual_sections() -> None:
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "SPEC.md",
        ROOT / "docs" / "GLOSSARY.md",
        ROOT / "docs" / "ROADMAP.md",
        ROOT / "docs" / "COMPATIBILITY.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "## EN" in text, path
        assert "## RU" in text, path


def test_readme_separates_draft_and_reference_implementation() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "OACS v0.1 draft" in text
    assert "Standard Draft vs Reference Implementation" in text
    assert "Draft стандарта и reference implementation" in text
    assert "docs/COMPATIBILITY.md" in text


def test_json_schemas_are_valid_json_objects() -> None:
    for path in (ROOT / "schemas").glob("*.schema.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert payload["type"] == "object"


def test_public_docs_do_not_use_stale_reference_version() -> None:
    major, minor, patch = (int(part) for part in __version__.split("."))
    stale = f"v{major}.{minor}.{patch - 1}" if patch else f"v{major}.{minor - 1}.0"
    for path in PUBLIC_MARKDOWN:
        assert stale not in path.read_text(encoding="utf-8"), path


def test_public_docs_call_standard_a_draft() -> None:
    pattern = re.compile(r"OACS v0\.1(?! draft)")
    for path in PUBLIC_MARKDOWN:
        assert not pattern.search(path.read_text(encoding="utf-8")), path
