from __future__ import annotations

import json

import httpx
import pytest
from jsonschema import ValidationError
from typer.testing import CliRunner

from oacs.app import services
from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.models import BenchmarkRun
from oacs.benchmark.packs import make_task_pack, tasks_from_pack, validate_task_pack
from oacs.benchmark.reports import compare_runs
from oacs.benchmark.runner import MemoryCriticalBenchmark
from oacs.cli.main import app
from oacs.core.errors import ValidationFailure


def test_task_pack_validates_schema_and_checksum() -> None:
    task = SyntheticTaskGenerator().generate("memory_critical", 1)[0]
    pack = make_task_pack([task], "pack_test", "Test Pack", "local")

    assert tasks_from_pack(pack)[0].id == task.id

    pack["tasks"][0].pop("user_prompt")
    with pytest.raises(ValidationError):
        validate_task_pack(pack)


def test_task_pack_rejects_checksum_mismatch() -> None:
    task = SyntheticTaskGenerator().generate("memory_critical", 1)[0]
    pack = make_task_pack([task], "pack_test", "Test Pack", "local")
    pack["tasks"][0]["user_prompt"] = "tampered"

    with pytest.raises(ValidationFailure):
        validate_task_pack(pack)


def test_task_pack_rejects_task_count_mismatch() -> None:
    task = SyntheticTaskGenerator().generate("memory_critical", 1)[0]
    pack = make_task_pack([task], "pack_test", "Test Pack", "local")
    pack["task_count"] = 2
    pack["integrity"]["sha256"] = "0" * 64

    with pytest.raises(ValidationFailure):
        validate_task_pack(pack)


def test_cli_benchmark_import_requires_pack_and_download_requires_network(tmp_path, monkeypatch):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0

    task = SyntheticTaskGenerator().generate("memory_critical", 1)[0]
    pack = make_task_pack([task], "pack_cli", "CLI Pack", "local")
    pack_file = tmp_path / "pack.json"
    pack_file.write_text(json.dumps(pack), encoding="utf-8")

    imported = runner.invoke(
        app, ["benchmark", "import", str(pack_file), "--db", str(db), "--json"]
    )
    assert imported.exit_code == 0, imported.output
    assert task.id in imported.output

    called = False

    def fail_get(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("network should be disabled")

    monkeypatch.setattr(httpx, "get", fail_get)
    denied = runner.invoke(
        app,
        [
            "benchmark",
            "download",
            "https://example.test/pack.json",
            "0" * 64,
            "--db",
            str(db),
            "--json",
        ],
    )
    assert denied.exit_code != 0
    assert called is False


def test_cli_import_memoryarena_requires_file_or_allow_network(tmp_path, monkeypatch):
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0

    called = False

    def fail_get(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("network should be disabled")

    monkeypatch.setattr(httpx, "get", fail_get)
    result = runner.invoke(
        app,
        ["benchmark", "import-memoryarena", "--db", str(db), "--json"],
    )
    assert result.exit_code != 0
    assert called is False


def test_compare_marks_mismatched_provider_or_model_incompatible() -> None:
    baseline = BenchmarkRun(
        mode="baseline_no_memory",
        task_results=[],
        summary={
            "average_score": 1,
            "tokens_estimated": 10,
            "provider": "deterministic",
            "model": None,
            "task_pack_ids": ["pack_a"],
        },
    )
    oacs = BenchmarkRun(
        mode="oacs_memory_call_loop",
        task_results=[],
        summary={
            "average_score": 2,
            "tokens_estimated": 20,
            "provider": "lmstudio",
            "model": "gemma",
            "task_pack_ids": ["pack_a"],
            "native_harnesses": [{"name": "native"}],
        },
    )

    comparison = compare_runs(baseline, oacs)
    assert comparison["compatible"] is False
    assert comparison["oacs_native_harnesses"] == [{"name": "native"}]


def test_lmstudio_usage_is_recorded_when_returned(db, monkeypatch) -> None:
    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "model": "gemma-test",
                "usage": {
                    "prompt_tokens": 7,
                    "completion_tokens": 3,
                    "total_tokens": 10,
                },
                "choices": [
                    {
                        "message": {"content": "make report-safe"},
                        "finish_reason": "stop",
                    }
                ],
            }

    monkeypatch.setattr(httpx, "post", lambda *_args, **_kwargs: Response())
    svc = services(str(db))
    task = SyntheticTaskGenerator().generate("memory_critical", 1)[0]
    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        [task], "baseline_no_memory", None, "gemma-test", "lmstudio"
    )

    assert run.summary["prompt_tokens_estimated"] == 7
    assert run.summary["output_tokens_estimated"] == 3
    assert run.summary["lmstudio_stateless_chat_completions"] is True
    assert run.task_results[0]["lmstudio_usage"]["total_tokens"] == 10
    assert run.task_results[0]["lmstudio_stateless_chat_completions"] is True
