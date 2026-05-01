from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx

from oacs.benchmark.models import BenchmarkTask

TRAVEL_PLAN_FIELDS = (
    "breakfast",
    "lunch",
    "dinner",
    "accommodation",
    "attraction",
    "transportation",
)

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
        memory_selectors = _memory_selectors(previous_answers, answers[question_index], expected)

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
                    "evidence": _travel_evidence_items(
                        answer,
                        row_id=row_id,
                        participant=_participant_from_question(str(questions[index])),
                        source_ref=f"memoryarena:{row_id}:answer:{index}",
                    ),
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
                "memory_selectors": memory_selectors,
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
                "evidence": [
                    {
                        "evidence_kind": "accepted_answer",
                        "claim": "Accepted answer for prior progressive search query",
                        "value": str(answers[index]),
                        "source_ref": f"memoryarena-progressive:{row_id}:answer:{index}",
                        "confidence": 1.0,
                        "slot": "evidence",
                        "order": index + 1,
                    }
                ],
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
            expected_facts=expected[:3],
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
                "evidence": [
                    {
                        "evidence_kind": "trajectory_answer",
                        "claim": "Answer grounded in AMA-Bench trajectory",
                        "value": answer,
                        "source_ref": f"ama:{episode_id}:qa:0",
                        "confidence": 1.0,
                        "slot": "evidence",
                    }
                ],
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


def _expected_facts(previous_answers: list[Any], current_answer: Any) -> list[str]:
    previous_strings = set(_strings(previous_answers))
    current_strings = list(dict.fromkeys(_strings_for_plan_fields(current_answer)))
    overlaps = [
        value
        for value in current_strings
        if value in previous_strings and _is_specific_expected_fact(value)
    ]
    if len(overlaps) != 1:
        return []
    return overlaps


def _select_memory_supported_question(
    questions: list[Any], answers: list[Any]
) -> tuple[int, list[str]] | None:
    for question_index in range(1, min(len(questions), len(answers))):
        expected = _expected_facts(answers[:question_index], answers[question_index])
        if expected:
            return question_index, expected
    return None


def _strings_for_plan_fields(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in TRAVEL_PLAN_FIELDS:
                yield from _strings(child)
            elif isinstance(child, dict | list):
                yield from _strings_for_plan_fields(child)
        return
    if isinstance(value, list):
        for child in value:
            yield from _strings_for_plan_fields(child)


def _memory_selectors(
    previous_answers: list[Any], current_answer: Any, expected: list[str]
) -> dict[str, object]:
    expected_set = set(expected)
    selector_items: list[dict[str, object]] = []
    for current_slot, _current_day, current_value in _travel_plan_values(current_answer):
        if current_value not in expected_set:
            continue
        for index, previous_answer in enumerate(previous_answers):
            for previous_slot, previous_day, previous_value in _travel_plan_values(previous_answer):
                if previous_value == current_value:
                    selector: dict[str, object] = {
                        "slot": previous_slot or current_slot,
                        "source_index": index,
                    }
                    if previous_day is not None:
                        selector["day"] = previous_day
                    selector_items.append(selector)
    slots = sorted({str(item["slot"]) for item in selector_items if item.get("slot")})
    days: list[int] = []
    for item in selector_items:
        day = item.get("day")
        if isinstance(day, int) and day not in days:
            days.append(day)
    days.sort()
    return {
        "items": selector_items,
        "slots": slots,
        "days": days,
    }


def _travel_evidence_items(
    answer: Any, row_id: str, participant: str | None, source_ref: str
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    plans = answer if isinstance(answer, list) else [answer]
    for plan in plans:
        if not isinstance(plan, dict):
            continue
        day = plan.get("days")
        for slot in TRAVEL_PLAN_FIELDS:
            value = plan.get(slot)
            if isinstance(value, str) and _is_specific_expected_fact(value):
                item: dict[str, object] = {
                    "evidence_kind": "travel_plan_item",
                    "claim": f"Accepted {slot} plan item",
                    "value": value,
                    "source_ref": source_ref,
                    "confidence": 1.0,
                    "scope": [f"memoryarena:{row_id}"],
                    "slot": slot,
                }
                if isinstance(day, int):
                    item["day"] = day
                if participant:
                    item["participant"] = participant
                items.append(item)
    return items


def _travel_plan_values(value: Any) -> Iterable[tuple[str, int | None, str]]:
    plans = value if isinstance(value, list) else [value]
    for plan in plans:
        if not isinstance(plan, dict):
            continue
        day = plan.get("days")
        normalized_day = day if isinstance(day, int) else None
        for slot in TRAVEL_PLAN_FIELDS:
            item = plan.get(slot)
            if isinstance(item, str) and _is_specific_expected_fact(item):
                yield slot, normalized_day, item


def _participant_from_question(question: str) -> str | None:
    match = re.search(r"\bI am ([A-Z][a-z]+)\b", question)
    return match.group(1) if match else None


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
        return _name_variants(exact[0].strip(" .,:;*"))
    criteria = re.findall(r"criteria match[^.]*with\s+\*\*([^*]{3,80})\*\*", text, re.IGNORECASE)
    if criteria:
        return _name_variants(criteria[0].strip(" .,:;*"))
    marked = re.findall(r"\*\*([^*]{3,80})\*\*", text)
    candidates = marked or re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b", text)
    result: list[str] = []
    for candidate in candidates:
        cleaned = candidate.strip(" .,:;")
        if cleaned and cleaned not in result and cleaned.lower() not in _GENERIC_NAME_MARKERS:
            result.extend(item for item in _name_variants(cleaned) if item not in result)
    return result


def _name_variants(value: str) -> list[str]:
    variants = [value]
    base = re.sub(r"\s*\([^)]*\)\s*$", "", value).strip()
    if base and base != value:
        variants.append(base)
    alias = re.search(r"\b(?:also written as|also referred to as)\s+([^;)]+)", value, re.I)
    if alias:
        variants.append(alias.group(1).strip())
    return list(dict.fromkeys(variants))


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
