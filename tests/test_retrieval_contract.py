from __future__ import annotations

import httpx
import pytest

from oacs.core.errors import ValidationFailure
from oacs.llm.lmstudio import LMStudioClient
from oacs.memory.models import EvidenceItem, MemoryContent, MemoryRecord
from oacs.memory.retrieval import (
    EmbeddingRetrievalProvider,
    LexicalRetrievalProvider,
    RetrievalQuery,
    StructuredEvidenceRetrievalProvider,
)


def test_lexical_retrieval_provider_contract_returns_ranked_hits() -> None:
    provider = LexicalRetrievalProvider()
    first = MemoryRecord(
        id="mem_b",
        memory_type="fact",
        depth=2,
        content=MemoryContent(text="Alpha report command"),
    )
    second = MemoryRecord(
        id="mem_a",
        memory_type="fact",
        depth=2,
        content=MemoryContent(text="Alpha report command"),
    )

    hits = provider.retrieve(RetrievalQuery(text="Alpha report"), [first, second])

    assert [hit.memory.id for hit in hits] == ["mem_a", "mem_b"]
    assert hits[0].provider == "lexical"
    assert hits[0].score > 0
    assert hits[0].reasons == ["lexical_text_overlap"]


def test_memory_query_filters_policy_before_decrypting_or_scoring(svc, monkeypatch) -> None:
    actor = svc.actors.create("agent", "RetrievalScoped")
    svc.capabilities.grant_shared_memory(actor.id, "system", ["task:allowed"])
    denied = svc.memory.propose("fact", 2, "denied retrieval memory", None, ["task:other"])
    svc.memory.commit(denied.id, None)

    def fail_decrypt(row):
        raise AssertionError(f"unauthorized row reached decrypt: {row['id']}")

    monkeypatch.setattr(svc.memory, "_decrypt", fail_decrypt)

    assert svc.memory.query("denied", actor.id, ["task:allowed"]) == []


def test_lexical_retrieval_is_deterministic_for_ties_and_repeated_runs() -> None:
    provider = LexicalRetrievalProvider()
    memories = [
        MemoryRecord(
            id="mem_c",
            memory_type="fact",
            depth=2,
            content=MemoryContent(text="same query words"),
        ),
        MemoryRecord(
            id="mem_a",
            memory_type="fact",
            depth=2,
            content=MemoryContent(text="same query words"),
        ),
        MemoryRecord(
            id="mem_b",
            memory_type="episode",
            depth=1,
            content=MemoryContent(text="same query words"),
        ),
    ]

    orders = [
        [hit.memory.id for hit in provider.retrieve(RetrievalQuery(text="same query"), memories)]
        for _ in range(5)
    ]

    assert orders == [["mem_b", "mem_a", "mem_c"]] * 5


def test_structured_evidence_retrieval_is_generic_not_benchmark_specific() -> None:
    provider = StructuredEvidenceRetrievalProvider()
    memory = MemoryRecord(
        id="mem_structured",
        memory_type="procedure",
        depth=2,
        content=MemoryContent(
            text="Project convention.",
            evidence=[
                EvidenceItem(
                    evidence_kind="procedure",
                    claim="Alpha report command",
                    value="make report-safe",
                    slot="command",
                )
            ],
        ),
    )

    hits = provider.retrieve(RetrievalQuery(text="Alpha report command"), [memory])

    assert len(hits) == 1
    assert hits[0].provider == "structured_evidence"
    assert hits[0].evidence_values == ["make report-safe"]
    assert hits[0].reasons == ["evidence_overlap:command"]


def test_embedding_retrieval_is_disabled_by_default() -> None:
    provider = EmbeddingRetrievalProvider()

    with pytest.raises(ValidationFailure, match="disabled by default"):
        provider.retrieve(RetrievalQuery(text="Alpha"), [])


def test_default_retrieval_does_not_call_embeddings_or_network(svc, monkeypatch) -> None:
    mem = svc.memory.propose("fact", 2, "Alpha reports use make report-safe.", None, ["project"])
    svc.memory.commit(mem.id, None)

    def fail_network(*args, **kwargs):
        raise AssertionError("network should not be used by default retrieval")

    monkeypatch.setattr(httpx, "get", fail_network)
    monkeypatch.setattr(httpx, "post", fail_network)
    monkeypatch.setattr(LMStudioClient, "embeddings", fail_network)

    result = svc.memory.query("Alpha report", None, ["project"])
    loop_result = svc.loop.run(
        "How do I generate the Alpha report?",
        None,
        scope=["project"],
        model_config={"memory_calls": True},
    )

    assert result[0].id == mem.id
    assert mem.id in loop_result.memories_used
