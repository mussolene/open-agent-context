from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from oacs.cli.main import app
from oacs.core.errors import AccessDenied


def test_vault_use_does_not_reveal_without_read_grant(svc) -> None:
    agent = svc.actors.create("agent", "VaultAgent")
    protected = svc.vault.put(
        value="OACS_TEST_SECRET_VALUE",
        value_kind="token",
        label="service token",
        actor_id=None,
        scope=["project"],
    )
    svc.capabilities.grant(
        agent.id,
        "system",
        ["protected.use", "protected.list"],
        scope=["project"],
    )

    result = svc.vault.use(protected.id, agent.id)

    assert result["revealed"] is False
    assert result["value"] is None
    assert result["protected_ref"]["id"] == protected.id
    with pytest.raises(AccessDenied):
        svc.vault.use(protected.id, agent.id, reveal=True)


def test_vault_reveal_requires_separate_secret_read_grant(svc) -> None:
    agent = svc.actors.create("agent", "VaultReader")
    protected = svc.vault.put(
        value="OACS_TEST_SECRET_VALUE",
        value_kind="token",
        label="service token",
        actor_id=None,
        scope=["project"],
    )
    svc.capabilities.grant(
        agent.id,
        "system",
        ["protected.use", "secret.read"],
        scope=["project"],
    )

    result = svc.vault.use(protected.id, agent.id, reveal=True)

    assert result["revealed"] is True
    assert result["value"] == "OACS_TEST_SECRET_VALUE"


def test_cli_vault_outputs_are_redacted_by_default(tmp_path) -> None:
    db = tmp_path / "oacs.db"
    runner = CliRunner()
    assert runner.invoke(app, ["init", "--db", str(db), "--json"]).exit_code == 0
    assert (
        runner.invoke(
            app, ["key", "init", "--db", str(db), "--passphrase", "pw", "--json"]
        ).exit_code
        == 0
    )
    put = runner.invoke(
        app,
        [
            "vault",
            "put",
            "--db",
            str(db),
            "--label",
            "service token",
            "--value",
            "OACS_TEST_SECRET_VALUE",
            "--scope",
            "project",
            "--json",
        ],
    )
    assert put.exit_code == 0, put.output
    assert "OACS_TEST_SECRET_VALUE" not in put.output
    protected_id = json.loads(put.output)["id"]

    use = runner.invoke(app, ["vault", "use", protected_id, "--db", str(db), "--json"])

    assert use.exit_code == 0, use.output
    payload = json.loads(use.output)
    assert payload["revealed"] is False
    assert payload["value"] is None
    assert "OACS_TEST_SECRET_VALUE" not in use.output
