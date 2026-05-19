from __future__ import annotations

import argparse
import shutil
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install the OACS repo development consumer pack into a local repository."
    )
    parser.add_argument("--target", required=True, type=Path, help="Target repository root.")
    parser.add_argument("--agents", action="store_true", help="Install AGENTS.md fragment.")
    parser.add_argument("--claude", action="store_true", help="Install CLAUDE.md fragment.")
    parser.add_argument("--cursor", action="store_true", help="Install Cursor rule and skill.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print writes without changing files.",
    )
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.exists() or not target.is_dir():
        raise SystemExit(f"target directory does not exist: {target}")
    if not any((target / marker).exists() for marker in (".git", "pyproject.toml", "package.json")):
        raise SystemExit(f"target does not look like a repository root: {target}")

    selected = args.agents or args.claude or args.cursor
    install_agents = args.agents or not selected
    install_claude = args.claude or not selected
    install_cursor = args.cursor or not selected

    writes: list[tuple[Path, Path]] = []
    if install_agents:
        writes.append((PACK_ROOT / "AGENTS.fragment.md", target / "AGENTS.md"))
    if install_claude:
        writes.append((PACK_ROOT / "CLAUDE.fragment.md", target / "CLAUDE.md"))
    if install_cursor:
        writes.append(
            (
                PACK_ROOT / "cursor" / "rules" / "oacs-repo-memory.mdc",
                target / ".cursor" / "rules" / "oacs-repo-memory.mdc",
            )
        )
        writes.append(
            (
                PACK_ROOT / "cursor" / "skills" / "oacs-repo-memory" / "SKILL.md",
                target / ".cursor" / "skills" / "oacs-repo-memory" / "SKILL.md",
            )
        )

    for src, dst in writes:
        print(f"{'would write' if args.dry_run else 'write'} {dst}")
        if args.dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            updated = _append_or_replace(dst.read_text(encoding="utf-8"), src)
            dst.write_text(updated, encoding="utf-8")
        else:
            shutil.copyfile(src, dst)


def _append_or_replace(existing: str, src: Path) -> str:
    block = src.read_text(encoding="utf-8").strip() + "\n"
    marker = "## OACS / ACS Repository Workflow"
    if marker not in block:
        return block
    start = existing.find(marker)
    if start == -1:
        return existing.rstrip() + "\n\n" + block
    next_section = existing.find("\n## ", start + len(marker))
    if next_section == -1:
        return existing[:start].rstrip() + "\n\n" + block
    return existing[:start].rstrip() + "\n\n" + block + "\n" + existing[next_section:].lstrip()


if __name__ == "__main__":
    main()
