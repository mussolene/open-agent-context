from __future__ import annotations

from fastapi import APIRouter

from oacs.app import services
from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.models import BenchmarkTask
from oacs.benchmark.reports import compare_runs, select_comparison_runs
from oacs.benchmark.runner import MemoryCriticalBenchmark
from oacs.core.json import hash_json
from oacs.core.time import now_iso

router = APIRouter(prefix="/v1")


@router.post("/benchmark/generate")
def generate(req: dict[str, object]) -> list[dict[str, object]]:
    svc = services(require_key=False)
    tasks = SyntheticTaskGenerator().generate(
        str(req.get("suite", "memory_critical")), int(str(req.get("count", 20)))
    )
    for task in tasks:
        now = now_iso()
        svc.store.put_json(
            "benchmark_tasks",
            {
                "id": task.id,
                "task_type": task.type,
                "payload": task.model_dump(),
                "created_at": now,
                "updated_at": now,
                "status": "active",
                "namespace": "default",
                "scope": ["project"],
                "owner_actor_id": None,
                "content_hash": hash_json(task.model_dump()),
            },
        )
    return [task.model_dump() for task in tasks]


@router.post("/benchmark/run")
def run(req: dict[str, object]) -> dict[str, object]:
    svc = services()
    rows = svc.store.list("benchmark_tasks", "WHERE status='active'")
    tasks = [BenchmarkTask(**row["payload"]) for row in rows] or SyntheticTaskGenerator().generate(
        "memory_critical", 3
    )
    result = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        tasks,
        str(req.get("mode", "baseline_no_memory")),
        req.get("actor_id"),  # type: ignore[arg-type]
    )
    now = now_iso()
    svc.store.put_json(
        "benchmark_runs",
        {
            "id": result.id,
            "mode": result.mode,
            "payload": result.model_dump(),
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "namespace": "default",
            "scope": ["project"],
            "owner_actor_id": req.get("actor_id"),
            "content_hash": hash_json(result.model_dump()),
        },
    )
    return result.model_dump()


@router.post("/benchmark/compare")
def compare() -> dict[str, object]:
    rows = services(require_key=False).store.list("benchmark_runs", "ORDER BY created_at")
    baseline, oacs_run = select_comparison_runs(rows)
    return compare_runs(baseline, oacs_run)
