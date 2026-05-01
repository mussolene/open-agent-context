from __future__ import annotations

import json

from oacs.benchmark.models import BenchmarkRun, BenchmarkTask
from oacs.benchmark.scorer import score_answer
from oacs.llm.lmstudio import LMStudioClient
from oacs.llm.prompts import BASELINE_SYSTEM, OACS_SYSTEM, build_oacs_prompt
from oacs.loop.engine import MemoryLoopEngine
from oacs.loop.memory_calls import DeterministicMemoryCallLoop, memory_call_to_dict
from oacs.memory.service import MemoryService

BENCHMARK_MODES = {
    "baseline_no_memory",
    "baseline_full_context",
    "oacs_memory_loop",
    "oacs_memory_call_loop",
}


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
        provider: str = "deterministic",
    ) -> BenchmarkRun:
        if mode not in BENCHMARK_MODES:
            supported = ", ".join(sorted(BENCHMARK_MODES))
            raise ValueError(f"unsupported benchmark mode: {mode}; supported: {supported}")
        results: list[dict[str, object]] = []
        for task in tasks:
            scope = _task_scope(task)
            prompt_tokens = 0
            memory_metrics: dict[str, object] = {}
            if mode == "oacs_memory_loop":
                self._seed_memories(task, actor_id)
                if provider == "lmstudio":
                    answer, prompt_tokens = self._run_oacs_lmstudio(task, actor_id, model, scope)
                else:
                    loop_result = self.loop.run(task.user_prompt, actor_id, scope=scope)
                    answer = loop_result.final_answer
                    prompt_tokens = estimate_tokens(task.user_prompt)
            elif mode == "oacs_memory_call_loop":
                self._seed_memories(task, actor_id)
                answer, prompt_tokens, memory_metrics = self._run_memory_call_loop(
                    task, actor_id, model, scope, provider
                )
            elif mode == "baseline_full_context":
                prompt = _full_context_prompt(task)
                prompt_tokens = estimate_tokens(prompt)
                if provider == "lmstudio":
                    answer = _lmstudio_client(task, model).chat(prompt, BASELINE_SYSTEM)
                else:
                    answer = f"Generic answer for: {prompt}"
            else:
                prompt_tokens = estimate_tokens(task.user_prompt)
                if provider == "lmstudio":
                    answer = _lmstudio_client(task, model).chat(task.user_prompt, BASELINE_SYSTEM)
                else:
                    answer = f"Generic answer for: {task.user_prompt}"
            result = score_answer(task, answer)
            output_tokens = estimate_tokens(answer)
            result.update(
                {
                    "task_id": task.id,
                    "task_type": task.type,
                    "answer": answer,
                    "provider": provider,
                    "model": model,
                    "prompt_tokens_estimated": prompt_tokens,
                    "output_tokens_estimated": output_tokens,
                    "tokens_estimated": prompt_tokens + output_tokens,
                    **memory_metrics,
                }
            )
            results.append(result)
        avg = sum(int(str(r["rubric_score"])) for r in results) / max(1, len(results))
        total_tokens = sum(int(str(r["tokens_estimated"])) for r in results)
        return BenchmarkRun(
            mode=mode,
            task_results=results,
            summary={
                "average_score": avg,
                "successes": sum(bool(r["exact_success"]) for r in results),
                "tasks": len(results),
                "provider": provider,
                "model": model,
                "prompt_tokens_estimated": sum(
                    int(str(r["prompt_tokens_estimated"])) for r in results
                ),
                "output_tokens_estimated": sum(
                    int(str(r["output_tokens_estimated"])) for r in results
                ),
                "tokens_estimated": total_tokens,
                "score_per_1k_tokens": round((avg * len(results)) / max(1, total_tokens) * 1000, 4),
                "memory_calls_count": sum(
                    int(str(r.get("memory_calls_count", 0))) for r in results
                ),
                "evidence_items": sum(int(str(r.get("evidence_items", 0))) for r in results),
            },
        )

    def _seed_memories(self, task: BenchmarkTask, actor_id: str | None) -> None:
        for setup in task.setup_memories:
            mem = self.memory.propose(
                str(setup["memory_type"]),
                int(str(setup["depth"])),
                str(setup["text"]),
                actor_id,
                setup.get("scope", ["project"]),  # type: ignore[arg-type]
                evidence=setup.get("evidence"),  # type: ignore[arg-type]
            )
            if mem.depth >= 3:
                mem = self.memory.sharpen(mem.id, "synthetic_benchmark_evidence", actor_id)
            if setup.get("status") == "superseded":
                self.memory.commit(mem.id, actor_id)
                self.memory.deprecate(mem.id, actor_id)
            else:
                self.memory.commit(mem.id, actor_id)

    def _run_oacs_lmstudio(
        self, task: BenchmarkTask, actor_id: str | None, model: str | None, scope: list[str]
    ) -> tuple[str, int]:
        capsule = self.loop.context_builder.build(
            task.user_prompt,
            actor_id,
            scope=scope,
            token_budget=int(str(task.rubric.get("token_budget", 4000))),
        )
        memories = [
            self.memory.read(memory_id, actor_id) for memory_id in capsule.included_memories
        ]
        prompt = build_oacs_prompt(task.user_prompt, capsule, memories)
        return _lmstudio_client(task, model).chat(prompt, OACS_SYSTEM), estimate_tokens(prompt)

    def _run_memory_call_loop(
        self,
        task: BenchmarkTask,
        actor_id: str | None,
        model: str | None,
        scope: list[str],
        provider: str,
    ) -> tuple[str, int, dict[str, object]]:
        memories = self.memory.query(task.user_prompt, actor_id, scope)
        call_result = DeterministicMemoryCallLoop().build_prompt(task.user_prompt, memories)
        prompt_tokens = estimate_tokens(call_result.prompt)
        if provider == "lmstudio":
            model_answer = _lmstudio_client(task, model).chat(call_result.prompt, OACS_SYSTEM)
            if call_result.answer:
                answer = f"OACS memory answer: {call_result.answer}\nModel response: {model_answer}"
            else:
                answer = model_answer
        else:
            answer = call_result.answer or call_result.prompt
        return answer, prompt_tokens, {
            "memory_calls": [memory_call_to_dict(call) for call in call_result.memory_calls],
            "memory_calls_count": len(call_result.memory_calls),
            "evidence_items": len(call_result.evidence),
            "evidence_values": [item.value for item in call_result.evidence],
            "answered_deterministically": call_result.answered_deterministically,
        }


def _task_scope(task: BenchmarkTask) -> list[str]:
    raw = task.rubric.get("scope")
    if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
        return raw
    return ["project"]


def _lmstudio_client(task: BenchmarkTask, model: str | None) -> LMStudioClient:
    max_tokens = int(str(task.rubric.get("max_output_tokens", 512)))
    return LMStudioClient(model=model, max_tokens=max_tokens)


def _full_context_prompt(task: BenchmarkTask) -> str:
    memories = "\n\n".join(
        json.dumps(_baseline_memory_view(memory), ensure_ascii=False, sort_keys=True)
        for memory in task.setup_memories
    )
    return "\n".join(
        [
            "Use the prior task context below if it is relevant.",
            "Prior context:",
            memories or "none",
            "Current task:",
            task.user_prompt,
        ]
    )


def estimate_tokens(text: str) -> int:
    # Deterministic approximation for local reports; avoids tokenizer-specific dependencies.
    return max(1, (len(text) + 3) // 4)


def _baseline_memory_view(memory: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in memory.items() if key != "evidence"}
