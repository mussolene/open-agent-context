from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from rich import print as rprint

from oacs.app import OacsServices, services
from oacs.benchmark.external import AmaBenchImporter, MemoryArenaImporter
from oacs.benchmark.generator import SyntheticTaskGenerator
from oacs.benchmark.models import BenchmarkRun, BenchmarkTask
from oacs.benchmark.reports import compare_runs
from oacs.benchmark.runner import MemoryCriticalBenchmark
from oacs.context.reducer import reduce_capsule
from oacs.core.config import OacsConfig
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.crypto.hybrid_pqc import HybridPQCKeyProvider
from oacs.rules.models import RuleManifest
from oacs.skills.models import SkillManifest
from oacs.tools.local import call_local_tool
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
mcp_app = typer.Typer()
loop_app = typer.Typer()
benchmark_app = typer.Typer()
server_app = typer.Typer()
audit_app = typer.Typer()
capability_app = typer.Typer()

app.add_typer(actor_app, name="actor")
app.add_typer(capability_app, name="capability")
app.add_typer(key_app, name="key")
app.add_typer(memory_app, name="memory")
app.add_typer(context_app, name="context")
app.add_typer(capsule_app, name="capsule")
app.add_typer(rule_app, name="rule")
app.add_typer(skill_app, name="skill")
app.add_typer(tool_app, name="tool")
app.add_typer(mcp_app, name="mcp")
app.add_typer(loop_app, name="loop")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(server_app, name="server")
app.add_typer(audit_app, name="audit")


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


