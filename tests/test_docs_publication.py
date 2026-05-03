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


def test_freeze_prep_manifest_tracks_schema_and_fixture_coverage() -> None:
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")
    schema_names = sorted(
        path.name.removesuffix(".schema.json") for path in (ROOT / "schemas").glob("*.json")
    )
    fixture_paths = (ROOT / "conformance" / "fixtures").glob("*.json")
    positive_fixtures = {
        path.name.removesuffix(".json") for path in fixture_paths
    }
    negative_schema_refs = {
        str(json.loads(path.read_text(encoding="utf-8")).get("schema", "")).removesuffix(
            ".schema.json"
        )
        for path in (ROOT / "conformance" / "negative").glob("*.json")
    }

    for schema_name in schema_names:
        assert f"| `{schema_name}` |" in manifest

    for fixture_name in positive_fixtures:
        assert f"| `{fixture_name}` | `stable_candidate` | yes |" in manifest

    for schema_name in negative_schema_refs:
        assert f"| `{schema_name}` | `stable_candidate` | yes | yes |" in manifest

    assert "`actor` | `draft_support`" in manifest
    assert "`context_capsule_export` | `draft_support`" in manifest
    assert "`benchmark_task` | `reference_only`" in manifest
    assert "`benchmark_task_pack` | `reference_only`" in manifest


def test_stable_candidate_schemas_reject_additional_properties() -> None:
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")
    stable_candidates = re.findall(r"\| `([^`]+)` \| `stable_candidate` \|", manifest)

    assert stable_candidates
    for schema_name in sorted(set(stable_candidates)):
        payload = json.loads((ROOT / "schemas" / f"{schema_name}.schema.json").read_text())
        assert payload.get("additionalProperties") is False, schema_name


def test_stable_candidate_schema_properties_have_descriptions() -> None:
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")
    stable_candidates = re.findall(r"\| `([^`]+)` \| `stable_candidate` \|", manifest)

    assert stable_candidates
    for schema_name in sorted(set(stable_candidates)):
        payload = json.loads((ROOT / "schemas" / f"{schema_name}.schema.json").read_text())
        properties = payload.get("properties", {})
        assert isinstance(properties, dict), schema_name
        for property_name, property_schema in properties.items():
            assert isinstance(property_schema, dict), f"{schema_name}.{property_name}"
            description = property_schema.get("description")
            assert isinstance(description, str) and description.strip(), (
                f"{schema_name}.{property_name}"
            )


def test_freeze_prep_status_is_current_in_roadmap_and_manifest() -> None:
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")

    assert "stable-candidate schemas reject unknown top-level fields" in roadmap
    assert "portable field descriptions" in roadmap
    assert "stable-candidate schemas have strict top-level shape" in roadmap
    assert "stable-candidate schemas имеют strict top-level shape" in roadmap
    assert "Completed freeze-prep work:" in manifest
    assert "Open freeze-prep work:" in manifest
    assert "Add descriptions to schema fields" in manifest
    assert "Добавить descriptions к schema fields" in manifest


def test_public_docs_do_not_use_stale_reference_version() -> None:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", __version__)
    assert match is not None
    major, minor, patch = (int(part) for part in match.groups())
    stale = f"v{major}.{minor}.{patch - 1}" if patch else f"v{major}.{minor - 1}.0"
    for path in PUBLIC_MARKDOWN:
        if path.name == "ROADMAP.md":
            continue
        assert stale not in path.read_text(encoding="utf-8"), path


def test_quickstart_pypi_uses_current_version() -> None:
    text = (ROOT / "docs" / "QUICKSTART_PYPI.md").read_text(encoding="utf-8")

    assert f"pip install oacs=={__version__}" in text
    assert "pip install oacs==0.3.0a1" not in text


def test_tool_docs_describe_canonical_evidence_projection() -> None:
    text = (ROOT / "docs" / "TOOL_BINDINGS.md").read_text(encoding="utf-8")
    pattern = (
        "external retrieval tool -> tool ingest-result -> EvidenceRef -> "
        "memory sharpen -> context build"
    )

    assert pattern in text
    assert "acs evidence list --kind tool_result --json" in text
    assert "acs evidence inspect <ev_...> --json" in text
    assert "does not enter `ContextCapsule.evidence_refs` by" in text


def test_interoperability_docs_link_conformance_fixtures_and_reference_boundary() -> None:
    interoperability = (ROOT / "docs" / "INTEROPERABILITY.md").read_text(encoding="utf-8")
    conformance = (ROOT / "conformance" / "README.md").read_text(encoding="utf-8")
    spec = (ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")

    assert "conformance/fixtures/" in interoperability
    assert "not Python object snapshots" in conformance
    assert "not the only OACS transport" in (ROOT / "docs" / "API.md").read_text(
        encoding="utf-8"
    )
    assert "Python-specific behavior is reference-only" in spec
    assert "docs/INTEROPERABILITY.md" in spec
    assert "storage_selector.schema.json" in (
        ROOT / "docs" / "MEMORY_MODEL.md"
    ).read_text(encoding="utf-8")


def test_agent_instructions_use_oacs_native_proof_loop() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "OACS Repo Development Workflow" in text
    assert "acs tool ingest-result" in text
    assert "acs evidence inspect <ev_...>" in text
    assert ".agent/tasks" not in text


def test_public_docs_call_standard_a_draft() -> None:
    pattern = re.compile(r"OACS v0\.1(?! draft)")
    for path in PUBLIC_MARKDOWN:
        assert not pattern.search(path.read_text(encoding="utf-8")), path
