from __future__ import annotations

from dataclasses import dataclass

from oacs.audit import AuditService
from oacs.context.builder import ContextBuilder
from oacs.core.config import OacsConfig
from oacs.crypto.local_passphrase import LocalPassphraseKeyProvider
from oacs.crypto.payload_codec import EncryptionMode, PayloadCodec
from oacs.evidence import EvidenceService
from oacs.identity.actors import ActorService
from oacs.identity.capabilities import CapabilityService
from oacs.identity.policy import PolicyEngine
from oacs.loop.engine import MemoryLoopEngine
from oacs.memory.service import MemoryService
from oacs.rules.engine import RuleEngine
from oacs.skills.registry import SkillRegistry
from oacs.storage.backend import StorageBackend
from oacs.storage.repositories import Repository
from oacs.storage.sqlite import SQLiteStore
from oacs.tools.mcp import McpRegistry
from oacs.tools.registry import ToolRegistry
from oacs.tools.runner import ToolRunner


@dataclass
class OacsServices:
    config: OacsConfig
    store: StorageBackend
    key_provider: LocalPassphraseKeyProvider
    actors: ActorService
    capabilities: CapabilityService
    policy: PolicyEngine
    memory: MemoryService
    rules: RuleEngine
    skills: SkillRegistry
    tools: ToolRegistry
    mcp: McpRegistry
    evidence: EvidenceService
    tool_runner: ToolRunner
    context: ContextBuilder
    loop: MemoryLoopEngine
    audit: AuditService
    encryption_mode: EncryptionMode


def services(
    db: str | None = None, passphrase: str | None = None, require_key: bool = True
) -> OacsServices:
    config = OacsConfig.from_values(db, passphrase)
    store = SQLiteStore(config.db_path)
    store.init()
    key_provider = LocalPassphraseKeyProvider(config.key_file, config.unlocked_file)
    encryption_mode = _resolve_encryption_mode(config, store)
    master_key: bytes | None = None
    if require_key:
        if config.passphrase and not config.unlocked_file.exists():
            master_key = key_provider.unwrap_key(config.passphrase)
        else:
            master_key = key_provider.load_unlocked()
    codec = PayloadCodec(encryption_mode, master_key)
    capabilities = CapabilityService(
        Repository(store, "capability_grants"),
        Repository(store, "capability_definitions"),
    )
    audit = AuditService(Repository(store, "audit_events"))
    policy = PolicyEngine(capabilities, audit)
    memory = MemoryService(Repository(store, "memory_records"), policy, codec)
    rules = RuleEngine(Repository(store, "rules"))
    skills = SkillRegistry(Repository(store, "skills"))
    tools = ToolRegistry(Repository(store, "tools"))
    mcp = McpRegistry(Repository(store, "mcp_bindings"), tools)
    evidence = EvidenceService(Repository(store, "evidence_refs"), policy, audit)
    tool_runner = ToolRunner(
        tools,
        mcp,
        policy,
        audit,
        evidence,
    )
    context = ContextBuilder(
        Repository(store, "context_capsules"),
        memory,
        rules,
        skills,
        tools,
        policy,
        codec,
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
        evidence=evidence,
        tool_runner=tool_runner,
        context=context,
        loop=MemoryLoopEngine(memory, context),
        audit=audit,
        encryption_mode=encryption_mode,
    )


def _resolve_encryption_mode(config: OacsConfig, store: SQLiteStore) -> EncryptionMode:
    requested = _normalize_encryption_mode(config.encryption)
    if requested:
        store.set_metadata("encryption_mode", requested)
        return requested
    stored = _normalize_encryption_mode(store.get_metadata("encryption_mode"))
    if stored:
        return stored
    if config.key_file.exists():
        return _provider_mode(config) or "local_passphrase"
    return "local_unlocked"


def _normalize_encryption_mode(value: str | None) -> EncryptionMode | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("-", "_")
    if normalized in {"local_unlocked", "unlocked", "dev"}:
        return "local_unlocked"
    if normalized in {"local_passphrase", "passphrase", "encrypted"}:
        return "local_passphrase"
    raise ValueError(f"unsupported OACS_ENCRYPTION mode: {value}")


def _provider_mode(config: OacsConfig) -> EncryptionMode | None:
    import json

    try:
        metadata = json.loads(config.key_file.read_text(encoding="utf-8"))
    except Exception:
        return None
    provider = metadata.get("provider")
    if provider == "local_unlocked":
        return "local_unlocked"
    if provider == "local_passphrase":
        return "local_passphrase"
    return None
