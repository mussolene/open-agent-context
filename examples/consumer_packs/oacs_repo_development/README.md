# OACS Repo Development Consumer Pack

This pack projects one OACS-backed repository workflow into Codex, Claude, and
Cursor surfaces. It is a local adapter pack, not part of the OACS standard.

Install into a target repository:

```bash
python3 examples/consumer_packs/oacs_repo_development/scripts/install.py \
  --target /path/to/repo \
  --agents \
  --claude \
  --cursor \
  --dry-run
```

Remove `--dry-run` after reviewing the target paths.

The pack does not create `.agent/oacs`, `.oacs`, keys, passphrases, or
databases. Initialize those explicitly in the target repository when local
memory is wanted. For local development, `acs key init --json` creates
`local_unlocked` key material by default. Passphrase-wrapped stores remain
supported when a repository already uses `OACS_PASSPHRASE`.

The pack teaches direct OACS context usage for substantial repository work.
Agents build context before implementation, then record command evidence,
verification, leak/secret review, and checkpoints.

Local OACS key material is private runtime state. Agents must not read, print,
or commit `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`, databases,
passphrases, `.agent/oacs`, `.oacs`, or private agent state.

## Included Surfaces

- `AGENTS.fragment.md`: append to or use as a root `AGENTS.md` section.
- `CLAUDE.fragment.md`: append to or use as a root `CLAUDE.md` section.
- `.cursor/rules/oacs-repo-memory.mdc`: always-on Cursor rule.
- `.cursor/skills/oacs-repo-memory/SKILL.md`: Cursor skill for substantial
  repo work.
