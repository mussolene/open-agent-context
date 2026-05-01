from __future__ import annotations

from oacs.benchmark.models import BenchmarkRun


def compare_runs(baseline: BenchmarkRun, oacs: BenchmarkRun) -> dict[str, object]:
    baseline_average = float(str(baseline.summary.get("average_score", 0) or 0))
    oacs_average = float(str(oacs.summary.get("average_score", 0) or 0))
    baseline_tokens = int(str(baseline.summary.get("tokens_estimated", 0) or 0))
    oacs_tokens = int(str(oacs.summary.get("tokens_estimated", 0) or 0))
    return {
        "baseline_average": baseline_average,
        "oacs_average": oacs_average,
        "improvement": oacs_average - baseline_average,
        "baseline_tokens_estimated": baseline_tokens,
        "oacs_tokens_estimated": oacs_tokens,
        "token_delta_estimated": oacs_tokens - baseline_tokens,
        "baseline_score_per_1k_tokens": baseline.summary.get("score_per_1k_tokens", 0),
        "oacs_score_per_1k_tokens": oacs.summary.get("score_per_1k_tokens", 0),
    }
