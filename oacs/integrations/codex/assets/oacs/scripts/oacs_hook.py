from __future__ import annotations

import json
import sys

from oacs.integrations.codex.runtime import run_hook


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    result = run_hook(payload)
    if result is not None:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
