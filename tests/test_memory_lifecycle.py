from __future__ import annotations


def test_memory_propose_commit_query_read(svc):
    mem = svc.memory.propose("procedure", 2, "Alpha uses make report-safe.", None, ["project"])
    committed = svc.memory.commit(mem.id, None)
    assert committed.lifecycle_status == "active"
    results = svc.memory.query("Alpha report", None, ["project"])
    assert results[0].id == mem.id
    assert svc.memory.read(mem.id, None).content.text == "Alpha uses make report-safe."


def test_forget_blocks_normal_read(svc):
    mem = svc.memory.propose("fact", 2, "secret forgotten text", None, ["project"])
    svc.memory.commit(mem.id, None)
    svc.memory.forget(mem.id, None)
    try:
        svc.memory.read(mem.id, None)
    except Exception as exc:
        assert "forgotten" in str(exc)
    else:
        raise AssertionError("forgotten memory was readable")
