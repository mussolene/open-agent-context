from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
