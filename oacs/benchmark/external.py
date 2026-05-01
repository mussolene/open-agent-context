from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx

from oacs.benchmark.models import BenchmarkTask

MEMORYARENA_URLS = {
    "group_travel_planner": (
        "https://huggingface.co/datasets/ZexueHe/memoryarena/resolve/main/"
        "group_travel_planner/data.jsonl"
    ),
    "progressive_search": (
        "https://huggingface.co/datasets/ZexueHe/memoryarena/resolve/main/"
        "progressive_search/data.jsonl"
    ),
}


class MemoryArenaImporter:
    def from_file(self, path: Path, count: int) -> list[BenchmarkTask]:
        rows = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
                if len(rows) >= count:
                    break
        return self.from_rows(rows, count)

    def from_url(self, url: str, count: int) -> list[BenchmarkTask]:
        response = httpx.get(url, timeout=60, follow_redirects=True)
        response.raise_for_status()
        rows = []
        for line in response.text.splitlines():
            if line.strip():
                rows.append(json.loads(line))
            if len(rows) >= count:
                break
        return self.from_rows(rows, count)

    def from_subset(self, subset: str, count: int) -> list[BenchmarkTask]:
        try:
            url = MEMORYARENA_URLS[subset]
        except KeyError as exc:
            supported = ", ".join(sorted(MEMORYARENA_URLS))
            message = f"unsupported MemoryArena subset: {subset}; supported: {supported}"
            raise ValueError(message) from exc
        return self.from_url(url, count)

    def from_rows(self, rows: list[dict[str, Any]], count: int) -> list[BenchmarkTask]:
        tasks: list[BenchmarkTask] = []
        for row in rows:
            task = self._convert_group_travel_row(row)
            if task is not None:
                tasks.append(task)
            if len(tasks) >= count:
                break
        return tasks

    def _convert_group_travel_row(self, row: dict[str, Any]) -> BenchmarkTask | None:
        questions = row.get("questions")
        answers = row.get("answers")
        if not isinstance(questions, list) or not isinstance(answers, list) or len(questions) < 2:
            return None

        question_index = 1
        row_id = str(row.get("id", "unknown"))
        previous_answers = answers[:question_index]
        current_answer = answers[question_index]
        current_question = str(questions[question_index])
        expected = _expected_facts(previous_answers, current_answer, current_question)
        if not expected:
            return None

        setup_memories = [
            {
                "memory_type": "episode",
                "depth": 1,
                "scope": [f"memoryarena:{row_id}"],
                "text": (
                    f"MemoryArena group_travel_planner row {row_id} base plan:\n"
                    f"{json.dumps(row.get('base_person', {}), ensure_ascii=False)}"
                ),
            }
        ]
        for index, answer in enumerate(previous_answers):
            setup_memories.append(
                {
                    "memory_type": "episode",
                    "depth": 1,
                    "scope": [f"memoryarena:{row_id}"],
                    "text": (
                        f"MemoryArena group_travel_planner row {row_id} prior participant "
                        f"{index + 1} request:\n{questions[index]}\nExact accepted plan:\n"
                        f"{json.dumps(answer, ensure_ascii=False)}"
                    ),
                }
            )

        return BenchmarkTask(
            type="memoryarena_group_travel_planner",
            setup_memories=setup_memories,
            user_prompt=(
                "Use the prior trip plans if available. Answer the current MemoryArena "
                "group_travel_planner request with the exact reused plan items.\n\n"
                f"Dataset row: {row_id}\nCurrent request:\n{questions[question_index]}"
            ),
            expected_facts=expected,
            rubric={
                "max_score": 5,
                "source": "ZexueHe/memoryarena",
                "subset": "group_travel_planner",
                "row_id": row_id,
                "question_index": question_index,
                "scope": [f"memoryarena:{row_id}"],
                "max_output_tokens": 512,
                "requires_memory": True,
            },
        )


def _expected_facts(
    previous_answers: list[Any], current_answer: Any, current_question: str
) -> list[str]:
    previous_strings = set(_strings(previous_answers))
    current_strings = list(dict.fromkeys(_requested_slot_strings(current_answer, current_question)))
    overlaps = [
        value
        for value in current_strings
        if value in previous_strings and _is_specific_expected_fact(value)
    ]
    candidates = overlaps or [
        value for value in current_strings if _is_specific_expected_fact(value)
    ]
    return sorted(candidates, key=len, reverse=True)[:3]


def _requested_slot_strings(value: Any, question: str) -> Iterable[str]:
    requested = {
        key
        for key in ("breakfast", "lunch", "dinner", "accommodation", "attraction", "transportation")
        if key in question.lower()
    }
    requested_days = _requested_days(question)
    if not requested:
        yield from _strings(value)
        return
    yield from _strings_for_keys(value, requested, requested_days)


def _strings_for_keys(value: Any, requested: set[str], requested_days: set[int]) -> Iterable[str]:
    if isinstance(value, dict):
        day = value.get("days")
        if requested_days and isinstance(day, int) and day not in requested_days:
            return
        for key, child in value.items():
            if str(key).lower() in requested:
                yield from _strings(child)
            elif isinstance(child, dict | list):
                yield from _strings_for_keys(child, requested, requested_days)
        return
    if isinstance(value, list):
        for child in value:
            yield from _strings_for_keys(child, requested, requested_days)


def _requested_days(question: str) -> set[int]:
    question_lower = question.lower()
    mapping = {"first": 1, "second": 2, "third": 3, "1": 1, "2": 2, "3": 3}
    return {
        day
        for word, day in mapping.items()
        if re.search(rf"\b{re.escape(word)}[- ]day\b|\bday {re.escape(word)}\b", question_lower)
    }


def _strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned:
            yield cleaned
        return
    if isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
        return
    if isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _is_specific_expected_fact(value: str) -> bool:
    if value == "-":
        return False
    if len(value) < 6:
        return False
    generic = {
        "Rockford",
        "St. Petersburg",
        "from St. Petersburg to Rockford",
        "from Rockford to St. Petersburg",
    }
    return value not in generic
