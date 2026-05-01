from __future__ import annotations

from oacs.benchmark.models import BenchmarkTask

TASK_TYPES = [
    "hidden_project_convention",
    "long_range_preference",
    "contradictory_facts",
    "fuzzy_pattern_requiring_sharpening",
    "multi_agent_scoped_memory",
    "skill_activation",
    "memory_loop_improvement",
]


class SyntheticTaskGenerator:
    def generate(self, suite: str, count: int) -> list[BenchmarkTask]:
        if suite != "memory_critical":
            raise ValueError("only memory_critical suite is implemented")
        tasks: list[BenchmarkTask] = []
        for i in range(count):
            task_type = TASK_TYPES[i % len(TASK_TYPES)]
            tasks.append(self._task(task_type, i))
        return tasks

    def _task(self, task_type: str, index: int) -> BenchmarkTask:
        if task_type == "hidden_project_convention":
            scope = [f"synthetic:{index}"]
            return BenchmarkTask(
                type=task_type,
                setup_memories=[
                    {
                        "memory_type": "procedure",
                        "depth": 2,
                        "scope": scope,
                        "text": (
                            "В проекте Alpha отчёты всегда генерируются через make report-safe."
                        ),
                        "evidence": [
                            {
                                "evidence_kind": "procedure",
                                "claim": "Active Alpha report generation command",
                                "value": "make report-safe",
                                "slot": "evidence",
                                "confidence": 1.0,
                            }
                        ],
                    },
                    {
                        "memory_type": "procedure",
                        "depth": 2,
                        "scope": scope,
                        "text": "Раньше отчёты генерировались через python scripts/report.py.",
                        "evidence": [
                            {
                                "evidence_kind": "procedure",
                                "claim": "Superseded Alpha report generation command",
                                "value": "python scripts/report.py",
                                "slot": "evidence",
                                "confidence": 1.0,
                            }
                        ],
                        "status": "superseded",
                    },
                ],
                user_prompt="Подскажи команду для генерации отчёта в Alpha.",
                expected_facts=["make report-safe"],
                forbidden_facts=["python scripts/report.py"],
                rubric={"max_score": 5, "requires_memory": True, "scope": scope},
            )
        expected = f"memory-critical-fact-{index}"
        scope = [f"synthetic:{index}"]
        return BenchmarkTask(
            type=task_type,
            setup_memories=[
                {
                    "memory_type": "fact",
                    "depth": 2 if "fuzzy" not in task_type else 3,
                    "scope": scope,
                    "text": f"Required answer marker is {expected}.",
                    "evidence": [
                        {
                            "evidence_kind": "fact",
                            "claim": "Required answer marker",
                            "value": expected,
                            "slot": "evidence",
                            "confidence": 0.9,
                        }
                    ],
                }
            ],
            user_prompt=f"Solve task {index} using the project-specific marker.",
            expected_facts=[expected],
            forbidden_facts=[],
            rubric={"max_score": 5, "requires_memory": True, "scope": scope},
        )
