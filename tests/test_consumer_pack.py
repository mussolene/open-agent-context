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


def test_cursor_rule_is_always_on_and_routes_to_global_skills() -> None:
    text = (PACK / "cursor" / "rules" / "oacs-repo-memory.mdc").read_text(
        encoding="utf-8"
    )

    assert "alwaysApply: true" in text
    assert "globally installed" in text
    assert "proof-loop" in text
    assert "acs context build" not in text


def test_root_fragments_select_context_and_protect_private_oacs_state() -> None:
    combined = "\n".join(
        [
            (PACK / "AGENTS.fragment.md").read_text(encoding="utf-8"),
            (PACK / "CLAUDE.fragment.md").read_text(encoding="utf-8"),
        ]
    )

    assert "globally installed `oacs` Skill" in combined
    assert "globally installed `oacs` Skill" in combined
    assert "proof-loop" in combined
    assert "acs context build" not in combined


def test_consumer_pack_does_not_duplicate_global_protocol() -> None:
    surfaces = [
        PACK / "AGENTS.fragment.md",
        PACK / "CLAUDE.fragment.md",
        PACK / "cursor" / "rules" / "oacs-repo-memory.mdc",
        PACK / "cursor" / "skills" / "oacs-repo-memory" / "SKILL.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in surfaces)

    assert "globally installed" in combined
    assert "acs context build" not in combined
    assert "acs tool ingest-result" not in combined
    assert "acs checkpoint add" not in combined


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
