from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "examples" / "consumer_packs" / "oacs_repo_development"


def test_oacs_consumer_pack_surfaces_exist() -> None:
    assert (PACK / "AGENTS.fragment.md").is_file()
    assert (PACK / "CLAUDE.fragment.md").is_file()
    assert (PACK / "cursor" / "rules" / "oacs-repo-memory.mdc").is_file()
    assert (PACK / "cursor" / "skills" / "oacs-repo-memory" / "SKILL.md").is_file()


def test_cursor_rule_is_always_on_and_preserves_oacs_boundaries() -> None:
    text = (PACK / "cursor" / "rules" / "oacs-repo-memory.mdc").read_text(
        encoding="utf-8"
    )

    assert "alwaysApply: true" in text
    assert "OACS does not orchestrate tools" in text
    assert "Do not prepend OACS context unconditionally" in text
    assert "acs context gate" in text
    assert "Standalone tool-result evidence does not enter" in text
    assert "Preserve attribution" in text
    assert ".agent/oacs/unlocked.key" in text


def test_root_fragments_select_context_and_protect_private_oacs_state() -> None:
    combined = "\n".join(
        [
            (PACK / "AGENTS.fragment.md").read_text(encoding="utf-8"),
            (PACK / "CLAUDE.fragment.md").read_text(encoding="utf-8"),
        ]
    )

    assert "Ask the reference context gate" in combined
    assert "acs context gate" in combined
    assert "decision=build" in combined
    assert "decision=skip" in combined
    assert "Do not prepend OACS context unconditionally" in combined
    assert "Do not read, print, or commit `.agent/oacs/key.json`" in combined
    assert ".agent/oacs/unlocked.key" in combined
    assert "OACS is not the tool orchestrator" in combined
    assert "acs checkpoint add" in combined


def test_consumer_pack_installer_dry_run(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    target.mkdir()
    (target / ".git").mkdir()

    result = subprocess.run(
        [
            "python3",
            str(PACK / "scripts" / "install.py"),
            "--target",
            str(target),
            "--cursor",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "would write" in result.stdout
    assert not (target / ".cursor").exists()