@app.command()
def init(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    svc = services(db, require_key=False)
    emit({"db": str(svc.config.db_path), "status": "initialized"}, json_out)


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
        grants = svc.store.list("capability_grants", "ORDER BY created_at")
    emit(grants, json_out)


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
    svc = services(db)
    mem = svc.memory.propose(type, depth, text, actor, scope or [])
    svc.audit.record("memory.propose", actor, mem.id)
    emit(mem.model_dump(), json_out)


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
    actor: ActorOpt = None,
    scope: ScopeOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    result = svc.memory.query(query, actor, scope or [])
    svc.audit.record("memory.query", actor, None, {"query_hash": hash_json(query)})
    emit([m.model_dump() for m in result], json_out)


@memory_app.command("read")
def memory_read(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    svc = services(db)
    mem = svc.memory.read(memory_id, actor)
    svc.audit.record("memory.read", actor, mem.id)
    emit(mem.model_dump(), json_out)


@memory_app.command("correct")
def memory_correct(
    memory_id: str,
    text: Annotated[str, typer.Option("--text")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    emit(svc.memory.correct(memory_id, text, actor).model_dump(), json_out)


@memory_app.command("deprecate")
def memory_deprecate(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).memory.deprecate(memory_id, actor).model_dump(), json_out)


@memory_app.command("supersede")
def memory_supersede(
    memory_id: str,
    replacement_id: str,
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(services(db).memory.supersede(memory_id, replacement_id, actor).model_dump(), json_out)


@memory_app.command("forget")
def memory_forget(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).memory.forget(memory_id, actor).model_dump(), json_out)


@memory_app.command("blur")
def memory_blur(
    memory_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).memory.blur(memory_id, actor).model_dump(), json_out)


@memory_app.command("sharpen")
def memory_sharpen(
    memory_id: str,
    evidence_ref: Annotated[str, typer.Option("--evidence")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(services(db).memory.sharpen(memory_id, evidence_ref, actor).model_dump(), json_out)


@memory_app.command("audit")
def memory_audit(db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db, require_key=False).audit.list(), json_out)


@memory_app.command("export")
def memory_export(actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(services(db).memory.export_all(actor), json_out)


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
    emit([m.model_dump() for m in imported], json_out)


@context_app.command("build")
def context_build(
    intent: Annotated[str, typer.Option("--intent")],
    actor: ActorOpt = None,
    agent: AgentOpt = None,
    scope: ScopeOpt = None,
    budget: Annotated[int, typer.Option("--budget")] = 4000,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(
        services(db).context.build(intent, actor, agent, scope or [], budget).model_dump(), json_out
    )


@context_app.command("explain")
def context_explain(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.explain(capsule_id, actor), json_out)


@context_app.command("reduce")
def context_reduce(
    capsule_id: str,
    max_memories: Annotated[int, typer.Option("--max-memories")] = 5,
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    emit(reduce_capsule(svc.context.read(capsule_id, actor), max_memories).model_dump(), json_out)


@context_app.command("expand")
def context_expand(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.read(capsule_id, actor).model_dump(), json_out)


@context_app.command("lock")
def context_lock(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.set_status(capsule_id, actor, "locked"), json_out)


@context_app.command("export")
def context_export(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    emit(services(db).context.read(capsule_id, actor).model_dump(), json_out)


@context_app.command("import")
def context_import(
    file: Annotated[Path, typer.Option("--file")],
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    capsule = services(db).context.import_capsule(
        json.loads(file.read_text(encoding="utf-8")), actor
    )
    emit(capsule.model_dump(), json_out)


@context_app.command("validate")
def context_validate(
    file: Annotated[Path, typer.Option("--file")],
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    result = services(db, require_key=False).context.validate_payload(
        json.loads(file.read_text(encoding="utf-8"))
    )
    emit(result, json_out)


@capsule_app.command("create")
def capsule_create(
    intent: Annotated[str, typer.Option("--intent")] = "manual",
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    context_build(intent, actor, None, [], 4000, db, json_out)


@capsule_app.command("inspect")
def capsule_inspect(
    capsule_id: str, actor: ActorOpt = None, db: DbOpt = None, json_out: JsonOpt = False
) -> None:
    context_export(capsule_id, actor, db, json_out)


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
        "capability_grants", "WHERE subject_actor_id=? AND status='active'", (subject,)
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
def skill_run(skill_id: str, json_out: JsonOpt = False) -> None:
    from oacs.skills.runner import run_builtin_skill

    emit(run_builtin_skill(skill_id, {}), json_out)


@tool_app.command("add")
def tool_add(
    name: Annotated[str, typer.Option("--name")],
    type: Annotated[str, typer.Option("--type")] = "python_function",
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(
        services(db, require_key=False).tools.add(ToolBinding(name=name, type=type)).model_dump(),
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
def tool_call(name: str, json_out: JsonOpt = False) -> None:
    emit(call_local_tool(name, {"called": True}), json_out)


@mcp_app.command("import")
def mcp_import(file: Path, db: DbOpt = None, json_out: JsonOpt = False) -> None:
    emit(
        [m.model_dump() for m in services(db, require_key=False).mcp.import_config(str(file))],
        json_out,
    )


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
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    emit(services(db).loop.run(request, actor, agent, scope or []).model_dump(), json_out)


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
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    importer = MemoryArenaImporter()
    if file is not None:
        tasks = importer.from_file(file, count, subset)
    elif url is not None:
        tasks = importer.from_url(url, count)
    else:
        tasks = importer.from_subset(subset, count)
    svc = services(db, require_key=False)
    _store_benchmark_tasks(svc, tasks)
    emit([t.model_dump() for t in tasks], json_out)


@benchmark_app.command("import-ama")
def benchmark_import_ama(
    count: Annotated[int, typer.Option("--count")] = 5,
    file: Annotated[Path | None, typer.Option("--file")] = None,
    url: Annotated[str | None, typer.Option("--url")] = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    importer = AmaBenchImporter()
    if file is not None:
        tasks = importer.from_file(file, count)
    elif url is not None:
        tasks = importer.from_url(url, count)
    else:
        raise typer.BadParameter("--file or --url is required for AMA-Bench import")
    svc = services(db, require_key=False)
    _store_benchmark_tasks(svc, tasks)
    emit([t.model_dump() for t in tasks], json_out)


def _store_benchmark_tasks(svc: OacsServices, tasks: list[BenchmarkTask]) -> None:
    for task in tasks:
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
    tasks = [BenchmarkTask(**item) for item in json.loads(file.read_text(encoding="utf-8"))]
    _store_benchmark_tasks(services(db, require_key=False), tasks)
    emit([t.model_dump() for t in tasks], json_out)


@benchmark_app.command("download")
def benchmark_download(url: str, checksum: str, json_out: JsonOpt = False) -> None:
    emit(
        {
            "url": url,
            "checksum": checksum,
            "downloaded": False,
            "reason": (
                "explicit downloader validates packs; network disabled in default POC command"
            ),
        },
        json_out,
    )


@benchmark_app.command("run")
def benchmark_run(
    mode: Annotated[str, typer.Option("--mode")],
    model: Annotated[str | None, typer.Option("--model")] = None,
    provider: Annotated[str, typer.Option("--provider")] = "deterministic",
    actor: ActorOpt = None,
    db: DbOpt = None,
    json_out: JsonOpt = False,
) -> None:
    svc = services(db)
    rows = svc.store.list("benchmark_tasks", "WHERE status='active'")
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
    rows = svc.store.list("benchmark_runs", "ORDER BY created_at")
    baseline = next(
        (BenchmarkRun(**r["payload"]) for r in rows if r["mode"] == "baseline_no_memory"),
        BenchmarkRun(mode="baseline_no_memory", task_results=[], summary={"average_score": 0}),
    )
    oacs_run = next(
        (BenchmarkRun(**r["payload"]) for r in rows if r["mode"] == "oacs_memory_loop"),
        BenchmarkRun(mode="oacs_memory_loop", task_results=[], summary={"average_score": 0}),
    )
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
