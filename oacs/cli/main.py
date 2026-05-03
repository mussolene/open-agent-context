from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from rich import print as rprint

from oacs import __version__
from oacs.app import OacsServices, services
from oacs.benchmark.external import AmaBenchImporter, MemoryArenaImporter
from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.models import BenchmarkTask
from oacs.benchmark.packs import download_task_pack, load_task_pack, tasks_from_pack
from oacs.benchmark.reports import compare_runs, select_comparison_runs
from oacs.benchmark.runner import MemoryCriticalBenchmark
from oacs.conformance import validate_conformance
from oacs.context.reducer import reduce_capsule
from oacs.core.config import OacsConfig
from oacs.core.errors import MemoryDecryptError, NotFound
from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.crypto.hybrid_pqc import HybridPQCKeyProvider
from oacs.rules.models import RuleManifest
from oacs.skills.models import SkillManifest
from oacs.skills.runner import run_skill
from oacs.tools.models import ToolBinding

app = typer.Typer(help="acs - Agent Context Shell")
actor_app = typer.Typer()
key_app = typer.Typer()
memory_app = typer.Typer()
context_app = typer.Typer()
capsule_app = typer.Typer()
rule_app = typer.Typer()
skill_app = typer.Typer()
tool_app = typer.Typer()
evidence_app = typer.Typer()
mcp_app = typer.Typer()
loop_app = typer.Typer()
benchmark_app = typer.Typer()
server_app = typer.Typer()
audit_app = typer.Typer()
capability_app = typer.Typer()
checkpoint_app = typer.Typer()
policy_app = typer.Typer()
conformance_app = typer.Typer()

app.add_typer(actor_app, name="actor")
app.add_typer(capability_app, name="capability")
app.add_typer(key_app, name="key")
app.add_typer(memory_app, name="memory")
app.add_typer(context_app, name="context")
app.add_typer(capsule_app, name="capsule")
app.add_typer(rule_app, name="rule")
app.add_typer(skill_app, name="skill")
app.add_typer(tool_app, name="tool")
app.add_typer(evidence_app, name="evidence")
app.add_typer(mcp_app, name="mcp")
app.add_typer(loop_app, name="loop")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(server_app, name="server")
app.add_typer(audit_app, name="audit")
app.add_typer(checkpoint_app, name="checkpoint")
app.add_typer(policy_app, name="policy")
app.add_typer(conformance_app, name="conformance")


DbOpt = Annotated[str | None, typer.Option("--db")]
JsonOpt = Annotated[bool, typer.Option("--json")]
ActorOpt = Annotated[str | None, typer.Option("--actor")]
AgentOpt = Annotated[str | None, typer.Option("--agent")]
ScopeOpt = Annotated[list[str] | None, typer.Option("--scope")]
PassOpt = Annotated[str | None, typer.Option("--passphrase")]


def emit(data: object, json_out: bool) -> None:
    if json_out:
        typer.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        rprint(data)


def fail(message: str) -> None:
    raise typer.BadParameter(message)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"acs {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Show the acs version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    _ = version


def _public_recent(row: dict[str, object]) -> dict[str, object]:
    keys = (
        "id",
        "kind",
        "uri",
        "operation",
        "target_id",
        "status",
        "created_at",
        "updated_at",
    )
    return {
        key: row.get(key)
        for key in keys
        if key in row
    }


def _policy_payload_text(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, default=str)


def _enforce_policy(
    db: str | None,
    operation: str,
    payload: dict[str, object],
    json_out: bool,
) -> list[dict[str, object]]:
    checks = services(db, require_key=False).rules.check(operation, payload)
    failures = [item for item in checks if item.blocking]
    if failures:
        emit(
            {
                "status": "blocked",
                "operation": operation,
                "policy_results": [item.model_dump() for item in checks],
            },
            json_out,
        )
        raise typer.Exit(2)
    return [item.model_dump() for item in checks if item.status != "pass"]


@app.command()
def init(
    db: DbOpt = None,
    project: Annotated[bool, typer.Option("--project")] = False,
    json_out: JsonOpt = False,
) -> None:
    resolved_db = db or (".agent/oacs/oacs.db" if project else None)
    svc = services(resolved_db, require_key=False)
    emit({"db": str(svc.config.db_path), "status": "initialized", "project": project}, json_out)


