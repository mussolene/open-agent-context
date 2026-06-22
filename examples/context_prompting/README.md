# Context Prompting Example / Пример Context Prompting

## EN
This example shows why a `ContextCapsule` should be rendered as typed governed
context instead of neutral prose.

Bad rendering turns several epistemic roles into one narrative:

```text
The project has a context anchoring issue. D3-D5 memory says repeated hypotheses
are risky, evidence refs are present, and the next step is to fix retrieval.
```

Good rendering keeps roles separate:

```text
## D0-D2 Facts, Preferences, And Procedures
- mem_fact D2 procedure: Context build is required before substantial repo work.

## D3-D5 Hypotheses And Priors
These items may guide attention, ranking, triage, personalization, or clarifying
questions. They are not factual evidence by themselves.
- mem_pattern D4 pattern: Long tasks may become anchored by repeated framing.

## Evidence Refs And Tool Observations
- ref: ev_anchor_tests

## Forbidden Assumptions
- Do not treat repeated hypotheses as facts.

## Response Contract
- State how the leading hypothesis could be false.
- End with the smallest next falsification test.
```

Ask context build to return the reference prompt beside the portable capsule:

```bash
acs context build \
  --intent "answer_project_question" \
  --scope project \
  --render-prompt \
  --prompt-mode falsification_ledger \
  --json
```

The prompt is wrapper output, not a field inside `ContextCapsule`. For already
exported capsules, use `acs context render-prompt --file capsule.json`.

This is reference adapter behavior, not an OACS v1.0 conformance requirement.

## RU
Этот пример показывает, почему `ContextCapsule` нужно рендерить как
типизированный governed context, а не как нейтральную прозу.

Плохой rendering смешивает разные эпистемические роли в один narrative:

```text
В проекте есть проблема context anchoring. D3-D5 memory говорит, что повторяемые
гипотезы рискованны, evidence refs есть, следующий шаг - чинить retrieval.
```

Хороший rendering разделяет роли:

```text
## D0-D2 Facts, Preferences, And Procedures
- mem_fact D2 procedure: Context build is required before substantial repo work.

## D3-D5 Hypotheses And Priors
These items may guide attention, ranking, triage, personalization, or clarifying
questions. They are not factual evidence by themselves.
- mem_pattern D4 pattern: Long tasks may become anchored by repeated framing.

## Evidence Refs And Tool Observations
- ref: ev_anchor_tests

## Forbidden Assumptions
- Do not treat repeated hypotheses as facts.

## Response Contract
- State how the leading hypothesis could be false.
- End with the smallest next falsification test.
```

Reference renderer:

```bash
acs context build \
  --intent "answer_project_question" \
  --scope project \
  --render-prompt \
  --prompt-mode falsification_ledger \
  --json
```

Prompt находится в wrapper output, а не внутри `ContextCapsule`. Для уже
exported capsules используйте `acs context render-prompt --file capsule.json`.

Это behavior reference adapter, а не требование OACS v1.0 conformance.
