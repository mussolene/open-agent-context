from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_REPORT = ROOT / "examples" / "benchmarks" / "full_context_gemma_e2b_2026-05-02.md"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the OACS governed memory/context killer demo."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / ".oacs" / "killer-demo",
        help="Directory for raw demo artifacts.",
    )
    parser.add_argument(
        "--passphrase",
        default="oacs-local-killer-demo-passphrase",
        help="Local demo passphrase for the throwaway encrypted store.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the output directory if it already exists.",
    )
    args = parser.parse_args()

    out_dir = args.out.expanduser().resolve()
    if out_dir.exists():
        if not args.force:
            raise SystemExit(f"{out_dir} exists; pass --force to replace it")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    db = out_dir / "oacs.db"
    env = os.environ.copy()
    env["OACS_PASSPHRASE"] = args.passphrase
    commands: list[dict[str, Any]] = []

    def run_cli(name: str, cli_args: list[str]) -> Any:
        command = [sys.executable, "-m", "oacs.cli.main", *cli_args, "--json"]
        proc = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        record = {
            "name": name,
            "command": command,
            "returncode": proc.returncode,
            "stdout_file": f"{name}.json",
            "stderr": proc.stderr,
        }
        commands.append(record)
        if proc.returncode != 0:
            (out_dir / f"{name}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
            raise SystemExit(f"{name} failed with exit code {proc.returncode}: {proc.stderr}")
        payload = json.loads(proc.stdout)
        write_json(out_dir / f"{name}.json", payload)
        return payload

    run_cli("01_init", ["init", "--db", str(db)])
    run_cli("02_key_init", ["key", "init", "--db", str(db), "--passphrase", args.passphrase])
    actor = run_cli(
        "03_actor_create",
        ["actor", "create", "--db", str(db), "--type", "human", "--name", "Demo User"],
    )
    actor_id = actor["id"]

    memory_text = (
        "For project Atlas, release evidence must be gathered with acs audit verify, "
        "context export, and the full-context benchmark report before public claims."
    )
    proposed = run_cli(
        "04_memory_propose",
        [
            "memory",
            "propose",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--scope",
            "project:atlas",
            "--type",
            "procedure",
            "--depth",
            "2",
            "--text",
            memory_text,
        ],
    )
    memory_id = proposed["id"]
    run_cli(
        "05_memory_commit",
        ["memory", "commit", memory_id, "--db", str(db), "--actor", actor_id],
    )
    memory_query = run_cli(
        "06_memory_query",
        [
            "memory",
            "query",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--scope",
            "project:atlas",
            "--query",
            "Atlas release evidence",
        ],
    )

    capsule = run_cli(
        "07_context_build",
        [
            "context",
            "build",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--scope",
            "project:atlas",
            "--intent",
            "Atlas release evidence before public claims",
            "--budget",
            "1600",
        ],
    )
    capsule_id = capsule["id"]
    exported = run_cli(
        "08_context_export",
        ["context", "export", capsule_id, "--db", str(db), "--actor", actor_id],
    )
    export_file = out_dir / "08_context_export.json"
    validation = run_cli(
        "09_context_validate",
        ["context", "validate", "--db", str(db), "--file", str(export_file)],
    )
    loop_run = run_cli(
        "10_loop_run",
        [
            "loop",
            "run",
            "--db",
            str(db),
            "--actor",
            actor_id,
            "--scope",
            "project:atlas",
            "--request",
            "What evidence is required before making public Atlas release claims?",
            "--budget",
            "1600",
        ],
    )

    mcp_config = {
        "mcpServers": {
            "demo-evidence-vault": {
                "command": "demo-evidence-vault",
                "args": ["--stdio"],
                "allowed_tools": ["fetch_release_evidence"],
                "namespace": "release",
                "scope": ["project:atlas"],
            }
        }
    }
    write_json(out_dir / "11_mcp_config.json", mcp_config)
    mcp_import = run_cli(
        "12_mcp_import",
        ["mcp", "import", str(out_dir / "11_mcp_config.json"), "--db", str(db)],
    )
    mcp_list = run_cli("13_mcp_list", ["mcp", "list", "--db", str(db)])
    audit_verify = run_cli("14_audit_verify", ["audit", "verify", "--db", str(db)])

    benchmark = read_benchmark_summary()
    api_artifacts = write_api_shaped_artifacts(out_dir, actor_id, capsule, exported, loop_run)
    summary = {
        "demo": "oacs_governed_context_killer_demo",
        "status": "PASS" if audit_verify["valid"] and validation["valid"] else "FAIL",
        "product_story": [
            "OACS is a draft contract for governed agent memory and context.",
            (
                "OACS builds portable Context Capsules from scoped memory, rules, "
                "tools, skills, evidence, and permissions."
            ),
            (
                "OACS keeps MCP/tool execution at adapter boundaries; imported MCP "
                "metadata does not expand the core standard."
            ),
            (
                "OACS is not an agent framework, model backend, vector database, "
                "benchmark harness, or MCP replacement."
            ),
        ],
        "raw_artifacts_dir": str(out_dir),
        "key_artifacts": {
            "memory_query": "06_memory_query.json",
            "context_capsule": "07_context_build.json",
            "context_export": "08_context_export.json",
            "context_validation": "09_context_validate.json",
            "loop_memory_calls": "10_loop_run.json",
            "mcp_adapter_metadata": "12_mcp_import.json",
            "audit_verification": "14_audit_verify.json",
            "api_shaped": api_artifacts,
        },
        "proof_points": {
            "memory_id": memory_id,
            "memory_query_hits": len(memory_query),
            "capsule_id": capsule_id,
            "capsule_memory_refs": len(capsule.get("included_memories", [])),
            "export_type": exported.get("export_type"),
            "context_validation": validation,
            "memory_calls": len(loop_run.get("memory_calls", [])),
            "mcp_bindings_imported": len(mcp_import),
            "mcp_bindings_listed": len(mcp_list),
            "audit": audit_verify,
        },
        "benchmark_comparison": benchmark,
    }
    write_json(out_dir / "summary.json", summary)
    write_json(out_dir / "commands.json", commands)
    write_markdown_summary(out_dir / "SUMMARY.md", summary)

    print(f"Demo complete: {out_dir}")
    print(f"Summary: {out_dir / 'SUMMARY.md'}")
    return 0


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def write_api_shaped_artifacts(
    out_dir: Path,
    actor_id: str,
    capsule: dict[str, Any],
    exported: dict[str, Any],
    loop_run: dict[str, Any],
) -> list[str]:
    artifacts = {
        "api_context_build.json": {
            "method": "POST",
            "path": "/v1/context/build",
            "request": {
                "actor_id": actor_id,
                "intent": "Atlas release evidence before public claims",
                "scope": ["project:atlas"],
                "token_budget": 1600,
            },
            "response_shape": capsule,
        },
        "api_context_export.json": {
            "method": "POST",
            "path": f"/v1/context/{capsule['id']}/export",
            "request": {"actor_id": actor_id},
            "response_shape": exported,
        },
        "api_loop_run.json": {
            "method": "POST",
            "path": "/v1/loop/run",
            "request": {
                "actor_id": actor_id,
                "scope": ["project:atlas"],
                "token_budget": 1600,
                "user_request": (
                    "What evidence is required before making public Atlas release claims?"
                ),
            },
            "response_shape": loop_run,
        },
    }
    for name, payload in artifacts.items():
        write_json(out_dir / name, payload)
    return sorted(artifacts)


def read_benchmark_summary() -> dict[str, Any]:
    text = BENCHMARK_REPORT.read_text(encoding="utf-8")
    aggregate_line = next(
        line for line in text.splitlines() if line.startswith("| Aggregate | 20 |")
    )
    return {
        "source": str(BENCHMARK_REPORT.relative_to(ROOT)),
        "aggregate_line": aggregate_line,
        "score_per_1k_tokens": {
            "baseline_no_memory": 1.9352,
            "baseline_full_context": 1.7534,
            "oacs_memory_call_loop": 4.3640,
        },
        "interpretation": (
            "On the checked-in 2026-05-02 LM Studio report, OACS memory calls solved "
            "20/20 memory-critical tasks with 22,915 tokens, while raw full context "
            "solved 17/20 with 51,898 tokens."
        ),
    }


def write_markdown_summary(path: Path, summary: dict[str, Any]) -> None:
    proof = summary["proof_points"]
    benchmark = summary["benchmark_comparison"]
    content = f"""# OACS Killer Demo Summary

Status: {summary["status"]}

This demo shows OACS as a draft contract for governed agent memory and context,
not as an agent framework, model backend, vector database, benchmark harness, or
MCP replacement.

## Proof Points

- Memory query hits: {proof["memory_query_hits"]}
- Context Capsule: `{proof["capsule_id"]}`
- Capsule memory refs: {proof["capsule_memory_refs"]}
- Context export type: `{proof["export_type"]}`
- Context validation: `{proof["context_validation"]["valid"]}`
- Memory calls emitted: {proof["memory_calls"]}
- MCP bindings imported: {proof["mcp_bindings_imported"]}
- Audit chain valid: `{proof["audit"]["valid"]}` across {proof["audit"]["events"]} events

## Benchmark Link

Source: `{benchmark["source"]}`

{benchmark["interpretation"]}

Aggregate row:

```text
{benchmark["aggregate_line"]}
```

## Raw Artifacts

See `summary.json`, `commands.json`, `06_memory_query.json`,
`07_context_build.json`, `08_context_export.json`, `09_context_validate.json`,
`10_loop_run.json`, `12_mcp_import.json`, and `14_audit_verify.json`.
"""
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