@app.command()
def status(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    key_status = svc.key_provider.status()
    memory_health: dict[str, object] = {
        "status": "WARN",
        "checked_records": 0,
        "unreadable_records": 0,
        "warnings": [
            {"type": "MemoryDecryptHealthSkipped", "reason": "key is locked or unavailable"}
        ],
    }
    if key_status.available and key_status.unlocked:
        memory_health = services(db).memory.decrypt_health()
    tables = (
        "memory_records",
        "context_capsules",
        "evidence_refs",
        "audit_events",
        "task_traces",
        "rules",
    )
    emit(
        {
            "db": str(svc.config.db_path),
            "db_exists": svc.config.db_path.exists(),
            "base_dir": str(svc.config.base_dir),
            "key": key_status.__dict__,
            "memory_decrypt_health": memory_health,
            "counts": {table: len(svc.store.list(table, limit=None)) for table in tables},
        },
        json_out,
    )


@app.command()
def doctor(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db)
    memory_health = svc.memory.decrypt_health()
    status_value = "PASS" if memory_health["status"] == "PASS" else "FAIL"
    emit({"status": status_value, "memory_decrypt_health": memory_health}, json_out)
    if status_value != "PASS":
        raise typer.Exit(1)


@app.command()
def resume(
    scope: ScopeOpt = None,
    limit: Annotated[int, typer.Option("--limit", min=1)] = 5,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    requested_scope = scope or []
    checkpoint_rows = svc.store.list(
        "task_traces",
        filters={"status": "active"},
        order_by=[("created_at", "desc"), ("id", "desc")],
        limit=limit,
    )
    evidence_rows = svc.evidence.list_refs(kind="tool_result", limit=limit)
    memory_rows = svc.store.list(
        "memory_records",
        filters={"status": "active"},
        order_by=[("updated_at", "desc"), ("id", "desc")],
        limit=limit,
    )
    capsule_rows = svc.store.list(
        "context_capsules",
        filters={"status": "active"},
        order_by=[("updated_at", "desc"), ("id", "desc")],
        limit=limit,
    )
    audit_rows = list(reversed(svc.audit.list()))[:limit]
    latest_checkpoint = checkpoint_rows[0]["payload"] if checkpoint_rows else None
    emit(
        {
            "db": str(svc.config.db_path),
            "scope": requested_scope,
            "latest_checkpoint": latest_checkpoint,
            "recent_checkpoints": [row["payload"] for row in checkpoint_rows],
            "recent_tool_results": [
                _public_recent(row) | {"payload": row.get("public_payload")}
                for row in evidence_rows
            ],
            "recent_memories": [
                {
                    "id": row["id"],
                    "memory_type": row["memory_type"],
                    "depth": row["depth"],
                    "lifecycle_status": row["lifecycle_status"],
                    "scope": row["scope"],
                    "updated_at": row["updated_at"],
                }
                for row in memory_rows
            ],
            "recent_context_capsules": [
                _public_recent(row) | {"purpose": row.get("purpose")}
                for row in capsule_rows
            ],
            "recent_audit": [
                _public_recent(row) | {"metadata": row.get("metadata")}
                for row in audit_rows
            ],
        },
        json_out,
    )


@app.command("run")
def run_command(
    command: Annotated[list[str], typer.Argument(help="Command to execute after --")],
    label: Annotated[str, typer.Option("--label")],
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    namespace: Annotated[str, typer.Option("--namespace")] = "default",
    timeout: Annotated[int, typer.Option("--timeout", min=1)] = 300,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    if not command:
        raise typer.BadParameter("command is required")
    command_text = " ".join(command)
    _enforce_policy(db, "tool.call", {"text": command_text}, json_out)
    try:
        completed = subprocess.run(
            command,
            cwd=Path.cwd(),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        status_text = "completed" if completed.returncode == 0 else "failed"
        output = {
            "command": command,
            "label": label,
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-8000:],
        }
    except subprocess.TimeoutExpired as exc:
        status_text = "timeout"
        output = {
            "command": command,
            "label": label,
            "exit_code": 124,
            "stdout": (exc.stdout or "")[-8000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-8000:] if isinstance(exc.stderr, str) else "",
            "timeout": timeout,
        }
    policy_warnings = _enforce_policy(
        db,
        "evidence.ingest",
        {"text": _policy_payload_text(output)},
        json_out,
    )
    svc = services(db, require_key=False)
    result = svc.evidence.ingest_tool_result(
        tool_id=f"run_{hash_json(command_text)[:12]}",
        tool_name=label,
        tool_type="local_cli",
        output=output,
        input_payload={"command": command, "timeout": timeout},
        actor_id=actor,
        scope=scope or [],
        namespace=namespace,
        source_uri=f"command://{hash_json(command_text)}",
        status=status_text,
        executed=True,
    )
    emit(result.model_dump() | {"policy_warnings": policy_warnings}, json_out)


@key_app.command("init")
def key_init(passphrase: PassOpt, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    if not passphrase:
        raise typer.BadParameter("--passphrase is required")
    cfg = OacsConfig.from_values(db, passphrase)
    cfg.base_dir.mkdir(parents=True, exist_ok=True)
    svc = services(db, require_key=False)
    metadata = svc.key_provider.generate(passphrase)
    emit(
        {
            "status": "initialized",
            "public": {k: metadata[k] for k in ("provider", "algorithm_name", "kdf")},
        },
        json_out,
    )


@key_app.command("unlock")
def key_unlock(passphrase: PassOpt, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    svc.key_provider.unwrap_key(passphrase or "")
    emit({"status": "unlocked"}, json_out)


@key_app.command("lock")
def key_lock(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    svc.key_provider.lock()
    emit({"status": "locked"}, json_out)


@key_app.command("status")
def key_status(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    status = svc.key_provider.status()
    pq = HybridPQCKeyProvider().status()
    emit({"local": status.__dict__, "hybrid_pqc": pq.__dict__}, json_out)


@key_app.command("export-public")
def key_export_public(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    emit(svc.key_provider.export_public(), json_out)


@actor_app.command("create")
def actor_create(
    type: Annotated[str, typer.Option("--type")],
    name: Annotated[str, typer.Option("--name")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    actor = svc.actors.create(type, name)  # type: ignore[arg-type]
    if type == "human":
        svc.capabilities.grant(actor.id, "system", ["*"], memory_depth_allowed=5)
    emit(actor.model_dump(), json_out)


@actor_app.command("list")
def actor_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([a.model_dump() for a in services(db, require_key=False).actors.list()], json_out)


@capability_app.command("list")
def capability_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(
        [
            cap.model_dump()
            for cap in services(db, require_key=False).capabilities.list_definitions()
        ],
        json_out,
    )


@capability_app.command("inspect")
def capability_inspect(capability_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        capability = services(db, require_key=False).capabilities.inspect_definition(capability_id)
    except KeyError as exc:
        fail(str(exc))
    emit(capability.model_dump(), json_out)


@capability_app.command("grants")
def capability_grants(actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    if actor:
        grants = [grant.model_dump() for grant in svc.capabilities.for_actor(actor)]
    else:
        grants = svc.store.list("capability_grants", order_by=[("created_at", "asc")])
    emit(grants, json_out)


@capability_app.command("grant-shared-memory")
def capability_grant_shared_memory(
    subject: Annotated[str, typer.Option("--subject")],
    issuer: Annotated[str, typer.Option("--issuer")] = "system",
    scope: ScopeOpt = None,
    depth: Annotated[int, typer.Option("--depth")] = 2,
    namespace: Annotated[list[str] | None, typer.Option("--namespace")] = None,
    expires_at: Annotated[str | None, typer.Option("--expires-at")] = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    grant = services(db, require_key=False).capabilities.grant_shared_memory(
        subject_actor_id=subject,
        issuer_actor_id=issuer,
        scope=scope or [],
        memory_depth_allowed=depth,
        namespaces_allowed=namespace or ["default"],
        expires_at=expires_at,
    )
    emit({"grant": grant.model_dump(), "shared_memory": True}, json_out)


@capability_app.command("grant")
def capability_grant(
    subject: Annotated[str, typer.Option("--subject")],
    operation: Annotated[list[str], typer.Option("--operation")],
    issuer: Annotated[str, typer.Option("--issuer")] = "system",
    scope: ScopeOpt = None,
    depth: Annotated[int, typer.Option("--depth")] = 2,
    namespace: Annotated[list[str] | None, typer.Option("--namespace")] = None,
    tool: Annotated[list[str] | None, typer.Option("--tool")] = None,
    skill: Annotated[list[str] | None, typer.Option("--skill")] = None,
    deny: Annotated[list[str] | None, typer.Option("--deny")] = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    grant = services(db, require_key=False).capabilities.grant(
        subject,
        issuer,
        list(operation),
        scope=scope,
        memory_depth_allowed=depth,
        namespaces_allowed=namespace,
        tools_allowed=tool,
        skills_allowed=skill,
        denied_operations=deny,
    )
    emit(grant.model_dump(), json_out)


@capability_app.command("grant-tool")
def capability_grant_tool(
    subject: Annotated[str, typer.Option("--subject")],
    tool: Annotated[list[str], typer.Option("--tool")],
    issuer: Annotated[str, typer.Option("--issuer")] = "system",
    scope: ScopeOpt = None,
    namespace: Annotated[list[str] | None, typer.Option("--namespace")] = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    grant = services(db, require_key=False).capabilities.grant(
        subject,
        issuer,
        ["tool.call"],
        scope=scope,
        namespaces_allowed=namespace,
        tools_allowed=tool,
    )
    emit(grant.model_dump(), json_out)


@memory_app.command("observe")
def memory_observe(
    text: Annotated[str, typer.Option("--text")],
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    mem = svc.memory.observe(text, actor, scope or [])
    svc.audit.record("memory.observe", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("propose")
def memory_propose(
    type: Annotated[str, typer.Option("--type")],
    depth: Annotated[int, typer.Option("--depth")],
    text: Annotated[str, typer.Option("--text")],
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    policy_warnings = _enforce_policy(db, "memory.propose", {"text": text}, json_out)
    svc = services(db)
    mem = svc.memory.propose(type, depth, text, actor, scope or [])
    svc.audit.record("memory.propose", actor, mem.id)
    emit(mem.model_dump() | {"policy_warnings": policy_warnings}, json_out)


@memory_app.command("commit")
def memory_commit(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    mem = svc.memory.commit(memory_id, actor)
    svc.audit.record("memory.commit", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("query")
def memory_query(
    query: Annotated[str, typer.Option("--query", "-q")] = "",
    strict: Annotated[bool, typer.Option("--strict")] = False,
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    try:
        result = svc.memory.query(query, actor, scope or [], strict=strict)
    except MemoryDecryptError as exc:
        emit({"error": "MemoryDecryptError", **exc.record}, json_out)
        raise typer.Exit(2) from exc
    svc.audit.record("memory.query", actor, None, {"query_hash": hash_json(query)})
    payload: object = [m.model_dump() for m in result]
    if svc.memory.last_warnings:
        payload = {"memories": payload, "warnings": svc.memory.last_warnings}
    emit(payload, json_out)


@memory_app.command("read")
def memory_read(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    try:
        mem = svc.memory.read(memory_id, actor)
    except MemoryDecryptError as exc:
        emit({"error": "MemoryDecryptError", **exc.record}, json_out)
        raise typer.Exit(2) from exc
    svc.audit.record("memory.read", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("doctor")
def memory_doctor(actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db)
    result = svc.memory.decrypt_health(actor)
    emit(result, json_out)
    if result["status"] != "PASS":
        raise typer.Exit(1)


@memory_app.command("quarantine")
def memory_quarantine(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    result = svc.memory.quarantine(memory_id, actor)
    svc.audit.record("memory.quarantine", actor, memory_id)
    emit(result, json_out)


@memory_app.command("export-readable")
def memory_export_readable(
    actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    memories = svc.memory.query("", actor, strict=False)
    result = {
        "memories": [memory.model_dump() for memory in memories],
        "warnings": svc.memory.last_warnings,
    }
    svc.audit.record("memory.export-readable", actor, None, {"count": len(memories)})
    emit(result, json_out)


@memory_app.command("purge-unreadable")
def memory_purge_unreadable(
    dry_run: Annotated[bool, typer.Option("--dry-run/--apply")] = True,
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    result = svc.memory.purge_unreadable(actor, dry_run=dry_run)
    svc.audit.record("memory.purge-unreadable", actor, None, result)
    emit(result, json_out)


@memory_app.command("correct")
def memory_correct(
    memory_id: str,
    text: Annotated[str, typer.Option("--text")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    mem = svc.memory.correct(memory_id, text, actor)
    svc.audit.record("memory.correct", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("deprecate")
def memory_deprecate(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    mem = svc.memory.deprecate(memory_id, actor)
    svc.audit.record("memory.deprecate", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("supersede")
def memory_supersede(
    memory_id: str,
    replacement_id: str,
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    mem = svc.memory.supersede(memory_id, replacement_id, actor)
    svc.audit.record("memory.supersede", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("forget")
def memory_forget(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    mem = svc.memory.forget(memory_id, actor)
    svc.audit.record("memory.forget", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("blur")
def memory_blur(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    mem = svc.memory.blur(memory_id, actor)
    svc.audit.record("memory.blur", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("sharpen")
def memory_sharpen(
    memory_id: str,
    evidence_ref: Annotated[str, typer.Option("--evidence")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    mem = svc.memory.sharpen(memory_id, evidence_ref, actor)
    svc.audit.record("memory.sharpen", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("audit")
def memory_audit(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db, require_key=False).audit.list(), json_out)


@memory_app.command("export")
def memory_export(actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db)
    result = svc.memory.export_all(actor)
    svc.audit.record("memory.export", actor, None, {"count": len(result)})
    emit(result, json_out)


@memory_app.command("import")
def memory_import(
    file: Annotated[Path, typer.Option("--file")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    data = json.loads(file.read_text(encoding="utf-8"))
    imported = [
        svc.memory.propose(
            item["memory_type"],
            item["depth"],
            item["content"]["text"],
            actor,
            item.get("scope", []),
        )
        for item in data
    ]
    svc.audit.record("memory.import", actor, None, {"count": len(imported)})
    emit([m.model_dump() for m in imported], json_out)


@context_app.command("build")
def context_build(
    intent: Annotated[str, typer.Option("--intent")],
    actor: ActorOpt = None,
    agent: AgentOpt = None,
    scope: ScopeOpt = None,
    budget: Annotated[int, typer.Option("--budget")] = 4000,
    strict: Annotated[bool, typer.Option("--strict")] = False,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    try:
        capsule = svc.context.build(intent, actor, agent, scope or [], budget, strict=strict)
    except MemoryDecryptError as exc:
        emit({"error": "MemoryDecryptError", **exc.record}, json_out)
        raise typer.Exit(2) from exc
    svc.audit.record("context.build", actor, capsule.id)
    payload: object = capsule.model_dump()
    if svc.context.last_warnings:
        payload = {"capsule": payload, "warnings": svc.context.last_warnings}
    emit(payload, json_out)


@context_app.command("explain")
def context_explain(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    result = svc.context.explain(capsule_id, actor)
    svc.audit.record("context.explain", actor, capsule_id)
    emit(result, json_out)


@context_app.command("reduce")
def context_reduce(
    capsule_id: str,
    max_memories: Annotated[int, typer.Option("--max-memories")] = 5,
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    capsule = reduce_capsule(svc.context.read(capsule_id, actor), max_memories)
    svc.audit.record("context.reduce", actor, capsule_id)
    emit(capsule.model_dump(), json_out)


@context_app.command("expand")
def context_expand(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    capsule = svc.context.read(capsule_id, actor)
    svc.audit.record("context.expand", actor, capsule_id)
    emit(capsule.model_dump(), json_out)


@context_app.command("lock")
def context_lock(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    result = svc.context.set_status(capsule_id, actor, "locked")
    svc.audit.record("context.lock", actor, capsule_id)
    emit(result, json_out)


@context_app.command("export")
def context_export(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    capsule = svc.context.export_capsule(capsule_id, actor)
    svc.audit.record("context.export", actor, capsule_id)
    emit(capsule.model_dump(), json_out)


@context_app.command("import")
def context_import(
    file: Annotated[Path, typer.Option("--file")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    capsule = svc.context.import_capsule(json.loads(file.read_text(encoding="utf-8")), actor)
    svc.audit.record("context.import", actor, capsule.id)
    emit(capsule.model_dump(), json_out)


@context_app.command("validate")
def context_validate(
    file: Annotated[Path, typer.Option("--file")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    payload = json.loads(file.read_text(encoding="utf-8"))
    requires_key = payload.get("export_type") == "context_capsule_export"
    result = services(db, require_key=requires_key).context.validate_payload(payload)
    emit(result, json_out)


@capsule_app.command("create")
def capsule_create(
    intent: Annotated[str, typer.Option("--intent")] = "manual",
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    context_build(intent, actor, None, [], 4000, False, db, json_out)


@capsule_app.command("inspect")
def capsule_inspect(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.read(capsule_id, actor).model_dump(), json_out)


@capsule_app.command("mount")
def capsule_mount(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.set_status(capsule_id, actor, "mounted"), json_out)


@capsule_app.command("unmount")
def capsule_unmount(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.set_status(capsule_id, actor, "active"), json_out)


@capsule_app.command("grant")
def capsule_grant(
    capsule_id: str,
    subject: Annotated[str, typer.Option("--subject")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    svc.context.read(capsule_id, None)
    emit(svc.capabilities.grant(subject, "system", ["context.export"]).model_dump(), json_out)


@capsule_app.command("revoke")
def capsule_revoke(
    capsule_id: str,
    subject: Annotated[str, typer.Option("--subject")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    svc.context.read(capsule_id, actor)
    revoked = 0
    for grant in svc.store.list(
        "capability_grants", filters={"subject_actor_id": subject, "status": "active"}
    ):
        if "context.export" in grant["allowed_operations"] or "*" in grant["allowed_operations"]:
            grant["status"] = "revoked"
            grant["updated_at"] = now_iso()
            svc.store.put_json("capability_grants", grant)
            revoked += 1
    emit({"capsule_id": capsule_id, "subject": subject, "revoked": revoked}, json_out)


@capsule_app.command("validate")
def capsule_validate(
    file: Annotated[Path, typer.Option("--file")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    context_validate(file, db, json_out)


@capsule_app.command("export")
def capsule_export(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    context_export(capsule_id, actor, db, json_out)


@capsule_app.command("import")
def capsule_import(
    file: Annotated[Path, typer.Option("--file")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    context_import(file, actor, db, json_out)


@rule_app.command("add")
def rule_add(
    name: Annotated[str, typer.Option("--name")],
    content: Annotated[str, typer.Option("--content")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    rule = services(db, require_key=False).rules.add(
        RuleManifest(name=name, rule_kind="project_rule", content=content)
    )
    emit(rule.model_dump(), json_out)


@policy_app.command("add-deny-pattern")
def policy_add_deny_pattern(
    pattern: str,
    name: Annotated[str | None, typer.Option("--name")] = None,
    applies_to: Annotated[list[str] | None, typer.Option("--applies-to")] = None,
    blocking: Annotated[bool, typer.Option("--blocking/--warn-only")] = True,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    rule = services(db, require_key=False).rules.add(
        RuleManifest(
            name=name or f"deny_pattern_{hash_json(pattern)[:8]}",
            rule_kind="deny_pattern",
            content=pattern,
            applies_to=applies_to or ["memory.propose", "tool.call", "evidence.ingest"],
            enforcement_mode="block" if blocking else "warn",
            blocking=blocking,
            priority=10,
        )
    )
    emit(rule.model_dump(), json_out)


@conformance_app.command("validate")
def conformance_validate(
    conformance_root: Annotated[Path | None, typer.Option("--conformance-root")] = None,
    schema_root: Annotated[Path | None, typer.Option("--schema-root")] = None,
    json_out: JsonOpt = False,
) -> None:
    result = validate_conformance(conformance_root, schema_root)
    emit(result, json_out)
    if not result["valid"]:
        raise typer.Exit(1)


@checkpoint_app.command("add")
def checkpoint_add(
    task: Annotated[str, typer.Option("--task")],
    summary: Annotated[str, typer.Option("--summary")],
    next_step: Annotated[str | None, typer.Option("--next")] = None,
    evidence: Annotated[list[str] | None, typer.Option("--evidence")] = None,
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    namespace: Annotated[str, typer.Option("--namespace")] = "default",
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    payload = {
        "kind": "checkpoint",
        "task": task,
        "summary": summary,
        "next": next_step,
        "evidence_refs": evidence or [],
    }
    policy_warnings = _enforce_policy(
        db, "task.checkpoint", {"text": _policy_payload_text(payload)}, json_out
    )
    svc = services(db, require_key=False)
    now = now_iso()
    record = {
        "id": new_id("trace"),
        "payload": payload,
        "created_at": now,
        "updated_at": now,
        "status": "active",
        "namespace": namespace,
        "scope": scope or [],
        "owner_actor_id": actor,
        "content_hash": hash_json(payload),
    }
    svc.store.put_json("task_traces", record)
    svc.audit.record(
        "task.checkpoint",
        actor,
        str(record["id"]),
        {"task_hash": hash_json(task), "evidence_refs": evidence or []},
    )
    emit(record | {"policy_warnings": policy_warnings}, json_out)


@checkpoint_app.command("latest")
def checkpoint_latest(
    task: Annotated[str | None, typer.Option("--task")] = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    rows = svc.store.list(
        "task_traces",
        filters={"status": "active"},
        order_by=[("created_at", "desc"), ("id", "desc")],
        limit=None,
    )
    for row in rows:
        payload = row.get("payload")
        if (
            isinstance(payload, dict)
            and payload.get("kind") == "checkpoint"
            and (task is None or payload.get("task") == task)
        ):
            emit(row, json_out)
            return
    raise typer.BadParameter("checkpoint not found")


@checkpoint_app.command("list")
def checkpoint_list(
    task: Annotated[str | None, typer.Option("--task")] = None,
    limit: Annotated[int, typer.Option("--limit", min=1)] = 20,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    rows = svc.store.list(
        "task_traces",
        filters={"status": "active"},
        order_by=[("created_at", "desc"), ("id", "desc")],
        limit=None,
    )
    checkpoints = [
        row
        for row in rows
        if isinstance(row.get("payload"), dict)
        and row["payload"].get("kind") == "checkpoint"
        and (task is None or row["payload"].get("task") == task)
    ][:limit]
    emit(checkpoints, json_out)


@rule_app.command("list")
def rule_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([r.model_dump() for r in services(db, require_key=False).rules.list()], json_out)


@rule_app.command("check")
def rule_check(
    operation: Annotated[str, typer.Option("--operation")] = "context.build",
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit([r.model_dump() for r in services(db, require_key=False).rules.check(operation)], json_out)


@rule_app.command("explain")
def rule_explain(rule_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    rules = [r for r in services(db, require_key=False).rules.list() if r.id == rule_id]
    emit(rules[0].model_dump() if rules else {"error": "not found"}, json_out)


@skill_app.command("add")
def skill_add(
    file: Annotated[Path, typer.Option("--file")], db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    skill = services(db, require_key=False).skills.add(
        SkillManifest(**json.loads(file.read_text()))
    )
    emit(skill.model_dump(), json_out)


@skill_app.command("scan")
def skill_scan(folder: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([s.model_dump() for s in services(db, require_key=False).skills.scan(folder)], json_out)


@skill_app.command("list")
def skill_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([s.model_dump() for s in services(db, require_key=False).skills.list()], json_out)


@skill_app.command("inspect")
def skill_inspect(skill_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        emit(services(db, require_key=False).skills.inspect(skill_id).model_dump(), json_out)
    except KeyError as exc:
        fail(str(exc))


@skill_app.command("activate")
def skill_activate(skill_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        emit(services(db, require_key=False).skills.activate(skill_id).model_dump(), json_out)
    except KeyError as exc:
        fail(str(exc))


@skill_app.command("run")
def skill_run(
    skill_id: str,
    payload: Annotated[str, typer.Option("--payload")] = "{}",
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    skill = svc.skills.inspect(skill_id)
    check_scope = skill.scope or scope or []
    if not (
        svc.policy.allows(
            actor, "skill.run", scope=check_scope, namespace=skill.namespace, skill=skill.id
        )
        or svc.policy.allows(
            actor, "skill.run", scope=check_scope, namespace=skill.namespace, skill=skill.name
        )
    ):
        svc.policy.require(
            actor, "skill.run", scope=check_scope, namespace=skill.namespace, skill=skill.id
        )
    parsed_payload = json.loads(payload)
    if not isinstance(parsed_payload, dict):
        raise typer.BadParameter("--payload must be a JSON object")
    parsed_payload.setdefault("db", db)
    parsed_payload.setdefault("actor", actor)
    parsed_payload.setdefault("scope", scope or [])
    result = run_skill(skill, parsed_payload)
    svc.audit.record("skill.run", actor, skill.id, {"status": "completed"})
    emit(result, json_out)


@tool_app.command("add")
def tool_add(
    name: Annotated[str, typer.Option("--name")],
    type: Annotated[str, typer.Option("--type")] = "python_function",
    command: Annotated[str | None, typer.Option("--command")] = None,
    input_schema: Annotated[Path | None, typer.Option("--input-schema")] = None,
    output_schema: Annotated[Path | None, typer.Option("--output-schema")] = None,
    http_url: Annotated[str | None, typer.Option("--http-url")] = None,
    http_method: Annotated[str, typer.Option("--http-method")] = "POST",
    allow_network: Annotated[bool, typer.Option("--allow-network")] = False,
    description: Annotated[str, typer.Option("--description")] = "",
    risk_level: Annotated[str, typer.Option("--risk")] = "low",
    namespace: Annotated[str, typer.Option("--namespace")] = "default",
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(
        services(db, require_key=False)
        .tools.add(
            ToolBinding(
                name=name,
                type=type,
                command=command,
                http=_http_config(http_url, http_method, allow_network),
                description=description,
                risk_level=risk_level,
                namespace=namespace,
                scope=scope or [],
                input_schema=_schema_file(input_schema),
                output_schema=_schema_file(output_schema),
            )
        )
        .model_dump(),
        json_out,
    )


@tool_app.command("list")
def tool_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([t.model_dump() for t in services(db, require_key=False).tools.list()], json_out)


@tool_app.command("inspect")
def tool_inspect(tool_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        emit(services(db, require_key=False).tools.inspect(tool_id).model_dump(), json_out)
    except KeyError as exc:
        fail(str(exc))


@tool_app.command("call")
def tool_call(
    name: str,
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    payload: Annotated[str, typer.Option("--payload")] = "{}",
    execute_mcp: Annotated[bool, typer.Option("--execute-mcp")] = False,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    parsed_payload = json.loads(payload)
    if not isinstance(parsed_payload, dict):
        raise typer.BadParameter("--payload must be a JSON object")
    result = svc.tool_runner.call(
        name,
        parsed_payload,
        actor_id=actor,
        scope=scope,
        execute_mcp=execute_mcp,
    )
    emit(result.model_dump(), json_out)


@tool_app.command("ingest-result")
def tool_ingest_result(
    tool_id: Annotated[str, typer.Option("--tool-id")],
    output: Annotated[str, typer.Option("--output")],
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    input_payload: Annotated[str, typer.Option("--input")] = "{}",
    tool_name: Annotated[str | None, typer.Option("--tool-name")] = None,
    tool_type: Annotated[str, typer.Option("--tool-type")] = "external",
    namespace: Annotated[str, typer.Option("--namespace")] = "default",
    source_uri: Annotated[str | None, typer.Option("--source-uri")] = None,
    status: Annotated[str, typer.Option("--status")] = "completed",
    executed: Annotated[bool, typer.Option("--executed/--not-executed")] = True,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    parsed_input = json.loads(input_payload)
    parsed_output = json.loads(output)
    if not isinstance(parsed_input, dict):
        raise typer.BadParameter("--input must be a JSON object")
    if not isinstance(parsed_output, dict):
        raise typer.BadParameter("--output must be a JSON object")
    policy_warnings = _enforce_policy(
        db,
        "evidence.ingest",
        {"text": _policy_payload_text({"input": parsed_input, "output": parsed_output})},
        json_out,
    )
    result = svc.evidence.ingest_tool_result(
        tool_id=tool_id,
        tool_name=tool_name,
        tool_type=tool_type,
        output=parsed_output,
        input_payload=parsed_input,
        actor_id=actor,
        scope=scope or [],
        namespace=namespace,
        source_uri=source_uri,
        status=status,
        executed=executed,
    )
    emit(result.model_dump() | {"policy_warnings": policy_warnings}, json_out)


@evidence_app.command("list")
def evidence_list(
    kind: Annotated[str | None, typer.Option("--kind")] = None,
    namespace: Annotated[str | None, typer.Option("--namespace")] = None,
    limit: Annotated[int, typer.Option("--limit", min=0)] = 50,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    records = services(db, require_key=False).evidence.list_refs(
        kind=kind,
        namespace=namespace,
        limit=limit,
    )
    emit(records, json_out)


@evidence_app.command("inspect")
def evidence_inspect(evidence_ref: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        emit(services(db, require_key=False).evidence.get(evidence_ref), json_out)
    except NotFound as exc:
        fail(str(exc))


def _schema_file(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise typer.BadParameter("schema file must contain a JSON object")
    return payload


def _http_config(url: str | None, method: str, allow_network: bool) -> dict[str, object] | None:
    if url is None and not allow_network:
        return None
    if not url:
        raise typer.BadParameter("--http-url is required for HTTP tool config")
    return {"url": url, "method": method.upper(), "allow_network": allow_network}


@mcp_app.command("import")
def mcp_import(file: Path, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    imported = svc.mcp.import_config(str(file))
    for binding in imported:
        svc.audit.record("mcp.import", None, binding.id)
    emit([m.model_dump() for m in imported], json_out)


@mcp_app.command("list")
def mcp_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit([m.model_dump() for m in services(db, require_key=False).mcp.list()], json_out)


@mcp_app.command("inspect")
def mcp_inspect(mcp_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    try:
        emit(services(db, require_key=False).mcp.inspect(mcp_id).model_dump(), json_out)
    except KeyError as exc:
        fail(str(exc))


@loop_app.command("run")
def loop_run(
    request: Annotated[str, typer.Option("--request")],
    actor: ActorOpt = None,
    agent: AgentOpt = None,
    scope: ScopeOpt = None,
    budget: Annotated[int, typer.Option("--budget")] = 4000,
    memory_calls: Annotated[
        bool | None, typer.Option("--memory-calls/--no-memory-calls")
    ] = None,
    allow_deepening: Annotated[bool, typer.Option("--deepening/--no-deepening")] = True,
    context_policy: Annotated[str, typer.Option("--context-policy")] = "auto",
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    model_config: dict[str, object] = {
        "allow_deepening": allow_deepening,
        "context_policy": context_policy,
    }
    if memory_calls is not None:
        model_config["memory_calls"] = memory_calls
    emit(
        services(db)
        .loop.run(
            request,
            actor,
            agent,
            scope or [],
            budget,
            model_config=model_config,
        )
        .model_dump(),
        json_out,
    )


@loop_app.command("explain")
def loop_explain(json_out: JsonOpt = False) -> None:
    emit(
        {
            "steps": [
                "observe",
                "classify",
                "retrieve",
                "build_context",
                "apply_rules",
                "act",
                "propose_memory",
                "audit",
            ]
        },
        json_out,
    )


@benchmark_app.command("generate")
def benchmark_generate(
    suite: Annotated[str, typer.Option("--suite")] = "memory_critical",
    count: Annotated[int, typer.Option("--count")] = 20,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db, require_key=False)
    tasks = SyntheticTaskGenerator().generate(suite, count)
    _store_benchmark_tasks(svc, tasks)
    emit([t.model_dump() for t in tasks], json_out)


@benchmark_app.command("import-memoryarena")
def benchmark_import_memoryarena(
    subset: Annotated[str, typer.Option("--subset")] = "group_travel_planner",
    count: Annotated[int, typer.Option("--count")] = 5,
    file: Annotated[Path | None, typer.Option("--file")] = None,
    url: Annotated[str | None, typer.Option("--url")] = None,
    allow_network: Annotated[bool, typer.Option("--allow-network")] = False,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    importer = MemoryArenaImporter()
    if file is not None:
        tasks = importer.from_file(file, count, subset)
    elif url is not None:
        tasks = importer.from_url(url, count, allow_network=allow_network)
    elif allow_network:
        tasks = importer.from_subset(subset, count, allow_network=True)
    else:
        raise typer.BadParameter("--file is required unless --allow-network is explicit")
    svc = services(db, require_key=False)
    _store_benchmark_tasks(svc, tasks)
    emit([t.model_dump() for t in tasks], json_out)


@benchmark_app.command("import-ama")
def benchmark_import_ama(
    count: Annotated[int, typer.Option("--count")] = 5,
    file: Annotated[Path | None, typer.Option("--file")] = None,
    url: Annotated[str | None, typer.Option("--url")] = None,
    allow_network: Annotated[bool, typer.Option("--allow-network")] = False,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    importer = AmaBenchImporter()
    if file is not None:
        tasks = importer.from_file(file, count)
    elif url is not None:
        tasks = importer.from_url(url, count, allow_network=allow_network)
    else:
        raise typer.BadParameter("--file or --url is required for AMA-Bench import")
    svc = services(db, require_key=False)
    _store_benchmark_tasks(svc, tasks)
    emit([t.model_dump() for t in tasks], json_out)


def _store_benchmark_tasks(
    svc: OacsServices, tasks: list[BenchmarkTask], pack: dict[str, object] | None = None
) -> None:
    for task in tasks:
        if pack is not None:
            rubric = dict(task.rubric)
            rubric["task_pack_id"] = pack["id"]
            rubric["task_pack_source"] = pack["source"]
            if pack.get("native_harness") is not None:
                rubric["native_harness"] = pack["native_harness"]
            if pack.get("native_suite") is not None:
                rubric["native_suite"] = pack["native_suite"]
            task = task.model_copy(update={"rubric": rubric})
        now = now_iso()
        svc.store.put_json(
            "benchmark_tasks",
            {
                "id": task.id,
                "task_type": task.type,
                "payload": task.model_dump(),
                "created_at": now,
                "updated_at": now,
                "status": "active",
                "namespace": "default",
                "scope": ["project"],
                "owner_actor_id": None,
                "content_hash": hash_json(task.model_dump()),
            },
        )


@benchmark_app.command("import")
def benchmark_import(file: Path, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    pack = load_task_pack(file)
    tasks = tasks_from_pack(pack)
    _store_benchmark_tasks(services(db, require_key=False), tasks, pack)
    emit([t.model_dump() for t in tasks], json_out)


@benchmark_app.command("download")
def benchmark_download(
    url: str,
    checksum: str,
    output: Annotated[Path, typer.Option("--output")] = Path(".oacs/task-pack.json"),
    allow_network: Annotated[bool, typer.Option("--allow-network")] = False,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    pack = download_task_pack(url, checksum, output, allow_network)
    tasks = tasks_from_pack(pack)
    _store_benchmark_tasks(services(db, require_key=False), tasks, pack)
    emit(
        {
            "url": url,
            "checksum": checksum,
            "downloaded": True,
            "output": str(output),
            "task_pack_id": pack["id"],
            "tasks": len(tasks),
        },
        json_out,
    )


@benchmark_app.command("run")
def benchmark_run(
    mode: Annotated[
        str,
        typer.Option(
            "--mode",
            help=(
                "Benchmark mode. Preferred: oacs_memory_call_loop. "
                "Context Capsule compatibility: oacs_memory_loop."
            ),
        ),
    ],
    model: Annotated[str | None, typer.Option("--model")] = None,
    provider: Annotated[str, typer.Option("--provider")] = "deterministic",
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    rows = svc.store.list("benchmark_tasks", filters={"status": "active"})
    tasks = [BenchmarkTask(**row["payload"]) for row in rows] or SyntheticTaskGenerator().generate(
        "memory_critical", 3
    )
    run = MemoryCriticalBenchmark(svc.memory, svc.loop).run(tasks, mode, actor, model, provider)
    now = now_iso()
    svc.store.put_json(
        "benchmark_runs",
        {
            "id": run.id,
            "mode": run.mode,
            "payload": run.model_dump(),
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "namespace": "default",
            "scope": ["project"],
            "owner_actor_id": actor,
            "content_hash": hash_json(run.model_dump()),
        },
    )
    emit(run.model_dump(), json_out)


@benchmark_app.command("compare")
def benchmark_compare(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    rows = svc.store.list("benchmark_runs", order_by=[("created_at", "asc")])
    baseline, oacs_run = select_comparison_runs(rows)
    emit(compare_runs(baseline, oacs_run), json_out)


@server_app.command("start")
def server_start(host: str = "127.0.0.1", port: int = 8000, db: DbOpt = None) -> None:
    if db:
        import os

        os.environ["OACS_DB"] = db
    uvicorn.run("oacs.api.server:create_app", factory=True, host=host, port=port)


@audit_app.command("tail")
def audit_tail(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db, require_key=False).audit.list()[-20:], json_out)


@audit_app.command("list")
def audit_list(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db, require_key=False).audit.list(), json_out)


@audit_app.command("explain")
def audit_explain(audit_id: str, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    events = [e for e in services(db, require_key=False).audit.list() if e["id"] == audit_id]
    emit(events[0] if events else {"error": "not found"}, json_out)


@audit_app.command("export")
def audit_export(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    audit_list(db, json_out)


@audit_app.command("verify")
def audit_verify(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db, require_key=False).audit.verify_chain(), json_out)


if __name__ == "__main__":
    app()
