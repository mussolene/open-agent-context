# OACS Repo Development Consumer Pack

This deprecated compatibility pack contains only repository-local opt-in shims.
New installations should use the supported global integrations:

```bash
acs integrations codex install
acs integrations codex doctor
acs integrations claude install
acs integrations claude doctor
acs integrations cursor install
acs integrations cursor doctor
```

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

The operating protocol lives only in the packaged global `oacs` and
`proof-loop` Skills. This pack does not copy that protocol.

Local OACS key material is private runtime state. Agents must not read, print,
or commit `.agent/oacs/key.json`, `.agent/oacs/unlocked.key`, databases,
passphrases, `.agent/oacs`, `.oacs`, or private agent state.

## Included Surfaces

- `AGENTS.fragment.md`: minimal project opt-in policy only. The Codex operating
  protocol lives in the global `oacs` Skill.
- `CLAUDE.fragment.md`: minimal repository opt-in policy.
- `.cursor/rules/oacs-repo-memory.mdc`: minimal repository opt-in policy.
- `.cursor/skills/oacs-repo-memory/SKILL.md`: deprecated routing shim.
