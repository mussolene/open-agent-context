from __future__ import annotations

import json
from hashlib import sha256
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def loads(text: str | bytes | None) -> Any:
    if text in (None, ""):
        return None
    return json.loads(text if text is not None else "null")


def hash_json(data: Any) -> str:
    return sha256(dumps(data).encode("utf-8")).hexdigest()
