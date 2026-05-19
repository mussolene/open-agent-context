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
        ROOT / "docs" / "V1_RELEASE_CHECKLIST.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "## EN" in text, path
        assert "## RU" in text, path


def test_readme_separates_draft_and_reference_implementation() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "OACS v1.0" in text
    assert "Standard vs Reference Implementation" in text
    assert "Стандарт и reference implementation" in text
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
    assert f"Current Position: v{__version__} Released / Post-1.0 Hardening" in roadmap
    assert "`acs context gate` is in this reference-adapter\nbucket" in roadmap
    assert "portable field descriptions" in roadmap
    assert "stable-candidate schemas have strict top-level shape" in roadmap
    assert "stable-candidate schemas имеют strict top-level shape" in roadmap
    assert "`actor` and `context_capsule_export` remain draft support" in roadmap
    assert "`actor` и `context_capsule_export` остаются draft support" in roadmap
    assert "Completed freeze-prep work:" in manifest
    assert "Open freeze-prep work:" in manifest
    assert "Add descriptions to schema fields" in manifest
    assert "Добавить descriptions к schema fields" in manifest
    assert "Decide that `actor` and `context_capsule_export` remain `draft_support`" in manifest
    assert "Решить, что `actor` и `context_capsule_export` остаются `draft_support`" in manifest
    assert "Publish `docs/V1_RELEASE_CHECKLIST.md`" in manifest
    assert "Open freeze-prep work:\n\n- None." in manifest


def test_context_gate_docs_keep_standard_boundary_machine_contract() -> None:
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    consumer_packs = (ROOT / "docs" / "CONSUMER_PACKS.md").read_text(encoding="utf-8")
    agent_workflow = (ROOT / "docs" / "AGENT_WORKFLOW.md").read_text(encoding="utf-8")
    spec = (ROOT / "docs" / "SPEC.md").read_text(encoding="utf-8")

    assert (
        "acs context gate --intent <intent> --scope <scope> --task <text> --json"
        in consumer_packs
    )
    assert "Required consumer decision keys" in consumer_packs
    assert "`decision` values are `build` and `skip`" in consumer_packs
    assert "reference_consumer_pack_convenience_not_oacs_standard" in consumer_packs
    assert (
        "does not\nread memory, decrypt local state, or add a portable standard schema"
        in agent_workflow
    )
    assert "not a new portable schema or conformance\nrequirement" in roadmap
    assert "context gate" not in spec.casefold()


def test_draft_support_schema_decisions_stay_outside_v1_stable_surface() -> None:
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")
    compatibility = (ROOT / "docs" / "COMPATIBILITY.md").read_text(encoding="utf-8")
    capsules = (ROOT / "docs" / "CONTEXT_CAPSULES.md").read_text(encoding="utf-8")

    assert "`actor` | `draft_support` | no | no | Keep actor identity records outside" in manifest
    assert (
        "`context_capsule_export` | `draft_support` | no | no | "
        "Keep export integrity envelopes outside"
        in manifest
    )
    assert "identity registry shape is not" in compatibility
    assert "raw\n`ContextCapsule` JSON is the portable record" in compatibility
    assert "not part of the v1.0 stable portable schema set" in capsules


def test_v1_release_checklist_blocks_freeze_release_risks() -> None:
    checklist = (ROOT / "docs" / "V1_RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "FREEZE_PREP.md").read_text(encoding="utf-8")

    for required in (
        "Freeze manifest drift",
        "Stable schema drift",
        "Fixture drift",
        "Compatibility drift",
        "Standard boundary drift",
        "Local gate failure",
        "Published package smoke failure",
        "Secret scan failure",
        "OACS proof gap",
    ):
        assert required in checklist
    assert "python3 -m oacs.cli.main conformance validate --json" in checklist
    assert "acs conformance validate --json" in checklist
    assert " examples " in checklist
    assert "examples/skills" not in checklist
    assert "docs/V1_RELEASE_CHECKLIST.md" in roadmap
    assert "Open freeze-prep work:\n\n- None." in manifest


def test_public_docs_link_consumer_packs_as_adapter_layer() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skills = (ROOT / "docs" / "SKILLS.md").read_text(encoding="utf-8")
    consumer_packs = (ROOT / "docs" / "CONSUMER_PACKS.md").read_text(encoding="utf-8")
    normalized_consumer_packs = " ".join(consumer_packs.split())

    assert "docs/CONSUMER_PACKS.md" in readme
    assert "docs/CONSUMER_PACKS.md" in skills
    assert "not part of the OACS v1.0 standard surface" in normalized_consumer_packs
    assert ".agent/oacs" in consumer_packs


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


def test_codex_oacs_runtime_skill_uses_current_evidence_capability() -> None:
    skill = json.loads(
        (ROOT / "examples" / "skills" / "codex_oacs_runtime" / "skill.json").read_text(
            encoding="utf-8"
        )
    )
    dogfood = (ROOT / "docs" / "DOGFOOD.md").read_text(encoding="utf-8")

    permissions = skill["permissions"]
    assert permissions["evidence.ingest"] is True
    assert "tool.ingest_result" not in permissions
    assert "evidence.ingest" in dogfood
    assert "not separate v1 portable capability\noperations" in dogfood


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


def test_public_docs_do_not_use_stale_draft_name_for_v1() -> None:
    pattern = re.compile(r"OACS v0\.1 draft|draft can change before v1\.0")
    for path in PUBLIC_MARKDOWN:
        assert not pattern.search(path.read_text(encoding="utf-8")), path
