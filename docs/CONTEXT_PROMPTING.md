# Context Prompting / Контекстный prompt rendering

## EN
`ContextCapsule` is the portable OACS data contract. It should not be flattened
into neutral prose before a model sees it. A runtime adapter should render the
capsule as typed governed context so the model can preserve the difference
between facts, hypotheses, tool observations, evidence refs, rules, permissions,
and forbidden assumptions.

This is reference implementation guidance, not a new OACS v1.0 core
requirement. OACS conformance still depends on the portable JSON records and
schemas. Prompt rendering belongs to adapters and runtimes because different
models and products need different prompt surfaces.

### Why It Matters

Long-running agent work can anchor on a repeated idea even when the underlying
memory contract is correct. Small qualitative tests in this repository found
that apparent anchoring can be driven by:

- prompt framing;
- coherent checkpoint rituals;
- stable context ordering;
- repeated semantic directions;
- broad long-horizon tasks that should be sliced into smaller checks.

The practical lesson is simple: do not hand a model a capsule as one coherent
story. Coherent stories are useful for people, but they can make one hypothesis
the cheapest continuation for a model.

### Reference Rendering Rules

A prompt renderer should:

- put D0-D2 facts, preferences, and procedures in a factual support section;
- put D3-D5 patterns, project models, and priors in a separate hypothesis
  section;
- state that D3-D5 may guide attention, ranking, triage, personalization, or
  clarifying questions, but are not factual evidence by themselves;
- show `EvidenceRef` identifiers as provenance, not as factual claims;
- keep tool observations separate from distilled memory;
- surface `forbidden_assumptions` in their own section;
- prefer a falsification ledger for long-horizon diagnostic work;
- avoid ordering hypotheses before facts unless the task explicitly asks for
  hypothesis generation.

### Reference Implementation

Python consumers can use:

```python
from oacs.context.prompt_renderer import render_context_prompt

rendered = render_context_prompt(capsule, memories=memories, mode="falsification_ledger")
print(rendered.prompt)
```

CLI consumers can ask context build to return the reference prompt surface next
to the portable capsule:

```bash
acs context build \
  --intent "answer_project_question" \
  --scope project \
  --render-prompt \
  --prompt-mode falsification_ledger \
  --json
```

The `prompt` and `prompt_rendering` fields are CLI output wrapper fields. They
are not stored inside the `ContextCapsule` and do not expand the OACS core
contract.

For an already exported capsule, use the file renderer:

```bash
acs context render-prompt --file capsule.json --mode answer
```

The command emits reference prompt text. It does not create a new portable OACS
record and is not required for v1.0 conformance.

### Bad Shape

Avoid rendering a capsule as:

```text
The project probably has a context anchoring issue. D3-D5 memory says repeated
hypotheses are risky, evidence refs are available, and the next step is to fix
memory retrieval.
```

That text mixes hypothesis, evidence, and recommendation into one narrative.

### Better Shape

Prefer sections:

```text
## D0-D2 Facts, Preferences, And Procedures
- ...

## D3-D5 Hypotheses And Priors
These items may guide attention. They are not factual evidence by themselves.
- ...

## Evidence Refs And Tool Observations
- ref: ev_...

## Forbidden Assumptions
- Do not treat repeated hypotheses as facts.

## Response Contract
- State how the leading hypothesis could be false.
- End with the smallest next falsification test.
```

## RU
`ContextCapsule` - переносимый OACS data contract. Его не стоит превращать в
нейтральную прозу перед передачей модели. Runtime adapter должен рендерить
capsule как типизированный governed context, чтобы модель сохраняла различие
между facts, hypotheses, tool observations, evidence refs, rules, permissions и
forbidden assumptions.

Это guidance для reference implementation, а не новое требование core OACS
v1.0. Conformance по-прежнему определяется portable JSON records и schemas.
Prompt rendering живёт в adapters/runtimes, потому что разные модели и продукты
требуют разной prompt surface.

### Зачем Это Нужно

Длинная агентная работа может заякориться на повторяемой идее даже при
корректном memory contract. Малые качественные проверки в этом репозитории
показали, что apparent anchoring может создаваться:

- framing запроса;
- coherent checkpoint rituals;
- стабильным порядком контекстных блоков;
- повторяемым семантическим направлением;
- слишком широкой long-horizon задачей, которую нужно резать на маленькие
  проверки.

Практический вывод: не передавайте capsule модели как одну связную историю.
Связная история удобна человеку, но для модели она может сделать одну гипотезу
самым дешёвым продолжением.

### Правила Reference Rendering

Prompt renderer должен:

- помещать D0-D2 facts/preferences/procedures в factual support section;
- помещать D3-D5 patterns/project models/priors в отдельный hypothesis section;
- явно писать, что D3-D5 могут направлять attention/ranking/triage/
  personalization/clarifying questions, но не являются factual evidence сами по
  себе;
- показывать `EvidenceRef` как provenance, а не как factual claims;
- отделять tool observations от distilled memory;
- выводить `forbidden_assumptions` отдельной секцией;
- для long-horizon diagnostics предпочитать falsification ledger;
- не ставить hypotheses перед facts по умолчанию.

### Reference Implementation

Python:

```python
from oacs.context.prompt_renderer import render_context_prompt

rendered = render_context_prompt(capsule, memories=memories, mode="falsification_ledger")
print(rendered.prompt)
```

CLI:

```bash
acs context build \
  --intent "answer_project_question" \
  --scope project \
  --render-prompt \
  --prompt-mode falsification_ledger \
  --json
```

Поля `prompt` и `prompt_rendering` находятся в CLI output wrapper. Они не
записываются внутрь `ContextCapsule` и не расширяют core contract OACS.

Для уже экспортированной capsule используйте file renderer:

```bash
acs context render-prompt --file capsule.json --mode answer
```

Команда выводит reference prompt text. Она не создаёт новый portable OACS record
и не требуется для v1.0 conformance.
