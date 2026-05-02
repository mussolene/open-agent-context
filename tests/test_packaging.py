from __future__ import annotations

import tomllib
from pathlib import Path


def test_wheel_includes_top_level_schemas():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    wheel = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]
    sdist = pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]
    assert wheel["force-include"]["schemas"] == "schemas"
    assert sdist["force-include"]["schemas"] == "schemas"
