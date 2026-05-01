from __future__ import annotations

from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.runner import MemoryCriticalBenchmark


def test_benchmark_oacs_beats_baseline(svc):
    tasks = SyntheticTaskGenerator().generate("memory_critical", 3)
    bench = MemoryCriticalBenchmark(svc.memory, svc.loop)
    baseline = bench.run(tasks, "baseline_no_memory", None)
    full_context = bench.run(tasks, "baseline_full_context", None)
    oacs_run = bench.run(tasks, "oacs_memory_loop", None)
    assert oacs_run.summary["average_score"] > baseline.summary["average_score"]
    assert full_context.summary["tokens_estimated"] > baseline.summary["tokens_estimated"]
    assert oacs_run.summary["score_per_1k_tokens"] > 0
