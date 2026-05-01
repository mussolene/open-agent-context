from __future__ import annotations

from oacs.benchmark.models import BenchmarkRun, BenchmarkTask
from oacs.benchmark.scorer import score_answer
from oacs.loop.engine import MemoryLoopEngine
from oacs.memory.service import MemoryService


class MemoryCriticalBenchmark:
    def __init__(self, memory: MemoryService, loop: MemoryLoopEngine):
        self.memory = memory
        self.loop = loop

    def run(
        self,
        tasks: list[BenchmarkTask],
        mode: str,
        actor_id: str | None,
        model: str | None = None,
    ) -> BenchmarkRun:
        results: list[dict[str, object]] = []
        for task in tasks:
            if mode == "oacs_memory_loop":
                for setup in task.setup_memories:
                    mem = self.memory.propose(
                        str(setup["memory_type"]),
                        int(str(setup["depth"])),
                        str(setup["text"]),
                        actor_id,
                        setup.get("scope", ["project"]),  # type: ignore[arg-type]
                    )
                    if mem.depth >= 3:
                        mem = self.memory.sharpen(mem.id, "synthetic_benchmark_evidence", actor_id)
                    if setup.get("status") == "superseded":
                        self.memory.commit(mem.id, actor_id)
                        self.memory.deprecate(mem.id, actor_id)
                    else:
                        self.memory.commit(mem.id, actor_id)
                answer = self.loop.run(task.user_prompt, actor_id, scope=["project"]).final_answer
            else:
                answer = f"Generic answer for: {task.user_prompt}"
            result = score_answer(task, answer)
            result.update({"task_id": task.id, "answer": answer})
            results.append(result)
        avg = sum(int(str(r["rubric_score"])) for r in results) / max(1, len(results))
        return BenchmarkRun(
            mode=mode,
            task_results=results,
            summary={
                "average_score": avg,
                "successes": sum(bool(r["exact_success"]) for r in results),
            },
        )
