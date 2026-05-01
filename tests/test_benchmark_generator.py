from __future__ import annotations

from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.reports import compare_runs, select_comparison_runs
from oacs.benchmark.runner import MemoryCriticalBenchmark


def test_benchmark_oacs_beats_baseline(svc):
    tasks = SyntheticTaskGenerator().generate("memory_critical", 3)
    bench = MemoryCriticalBenchmark(svc.memory, svc.loop)
    baseline = bench.run(tasks, "baseline_no_memory", None)
    full_context = bench.run(tasks, "baseline_full_context", None)
    oacs_run = bench.run(tasks, "oacs_memory_loop", None)
    assert oacs_run.summary["average_score"] > baseline.summary["average_score"]
    assert full_context.summary["average_score"] > baseline.summary["average_score"]
    assert full_context.summary["tokens_estimated"] > baseline.summary["tokens_estimated"]
    assert oacs_run.summary["score_per_1k_tokens"] > 0


def test_synthetic_tasks_expose_structured_evidence_to_memory_call_loop(svc):
    tasks = SyntheticTaskGenerator().generate("memory_critical", 3)
    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        tasks, "oacs_memory_call_loop", None
    )

    assert run.summary["successes"] == 3
    assert run.summary["evidence_items"] == 3
    assert run.summary["memory_calls_count"] == 6


def test_unknown_benchmark_mode_is_rejected(svc):
    tasks = SyntheticTaskGenerator().generate("memory_critical", 1)

    try:
        MemoryCriticalBenchmark(svc.memory, svc.loop).run(tasks, "not_a_mode", None)
    except ValueError as exc:
        assert "unsupported benchmark mode" in str(exc)
    else:
        raise AssertionError("expected unsupported benchmark mode to fail")


def test_compare_prefers_memory_call_loop_over_missing_oacs_loop(svc):
    tasks = SyntheticTaskGenerator().generate("memory_critical", 1)
    bench = MemoryCriticalBenchmark(svc.memory, svc.loop)
    baseline = bench.run(tasks, "baseline_no_memory", None)
    memory_calls = bench.run(tasks, "oacs_memory_call_loop", None)

    selected_baseline, selected_oacs = select_comparison_runs(
        [
            {"mode": baseline.mode, "payload": baseline.model_dump()},
            {"mode": memory_calls.mode, "payload": memory_calls.model_dump()},
        ]
    )
    comparison = compare_runs(selected_baseline, selected_oacs)

    assert selected_oacs.mode == "oacs_memory_call_loop"
    assert comparison["improvement"] > 0
