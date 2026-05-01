from __future__ import annotations

from oacs.benchmark.external import AmaBenchImporter, MemoryArenaImporter
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


def test_memory_call_loop_extracts_exact_scoped_evidence(svc):
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
        [task], "oacs_memory_call_loop", None
    )
    result = run.task_results[0]

    assert run.mode == "oacs_memory_call_loop"
    assert result["exact_success"] is True
    assert result["used_required_fact"] is True
    assert "Correct Lunch, Testville" in str(result["answer"])
    assert "Wrong Day Cafe, Testville" not in str(result["answer"])
    assert result["memory_calls_count"] == 2
    assert [call["op"] for call in result["memory_calls"]] == [
        "memory.query",
        "memory.extract_evidence",
    ]
    assert result["evidence_items"] == 1
    assert result["prompt_tokens_estimated"] > len(task.user_prompt) // 4
    assert run.summary["tokens_estimated"] == result["tokens_estimated"]


def test_memoryarena_importer_skips_constraint_only_question_until_memory_reuse():
    row = {
        "id": 10,
        "base_person": {"name": "Jennifer", "daily_plans": []},
        "questions": [
            "I am Eric. I need dinner.",
            "I am Maria. For dinner on the second day, I want a new BBQ place.",
            "I am Zoe. For lunch on the first day, I'd like to join Eric.",
        ],
        "answers": [
            [{"days": 1, "lunch": "Known Lunch, Testville"}],
            [{"days": 2, "dinner": "New Constraint Dinner, Testville"}],
            [{"days": 1, "lunch": "Known Lunch, Testville"}],
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1)[0]

    assert task.rubric["question_index"] == 2
    assert task.expected_facts == ["Known Lunch, Testville"]


def test_memoryarena_importer_treats_stay_as_accommodation():
    row = {
        "id": 11,
        "base_person": {"name": "Jennifer", "daily_plans": []},
        "questions": [
            "I am Amelia. I need accommodation.",
            "I am Maria. On the second day, I want to stay at the same place as Amelia.",
        ],
        "answers": [
            [
                {"days": 1, "accommodation": "Wrong Stay, Testville"},
                {"days": 2, "accommodation": "Correct Stay, Testville"},
            ],
            [
                {"days": 1, "accommodation": "Wrong Stay, Testville"},
                {"days": 2, "accommodation": "Correct Stay, Testville"},
            ],
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1)[0]

    assert task.expected_facts == ["Correct Stay, Testville"]


def test_memoryarena_progressive_search_importer_maps_accumulated_answer():
    row = {
        "id": 12,
        "questions": ["Who owns a business?", "Who owns a business and graduated in Abuja?"],
        "answers": [
            "The answer is **Ihuoma Sonia Uche**.",
            "The full name is **Ihuoma Sonia Uche**.",
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1, subset="progressive_search")[0]

    assert task.type == "memoryarena_progressive_search"
    assert task.expected_facts == ["Ihuoma Sonia Uche"]
    assert task.rubric["subset"] == "progressive_search"
    assert task.setup_memories[0]["memory_type"] == "episode"


def test_memoryarena_progressive_search_ignores_summary_marker():
    row = {
        "id": 13,
        "questions": ["Which athlete won?", "Which athlete matches every clue?"],
        "answers": [
            "Evidence points to **Tulsidas Balaram**.",
            "**Summary of evidence:** All criteria match perfectly with **Tulsidas Balaram**.",
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1, subset="progressive_search")[0]

    assert task.expected_facts == ["Tulsidas Balaram"]


def test_memoryarena_progressive_search_accepts_name_aliases():
    row = {
        "id": 16,
        "questions": ["Who received the donation?", "Who appeared on TV later?"],
        "answers": [
            "The recipient was **John Daniel delos Santos**.",
            "Exact Answer: Daniel Delos Santos (also written as John Daniel delos Santos)",
        ],
    }

    task = MemoryArenaImporter().from_rows([row], 1, subset="progressive_search")[0]

    assert "Daniel Delos Santos" in task.expected_facts
    assert "John Daniel delos Santos" in task.expected_facts


def test_memory_call_loop_extracts_progressive_search_evidence(svc):
    row = {
        "id": 14,
        "questions": ["Who owns a business?", "Who owns a business and graduated in Abuja?"],
        "answers": [
            "The answer is **Ihuoma Sonia Uche**.",
            "The full name is **Ihuoma Sonia Uche**.",
        ],
    }
    task = MemoryArenaImporter().from_rows([row], 1, subset="progressive_search")[0]

    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        [task], "oacs_memory_call_loop", None
    )
    result = run.task_results[0]

    assert result["exact_success"] is True
    assert result["used_required_fact"] is True
    assert result["evidence_items"] == 1
    assert "Ihuoma Sonia Uche" in str(result["answer"])
    assert result["prompt_tokens_estimated"] > len(task.user_prompt) // 4


def test_memory_call_loop_focuses_progressive_search_on_latest_evidence(svc):
    row = {
        "id": 15,
        "questions": [
            "Who is the candidate?",
            "Who is the candidate after adding the Abuja clue?",
            "Who is the final candidate after every clue?",
        ],
        "answers": [
            "The candidate might be **Wrong Candidate**.",
            "The accumulated answer is **Correct Candidate**.",
            "Exact Answer: Correct Candidate",
        ],
    }
    task = MemoryArenaImporter().from_rows([row], 1, subset="progressive_search")[0]

    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        [task], "oacs_memory_call_loop", None
    )
    result = run.task_results[0]

    assert result["exact_success"] is True
    assert result["evidence_items"] == 1
    assert result["evidence_values"] == ["The accumulated answer is **Correct Candidate**."]
    assert "Wrong Candidate" not in str(result["answer"])


def test_ama_bench_importer_maps_trajectory_qa_to_oacs_task():
    row = {
        "episode_id": 42,
        "task": "Grid puzzle",
        "trajectory": [
            {"turn_idx": 0, "action": "left", "observation": "state A"},
            {"turn_idx": 1, "action": "right", "observation": "state B"},
        ],
        "qa_pairs": [
            {
                "question": "What happened after the right action?",
                "answer": (
                    "The right action moved the agent back to state B. "
                    "This indicates reversal."
                ),
            }
        ],
    }

    task = AmaBenchImporter().from_rows([row], 1)[0]

    assert task.type == "ama_bench_open_end_qa"
    assert task.expected_facts == ["The right action moved the agent back to state B"]
    assert task.rubric["source"] == "AMA-bench/AMA-bench"
    assert task.setup_memories[0]["memory_type"] == "trace"
    assert task.setup_memories[1]["memory_type"] == "episode"


def test_memory_call_loop_extracts_ama_evidence(svc):
    row = {
        "episode_id": 43,
        "task": "Grid puzzle",
        "trajectory": [
            {"turn_idx": 0, "action": "down", "observation": "state A"},
            {"turn_idx": 1, "action": "up", "observation": "state B"},
        ],
        "qa_pairs": [
            {
                "question": "Which action reversed the previous move?",
                "answer": (
                    "The `up` action at Step 8 is the direct inverse of the "
                    "`down` action at Step 7."
                ),
            }
        ],
    }
    task = AmaBenchImporter().from_rows([row], 1)[0]

    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(
        [task], "oacs_memory_call_loop", None
    )
    result = run.task_results[0]

    assert result["exact_success"] is True
    assert result["used_required_fact"] is True
    assert result["evidence_items"] == 1
    assert "up` action at Step 8" in str(result["answer"])
