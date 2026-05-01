from __future__ import annotations


def call_local_tool(name: str, payload: dict[str, object]) -> dict[str, object]:
    if name == "local_echo":
        return {"echo": payload}
    raise ValueError(f"unknown local tool: {name}")
