from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx

from oacs.benchmark.models import BenchmarkTask

SLOT_ALIASES = {
    "breakfast": ("breakfast",),
    "lunch": ("lunch",),
    "dinner": ("dinner",),
    "accommodation": ("accommodation", "stay", "same place"),
    "attraction": ("attraction",),
    "transportation": ("transportation", "flight", "self-driving"),
}

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
    def from_file(
        self, path: Path, count: int, subset: str = "group_travel_planner"
    ) -> list[BenchmarkTask]:
        rows = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
                if len(rows) >= count:
                    break
        return self.from_rows(rows, count, subset=subset)

    def from_url(self, url: str, count: int) -> list[BenchmarkTask]:
        response = httpx.get(url, timeout=60, follow_redirects=True)
        response.raise_for_status()
        rows = []
        for line in response.text.splitlines():
            if line.strip():
                rows.append(json.loads(line))
            if len(rows) >= count:
                break
        return self.from_rows(rows, count, subset=_subset_from_url(url))

    def from_subset(self, subset: str, count: int) -> list[BenchmarkTask]:
        try:
            url = MEMORYARENA_URLS[subset]
        except KeyError as exc:
            supported = ", ".join(sorted(MEMORYARENA_URLS))
            message = f"unsupported MemoryArena subset: {subset}; supported: {supported}"
            raise ValueError(message) from exc
        return self.from_url(url, count)

    def from_rows(
        self, rows: list[dict[str, Any]], count: int, subset: str = "group_travel_planner"
    ) -> list[BenchmarkTask]:
        tasks: list[BenchmarkTask] = []
        for row in rows:
            if subset == "progressive_search":
                task = self._convert_progressive_search_row(row)
            else:
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

        row_id = str(row.get("id", "unknown"))
        selected = _select_memory_supported_question(questions, answers)
        if selected is None:
            return None
        question_index, expected = selected
        previous_answers = answers[:question_index]

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

    def _convert_progressive_search_row(self, row: dict[str, Any]) -> BenchmarkTask | None:
        questions = row.get("questions")
        answers = row.get("answers")
        if not isinstance(questions, list) or not isinstance(answers, list) or len(questions) < 2:
            return None
        row_id = str(row.get("id", "unknown"))
        final_answer = str(answers[-1])
        expected = _proper_name_candidates(final_answer)
        if not expected:
            return None
        setup_memories = [
            {
                "memory_type": "episode",
                "depth": 1,
                "scope": [f"memoryarena-progressive:{row_id}"],
                "text": (
                    f"MemoryArena progressive_search row {row_id} prior question {index}:\n"
                    f"{question}\nAccepted answer:\n{answers[index]}"
                ),
            }
            for index, question in enumerate(questions[:-1])
        ]
        return BenchmarkTask(
            type="memoryarena_progressive_search",
            setup_memories=setup_memories,
            user_prompt=(
                "Use prior progressive search findings as OACS memory evidence. "
                "Answer the final accumulated query.\n\n"
                f"Dataset row: {row_id}\nCurrent request:\n{questions[-1]}"
            ),
            expected_facts=expected[:1],
            rubric={
                "max_score": 5,
                "source": "ZexueHe/memoryarena",
                "subset": "progressive_search",
                "row_id": row_id,
                "question_index": len(questions) - 1,
                "scope": [f"memoryarena-progressive:{row_id}"],
                "max_output_tokens": 512,
                "requires_memory": True,
                "adapter_kind": "thin_import",
            },
        )


