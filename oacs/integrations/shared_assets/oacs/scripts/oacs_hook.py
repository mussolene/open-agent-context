from __future__ import annotations

import json
import sys

from oacs.integrations.runtime import run_cursor_hook, run_hook


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    result = (
        run_cursor_hook(payload)
        if payload.get("hook_event_name") == "sessionStart"
        else run_hook(payload)
    )
    if result is not None:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
