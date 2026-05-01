from __future__ import annotations

import pytest

from oacs.llm.lmstudio import LMStudioClient


def test_lmstudio_optional_integration():
    client = LMStudioClient(timeout_sec=1)
    try:
        text = client.chat("Return the word ok.")
    except RuntimeError as exc:
        pytest.skip(str(exc))
    assert text
