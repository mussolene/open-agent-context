from __future__ import annotations

from oacs.benchmark.external import MemoryArenaImporter


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
