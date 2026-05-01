from __future__ import annotations

from oacs.benchmark.models import BenchmarkRun


def compare_runs(baseline: BenchmarkRun, oacs: BenchmarkRun) -> dict[str, object]:
    baseline_average = float(str(baseline.summary.get("average_score", 0) or 0))
    oacs_average = float(str(oacs.summary.get("average_score", 0) or 0))
    return {
        "baseline_average": baseline_average,
        "oacs_average": oacs_average,
        "improvement": oacs_average - baseline_average,
    }
