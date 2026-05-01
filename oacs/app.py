from __future__ import annotations

from dataclasses import dataclass

from oacs.audit import AuditService
from oacs.context.builder import ContextBuilder
from oacs.core.config import OacsConfig
from oacs.crypto.local_passphrase import LocalPassphraseKeyProvider
from oacs.identity.actors import ActorService
from oacs.identity.capabilities import CapabilityService
from oacs.identity.policy import PolicyEngine
from oacs.loop.engine import MemoryLoopEngine
from oacs.memory.service import MemoryService
from oacs.rules.engine import RuleEngine
from oacs.skills.registry import SkillRegistry
from oacs.storage.repositories import Repository
from oacs.storage.sqlite import SQLiteStore
from oacs.tools.mcp import McpRegistry
from oacs.tools.registry import ToolRegistry


@dataclass
class OacsServices:
    config: OacsConfig
    store: SQLiteStore
    key_provider: LocalPassphraseKeyProvider
    actors: ActorService
    capabilities: CapabilityService
    policy: PolicyEngine
    memory: MemoryService
    rules: RuleEngine
    skills: SkillRegistry
    tools: ToolRegistry
    mcp: McpRegistry
    context: ContextBuilder
    loop: MemoryLoopEngine
    audit: AuditService


def services(
    db: str | None = None, passphrase: str | None = None, require_key: bool = True
) -> OacsServices:
    config = OacsConfig.from_values(db, passphrase)
    store = SQLiteStore(config.db_path)
    store.init()
    key_provider = LocalPassphraseKeyProvider(config.key_file, config.unlocked_file)
    if require_key:
        if config.passphrase and not config.unlocked_file.exists():
            master_key = key_provider.unwrap_key(config.passphrase)
        else:
            master_key = key_provider.load_unlocked()
    else:
        master_key = b"\x00" * 32
    capabilities = CapabilityService(
        Repository(store, "capability_grants"),
        Repository(store, "capability_definitions"),
    )
    policy = PolicyEngine(capabilities)
    memory = MemoryService(Repository(store, "memory_records"), policy, master_key)
    rules = RuleEngine(Repository(store, "rules"))
    skills = SkillRegistry(Repository(store, "skills"))
    tools = ToolRegistry(Repository(store, "tools"))
    mcp = McpRegistry(Repository(store, "mcp_bindings"), tools)
    context = ContextBuilder(
        Repository(store, "context_capsules"),
        memory,
        rules,
        skills,
        tools,
        policy,
        master_key,
    )
    return OacsServices(
        config=config,
        store=store,
        key_provider=key_provider,
        actors=ActorService(Repository(store, "actors")),
        capabilities=capabilities,
        policy=policy,
        memory=memory,
        rules=rules,
        skills=skills,
        tools=tools,
        mcp=mcp,
        context=context,
        loop=MemoryLoopEngine(memory, context),
        audit=AuditService(Repository(store, "audit_events")),
    )
