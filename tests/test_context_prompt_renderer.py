from __future__ import annotations

import json

from typer.testing import CliRunner

from oacs.cli.main import app
from oacs.context.capsule import ContextCapsule
from oacs.context.prompt_renderer import render_context_prompt
from oacs.memory.models import MemoryContent, MemoryRecord


def test_context_prompt_renderer_preserves_epistemic_roles() -> None:
    capsule = ContextCapsule(
        purpose="diagnose repeated answers",
        scope=["project"],
        included_rules=["rule_fuzzy_memory_not_fact"],
        included_tools=["tool_search"],
        evidence_refs=["ev_tool_result"],
        forbidden_assumptions=["Do not treat repeated hypotheses as facts"],
        permissions={"memory.query": True, "memory.commit": False},
    ).seal()
    fact = MemoryRecord(
        id="mem_fact",
        memory_type="fact",
        depth=2,
        content=MemoryContent(text="Builds use pytest.", kind="fact"),
        evidence_refs=["ev_fact"],
    )
    hypothesis = MemoryRecord(
        id="mem_hypothesis",
        memory_type="pattern",
        depth=4,
        content=MemoryContent(text="The task may be anchored by checkpoint phrasing."),
        evidence_refs=[],
    )

    rendered = render_context_prompt(
        capsule,
        task="Why are answers repetitive?",
        memories=[hypothesis, fact],
        evidence=[
            {
                "id": "ev_tool_result",
                "kind": "tool_result",
                "public_payload": {"output": {}},
            }
        ],
    )

    prompt = rendered.prompt
    assert "## D0-D2 Facts, Preferences, And Procedures" in prompt
    assert "- mem_fact D2 fact: Builds use pytest." in prompt
    assert "## D3-D5 Hypotheses And Priors" in prompt
    assert "They are not factual evidence by themselves." in prompt
    assert "- mem_hypothesis D4 pattern:" in prompt
    assert "## Forbidden Assumptions" in prompt
    assert "- Do not treat repeated hypotheses as facts" in prompt
    assert "Do not convert a raw tool result or an evidence ref identifier" in prompt
    assert "ref: ev_tool_result" in prompt


def test_context_prompt_renderer_falsification_mode_changes_response_contract() -> None:
    capsule = ContextCapsule(purpose="debug loop", scope=["project"]).seal()

    rendered = render_context_prompt(capsule, mode="falsification_ledger")

    assert rendered.mode == "falsification_ledger"
    assert (
        "State the leading hypothesis only after naming how it could be false."
        in rendered.prompt
    )
    assert "End with the smallest next falsification test." in rendered.prompt


def test_context_prompt_renderer_marks_missing_and_unlinked_evidence() -> None:
    capsule = ContextCapsule(
        purpose="check evidence boundaries",
        evidence_refs=["ev_pass", "ev_missing"],
    ).seal()
    fact = MemoryRecord(
        id="mem_with_evidence",
        memory_type="fact",
        depth=2,
        content=MemoryContent(text="Alpha fact."),
        evidence_refs=["ev_pass"],
    )

    rendered = render_context_prompt(
        capsule,
        memories=[fact],
        evidence=[
            {
                "id": "ev_pass",
                "kind": "tool_result",
                "status": "active",
                "public_payload": {
                    "tool_id": "test_tool",
                    "attribution": {
                        "role": "tool_observation",
                        "source_actor_id": "test_tool",
                    },
                    "output": {"claim": "Alpha fact."},
                },
            },
            {
                "id": "ev_unlinked",
                "kind": "tool_result",
                "status": "active",
                "public_payload": {
                    "tool_id": "other_tool",
                    "attribution": {
                        "role": "tool_observation",
                        "source_actor_id": "other_tool",
                    },
                    "output": {"claim": "Unlinked observation."},
                },
            },
        ],
    )

    prompt = rendered.prompt
    assert "mem_with_evidence D2 fact: Alpha fact. (evidence_refs: ev_pass)" in prompt
    assert "ref: ev_pass status=supplied" in prompt
    assert "ref: ev_missing status=missing_from_renderer_input" in prompt
    assert (
        "observation: ev_pass link=capsule_ref kind=tool_result status=active "
        "tool_id=test_tool role=tool_observation source=test_tool output_keys=['claim']"
        in prompt
    )
    assert "observation: ev_unlinked link=unlinked_observation" in prompt


def test_cli_context_render_prompt_from_capsule_file(tmp_path) -> None:
    capsule = ContextCapsule(
        purpose="manual render",
        forbidden_assumptions=["D3-D5 memory is not factual evidence"],
    ).seal()
    file = tmp_path / "capsule.json"
    file.write_text(capsule.model_dump_json(), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "context",
            "render-prompt",
            "--file",
            str(file),
            "--task",
            "Render this capsule.",
            "--mode",
            "falsification_ledger",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["mode"] == "falsification_ledger"
    assert payload["standard_boundary"] == "reference_rendering_not_oacs_conformance_record"
    assert "## Adapter Boundary" in payload["prompt"]
    assert "Render this capsule." in payload["prompt"]
    assert "D3-D5 memory is not factual evidence" in payload["prompt"]


def test_cli_context_build_can_render_prompt_without_changing_capsule(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    proposed = runner.invoke(
        app,
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--type",
            "procedure",
            "--depth",
            "2",
            "--text",
            "Context prompt tests use role-preserving sections.",
            "--scope",
            "project",
            "--json",
        ],
    )
    assert proposed.exit_code == 0, proposed.output
    memory_id = json.loads(proposed.output)["id"]
    committed = runner.invoke(
        app, ["memory", "commit", memory_id, "--db", str(db), "--json"]
    )
    assert committed.exit_code == 0, committed.output

    result = runner.invoke(
        app,
        [
            "context",
            "build",
            "--db",
            str(db),
            "--intent",
            "answer_project_question",
            "--query",
            "Context prompt tests",
            "--scope",
            "project",
            "--render-prompt",
            "--prompt-mode",
            "falsification_ledger",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert "capsule" in payload
    assert "prompt" in payload
    assert "prompt" not in payload["capsule"]
    assert payload["prompt_rendering"]["mode"] == "falsification_ledger"
    assert (
        payload["prompt_rendering"]["standard_boundary"]
        == "reference_rendering_not_oacs_conformance_record"
    )
    assert "Context prompt tests use role-preserving sections." in payload["prompt"]
    assert "State the leading hypothesis only after naming how it could be false." in (
        payload["prompt"]
    )