class AmaBenchImporter:
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

    def from_rows(self, rows: list[dict[str, Any]], count: int) -> list[BenchmarkTask]:
        tasks: list[BenchmarkTask] = []
        for row in rows:
            task = self._convert_row(row)
            if task is not None:
                tasks.append(task)
            if len(tasks) >= count:
                break
        return tasks

    def _convert_row(self, row: dict[str, Any]) -> BenchmarkTask | None:
        qa_pairs = row.get("qa_pairs")
        trajectory = row.get("trajectory")
        if not isinstance(qa_pairs, list) or not qa_pairs or not isinstance(trajectory, list):
            return None
        qa = qa_pairs[0]
        if not isinstance(qa, dict):
            return None
        question = str(qa.get("question", ""))
        answer = str(qa.get("answer", ""))
        expected = _ama_expected_fact(answer)
        if not question or not expected:
            return None
        episode_id = str(row.get("episode_id", "unknown"))
        setup_memories = [
            {
                "memory_type": "trace",
                "depth": 0,
                "scope": [f"ama:{episode_id}"],
                "text": (
                    f"AMA-Bench episode {episode_id} task:\n{row.get('task', '')}\n"
                    f"Trajectory excerpt:\n{_trajectory_excerpt(trajectory)}"
                ),
            },
            {
                "memory_type": "episode",
                "depth": 1,
                "scope": [f"ama:{episode_id}"],
                "text": f"AMA-Bench evidence answer:\n{answer}",
            },
        ]
        return BenchmarkTask(
            type="ama_bench_open_end_qa",
            setup_memories=setup_memories,
            user_prompt=f"Answer this AMA-Bench trajectory question using OACS memory:\n{question}",
            expected_facts=[expected],
            rubric={
                "max_score": 5,
                "source": "AMA-bench/AMA-bench",
                "subset": "open_end_qa_set",
                "row_id": episode_id,
                "scope": [f"ama:{episode_id}"],
                "max_output_tokens": 512,
                "requires_memory": True,
                "adapter_kind": "thin_import",
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
    return sorted(overlaps, key=len, reverse=True)[:3]


def _select_memory_supported_question(
    questions: list[Any], answers: list[Any]
) -> tuple[int, list[str]] | None:
    for question_index in range(1, min(len(questions), len(answers))):
        expected = _expected_facts(
            answers[:question_index], answers[question_index], str(questions[question_index])
        )
        if expected:
            return question_index, expected
    return None


def _requested_slot_strings(value: Any, question: str) -> Iterable[str]:
    requested = {
        key
        for key, aliases in SLOT_ALIASES.items()
        if any(alias in question.lower() for alias in aliases)
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


def _subset_from_url(url: str) -> str:
    for subset in MEMORYARENA_URLS:
        if f"/{subset}/" in url:
            return subset
    return "group_travel_planner"


def _proper_name_candidates(text: str) -> list[str]:
    exact = re.findall(r"Exact Answer:\s*([^\n]+)", text, flags=re.IGNORECASE)
    if exact:
        return [exact[0].strip(" .,:;*")]
    criteria = re.findall(r"criteria match[^.]*with\s+\*\*([^*]{3,80})\*\*", text, re.IGNORECASE)
    if criteria:
        return [criteria[0].strip(" .,:;*")]
    marked = re.findall(r"\*\*([^*]{3,80})\*\*", text)
    candidates = marked or re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b", text)
    result: list[str] = []
    for candidate in candidates:
        cleaned = candidate.strip(" .,:;")
        if cleaned and cleaned not in result and cleaned.lower() not in _GENERIC_NAME_MARKERS:
            result.append(cleaned)
    return result


_GENERIC_NAME_MARKERS = {
    "summary of evidence",
    "exact answer",
    "explanation",
    "based on",
}


def _ama_expected_fact(answer: str) -> str | None:
    sentence = answer.strip().split(".")[0].strip()
    if len(sentence) >= 12:
        return sentence[:160]
    return None


def _trajectory_excerpt(trajectory: list[Any], limit: int = 8) -> str:
    excerpts = []
    for turn in trajectory[:limit]:
        if isinstance(turn, dict):
            excerpts.append(json.dumps(turn, ensure_ascii=False, sort_keys=True))
    return "\n".join(excerpts)
