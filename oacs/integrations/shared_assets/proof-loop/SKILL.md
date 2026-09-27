---
name: proof-loop
description: Use for substantial repository features, refactors, bug fixes, migrations, and releases that need explicit acceptance criteria, the smallest safe implementation, current evidence, fresh verification, and a bounded fix loop. Use OACS as the durable state and evidence layer when the OACS integration is available.
metadata:
  short-description: Evidence-backed repository delivery loop
---

# Proof Loop

Use this Skill when completion needs to be demonstrated, not merely asserted. It is
domain-neutral and works above repository-specific tools and Skills.

The loop is:

1. freeze scope and acceptance criteria;
2. build the smallest safe change;
3. collect current evidence;
4. verify independently against current state;
5. fix only confirmed gaps and verify again.

Read `references/protocol.md` before running the loop.

## Relationship to OACS

When the installed `oacs` Skill is available, use it as the only durable task-state,
evidence, and checkpoint layer. Do not create `.agent/tasks/`, a second memory database,
or parallel proof files merely to run this Skill.

Historical OACS memory is orientation and evidence, not proof that the current code
passes. A fresh verifier must inspect current files and current command results. Current
explicit user instructions override every earlier specification, checkpoint, or memory.

## Relationship to Domain Skills

Use the repository's own checks and the relevant domain Skill to choose the cheapest
sufficient proof. This Skill owns the delivery loop, not domain semantics. For example,
1C work can use `onec-context`, BSL checks, xUnitFor1C, or Vanessa Automation without
making those tools part of the generic protocol.

## Agent Roles

The loop can run in one agent. When the user has authorized delegation and the runtime
provides matching roles, use:

- `task-spec-freezer` for scope and acceptance criteria;
- `task-builder` for implementation and implementation evidence;
- `task-verifier` for a fresh read-only verdict;
- `task-fixer` only for verifier-confirmed gaps.

Pass compact scope, acceptance criteria, relevant OACS context, and evidence references.
Do not pass full chat history or unrelated memory. The parent agent owns final integration
and must inspect delegated results before claiming completion.

Never claim completion unless every acceptance criterion is `PASS`. Use `UNKNOWN` when
the required environment or authority is unavailable.
