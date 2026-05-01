from __future__ import annotations


def distill_trace_to_candidate(trace_text: str) -> str:
    lines = [line.strip() for line in trace_text.splitlines() if line.strip()]
    return " ".join(lines)[:1000]
