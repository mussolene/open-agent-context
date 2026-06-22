from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from oacs.context.capsule import ContextCapsule
from oacs.memory.models import MemoryRecord

PromptRenderMode = Literal["answer", "falsification_ledger"]


@dataclass(frozen=True)
class RenderedContextPrompt:
    prompt: str
    mode: PromptRenderMode
    sections: list[str]


def render_context_prompt(
    capsule: ContextCapsule,
    *,
    task: str | None = None,
    memories: Sequence[MemoryRecord] | None = None,
    evidence: Sequence[Mapping[str, object]] | None = None,
    mode: PromptRenderMode = "answer",
) -> RenderedContextPrompt:
    """Render a ContextCapsule as typed model input.

    This is reference adapter behavior, not a portable OACS schema requirement.
    The renderer keeps epistemic roles visible on the prompt surface so a model
    does not receive facts, hypotheses, tool observations, and constraints as
    one flattened narrative.
    """

    facts = [memory for memory in memories or [] if memory.depth <= 2]
    hypotheses = [memory for memory in memories or [] if memory.depth >= 3]
    sections = [
        "adapter_boundary",
        "task",
        "capsule",
        "facts",
        "hypotheses",
        "evidence",
        "rules_and_tools",
        "permissions",
        "forbidden_assumptions",
        "open_questions",
        "response_contract",
    ]
    lines = [
        "# OACS Context Prompt",
        "",
        "## Adapter Boundary",
        "This prompt is a reference rendering of a ContextCapsule. It is not an OACS "
        "v1.0 conformance record and must not be treated as a new standard schema.",
        "",
        "## Task",
        task or capsule.purpose,
        "",
        "## Capsule Identity",
        f"- capsule_id: {capsule.id}",
        f"- purpose: {capsule.purpose}",
        f"- scope: {_format_list(capsule.scope)}",
        f"- token_budget: {capsule.token_budget}",
        "",
        "## D0-D2 Facts, Preferences, And Procedures",
        *_format_memories(facts, empty="- none"),
        "",
        "## D3-D5 Hypotheses And Priors",
        "These items may guide attention, ranking, triage, personalization, or "
        "clarifying questions. They are not factual evidence by themselves.",
        *_format_memories(hypotheses, empty="- none"),
        "",
        "## Evidence Refs And Tool Observations",
        "Evidence refs support provenance. Do not convert a raw tool result or an "
        "evidence ref identifier into a factual claim unless a fact/procedure record "
        "or the task input states that claim.",
        *_format_evidence_refs(capsule.evidence_refs, evidence or []),
        "",
        "## Included Rules, Skills, And Tools",
        f"- rules: {_format_list(capsule.included_rules)}",
        f"- skills: {_format_list(capsule.included_skills)}",
        f"- tools: {_format_list(capsule.included_tools)}",
        "",
        "## Permissions",
        *_format_mapping(capsule.permissions),
        "",
        "## Forbidden Assumptions",
        *_format_list_lines(capsule.forbidden_assumptions, empty="- none"),
        "",
        "## Open Questions",
        "- Ask for missing D0-D2 facts before making factual claims.",
        "- Prefer a falsification test when several causal stories fit the context.",
        "",
        "## Response Contract",
        *_response_contract(mode),
    ]
    return RenderedContextPrompt(
        prompt="\n".join(lines).rstrip() + "\n",
        mode=mode,
        sections=sections,
    )


def _format_memories(memories: Sequence[MemoryRecord], *, empty: str) -> list[str]:
    if not memories:
        return [empty]
    lines: list[str] = []
    for memory in sorted(memories, key=lambda item: (item.depth, item.id)):
        evidence_refs = _format_list(memory.evidence_refs)
        lines.append(
            f"- {memory.id} D{memory.depth} {memory.memory_type}: "
            f"{memory.content.text} (evidence_refs: {evidence_refs})"
        )
    return lines


def _format_evidence_refs(
    refs: Sequence[str], evidence: Sequence[Mapping[str, object]]
) -> list[str]:
    if not refs and not evidence:
        return ["- none"]
    supplied = {str(item.get("id")): item for item in evidence if item.get("id") is not None}
    ref_set = set(refs)
    lines: list[str] = []
    for ref in refs:
        if ref in supplied:
            lines.append(f"- ref: {ref} status=supplied")
        else:
            lines.append(f"- ref: {ref} status=missing_from_renderer_input")
    for item in evidence:
        evidence_id = item.get("id", "<unknown>")
        kind = item.get("kind", "<unknown>")
        status = item.get("status", "<unknown>")
        link_status = "capsule_ref" if evidence_id in ref_set else "unlinked_observation"
        payload = item.get("public_payload")
        summary = ""
        if isinstance(payload, Mapping):
            tool_id = payload.get("tool_id", "<unknown>")
            attribution = payload.get("attribution")
            role = "<unknown>"
            source = "<unknown>"
            if isinstance(attribution, Mapping):
                role = str(attribution.get("role", "<unknown>"))
                source = str(attribution.get("source_actor_id", "<unknown>"))
            output = payload.get("output")
            if isinstance(output, Mapping):
                summary = f" output_keys={sorted(str(key) for key in output)}"
            summary = f" tool_id={tool_id} role={role} source={source}{summary}"
        lines.append(
            f"- observation: {evidence_id} link={link_status} kind={kind} "
            f"status={status}{summary}"
        )
    return lines


def _format_mapping(mapping: Mapping[str, bool]) -> list[str]:
    if not mapping:
        return ["- none"]
    return [f"- {key}: {value}" for key, value in sorted(mapping.items())]


def _format_list(items: Sequence[str]) -> str:
    return ", ".join(items) if items else "none"


def _format_list_lines(items: Sequence[str], *, empty: str) -> list[str]:
    if not items:
        return [empty]
    return [f"- {item}" for item in items]


def _response_contract(mode: PromptRenderMode) -> list[str]:
    if mode == "falsification_ledger":
        return [
            "- Separate facts from hypotheses.",
            "- State the leading hypothesis only after naming how it could be false.",
            "- Include at least one alternative causal class.",
            "- End with the smallest next falsification test.",
        ]
    return [
        "- Use D0-D2 and evidence-backed records for factual claims.",
        "- Treat D3-D5 as hypotheses only.",
        "- Name missing facts instead of filling them with plausible narrative.",
        "- Do not let repeated context ordering make one hypothesis the default answer.",
    ]
