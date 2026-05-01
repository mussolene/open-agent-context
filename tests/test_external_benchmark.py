from __future__ import annotations

from oacs.benchmark.external import MemoryArenaImporter
from oacs.benchmark.runner import MemoryCriticalBenchmark


def test_memoryarena_importer_builds_memory_dependent_task():
    row = {
        "id": 7,
        "base_person": {"name": "Jennifer", "daily_plans": []},
        "questions": [
            "I am Eric. I need breakfast.",
            "I am Emma. For accommodation on the first day, I'd like to join Eric.",
        ],
        "answers": [
            [
                {
                    "days": 1,
                    "dinner": "Coco Bambu, Rockford",
                    "accommodation": "Pure luxury one bdrm + sofa bed on Central Park, Rockford",
                }
            ],
            [
                {
                    "days": 1,
                    "dinner": "Coco Bambu, Rockford",
                    "accommodation": "Pure luxury one bdrm + sofa bed on Central Park, Rockford",
                }
            ],
        ],
    }

    tasks = MemoryArenaImporter().from_rows([row], 1)

    assert len(tasks) == 1
    task = tasks[0]
    assert task.type == "memoryarena_group_travel_planner"
    assert task.expected_facts == ["Pure luxury one bdrm + sofa bed on Central Park, Rockford"]
    assert task.rubric["source"] == "ZexueHe/memoryarena"
    assert task.setup_memories[1]["depth"] == 1


def test_memoryarena_importer_filters_expected_fact_by_day_and_slot():
    row = {
        "id": 8,
        "base_person": {"name": "Jennifer", "daily_plans": []},
        "questions": [
            "I am Eric. I need lunch.",
            "I am Emma. For lunch on the second day, I'd like to join Eric.",
        ],
        "answers": [
            [
                {"days": 1, "lunch": "Wrong Day Cafe, Testville", "dinner": "Wrong Slot"},
                {"days": 2, "lunch": "Correct Lunch, Testville", "dinner": "Wrong Dinner"},
            ],
            [
                {"days": 1, "lunch": "Wrong Day Cafe, Testville", "dinner": "Wrong Slot"},
                {"days": 2, "lunch": "Correct Lunch, Testville", "dinner": "Wrong Dinner"},
            ],
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1)[0]

    assert task.expected_facts == ["Correct Lunch, Testville"]


def test_memory_tool_loop_extracts_exact_scoped_evidence(svc):
    row = {
        "id": 9,
        "base_person": {"name": "Jennifer", "daily_plans": []},
        "questions": [
            "I am Eric. I need lunch.",
            "I am Emma. For lunch on the second day, I'd like to join Eric.",
        ],
        "answers": [
            [
                {"days": 1, "lunch": "Wrong Day Cafe, Testville"},
                {"days": 2, "lunch": "Correct Lunch, Testville"},
            ],
            [
                {"days": 1, "lunch": "Wrong Day Cafe, Testville"},
                {"days": 2, "lunch": "Correct Lunch, Testville"},
            ],
        ],
    }
    task = MemoryArenaImporter().from_rows([row], 1)[0]

    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        [task], "oacs_memory_tool_loop", None
    )
    result = run.task_results[0]

    assert run.mode == "oacs_memory_tool_loop"
    assert result["exact_success"] is True
    assert result["used_required_fact"] is True
    assert "Correct Lunch, Testville" in str(result["answer"])
    assert "Wrong Day Cafe, Testville" not in str(result["answer"])
    assert result["tool_operations"] == 3
    assert result["evidence_items"] == 1
    assert result["prompt_tokens_estimated"] > len(task.user_prompt) // 4
    assert run.summary["tokens_estimated"] == result["tokens_estimated"]
