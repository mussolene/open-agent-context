from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_killer_demo_generates_governed_context_artifacts(tmp_path) -> None:
    out_dir = tmp_path / "killer-demo"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "examples" / "killer_demo" / "run_demo.py"),
            "--out",
            str(out_dir),
            "--force",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "PASS"
    assert "not an agent framework" in " ".join(summary["product_story"])
    proof = summary["proof_points"]
    assert proof["memory_query_hits"] == 1
    assert proof["capsule_memory_refs"] == 1
    assert proof["context_validation"]["valid"] is True
    assert proof["memory_calls"] >= 2
    assert proof["tool_call_evidence_ref"].startswith("ev_")
    assert proof["tool_call_output"]["echo"]["request"] == "capture release evidence proof"
    assert proof["mcp_bindings_imported"] == 1
    assert proof["audit"]["valid"] is True

    capsule = json.loads((out_dir / "07_context_build.json").read_text(encoding="utf-8"))
    assert proof["memory_id"] in capsule["included_memories"]
    assert capsule["scope"] == ["project:atlas"]

    export = json.loads((out_dir / "08_context_export.json").read_text(encoding="utf-8"))
    assert export["export_type"] == "context_capsule_export"
    assert export["integrity"]["algorithm"] == "HMAC-SHA256"

    loop = json.loads((out_dir / "10_loop_run.json").read_text(encoding="utf-8"))
    assert [call["op"] for call in loop["memory_calls"]] == [
        "memory.query",
        "memory.read",
        "memory.extract_evidence",
    ]

    api_loop = json.loads((out_dir / "api_loop_run.json").read_text(encoding="utf-8"))
    assert api_loop["method"] == "POST"
    assert api_loop["path"] == "/v1/loop/run"
    assert api_loop["response_shape"]["memory_calls"] == loop["memory_calls"]

    benchmark = summary["benchmark_comparison"]
    assert benchmark["source"] == "examples/benchmarks/full_context_gemma_e2b_2026-05-02.md"
    assert "20/20" in benchmark["aggregate_line"]
    assert benchmark["score_per_1k_tokens"]["oacs_memory_call_loop"] == 4.364
