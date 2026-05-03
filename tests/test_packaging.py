from __future__ import annotations

import tomllib
from pathlib import Path


def test_wheel_includes_top_level_schemas():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    wheel = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]
    sdist = pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]
    assert wheel["force-include"]["schemas"] == "schemas"
    assert sdist["force-include"]["schemas"] == "schemas"


def test_public_package_metadata_is_release_ready():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    optional = project["optional-dependencies"]
    urls = project["urls"]

    assert project["name"] == "oacs"
    assert project["version"] == "0.3.2a1"
    assert "Open Agent Context Standard" in project["description"]
    assert "Development Status :: 3 - Alpha" in project["classifiers"]
    assert "License :: OSI Approved :: Apache Software License" in project["classifiers"]
    assert "release" in optional
    assert "twine>=5" in optional["release"]
    assert urls["Repository"].endswith("/open-agent-context")
    assert urls["Changelog"].endswith("/CHANGELOG.md")


def test_release_workflow_uses_trusted_publishing():
    workflow = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@release/v1" in workflow
    assert "https://test.pypi.org/legacy/" in workflow
    assert "target == 'pypi'" in workflow
    assert "github.event_name == 'push'" in workflow
    assert "contains(github.ref_name, 'a')" in workflow
    assert "contains(github.ref_name, 'b')" in workflow
    assert "contains(github.ref_name, 'rc')" in workflow
