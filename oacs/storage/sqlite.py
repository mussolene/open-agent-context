from __future__ import annotations

import sqlite3
from contextlib import closing, suppress
from pathlib import Path
from typing import Any

from oacs.core.json import dumps, loads


class SQLiteStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init(self) -> None:
        with closing(self.connect()) as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def put_json(self, table: str, record: dict[str, Any]) -> None:
        cols = list(record)
        placeholders = ",".join("?" for _ in cols)
        updates = ",".join(f"{col}=excluded.{col}" for col in cols if col != "id")
        sql = (
            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders}) "
            f"ON CONFLICT(id) DO UPDATE SET {updates}"
        )
        values = [dumps(v) if isinstance(v, (dict, list)) else v for v in record.values()]
        with closing(self.connect()) as conn:
            conn.execute(sql, values)
            conn.commit()

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        with closing(self.connect()) as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (record_id,)).fetchone()
        return normalize_row(row) if row else None

    def list(
        self, table: str, where: str = "", params: tuple[Any, ...] = ()
    ) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM {table} {where}"
        with closing(self.connect()) as conn:
            rows = conn.execute(sql, params).fetchall()
        return [normalize_row(row) for row in rows]

    def delete(self, table: str, record_id: str) -> None:
        with closing(self.connect()) as conn:
            conn.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
            conn.commit()


def normalize_row(row: sqlite3.Row) -> dict[str, Any]:
    out = dict(row)
    for key, value in list(out.items()):
        if isinstance(value, str) and value[:1] in ("{", "["):
            with suppress(Exception):
                out[key] = loads(value)
    return out


SCHEMA = """
CREATE TABLE IF NOT EXISTS actors (
  id TEXT PRIMARY KEY, type TEXT NOT NULL, name TEXT NOT NULL,
  public_key_ref TEXT, trust_level INTEGER NOT NULL DEFAULT 0,
  owner_actor_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL DEFAULT 'default',
  scope TEXT NOT NULL DEFAULT '[]', content_hash TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS agents (
  id TEXT PRIMARY KEY, actor_id TEXT, name TEXT NOT NULL, created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL, status TEXT NOT NULL, namespace TEXT NOT NULL DEFAULT 'default',
  scope TEXT NOT NULL DEFAULT '[]', content_hash TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS capability_grants (
  id TEXT PRIMARY KEY, subject_actor_id TEXT NOT NULL, issuer_actor_id TEXT NOT NULL,
  scope TEXT NOT NULL, allowed_operations TEXT NOT NULL, denied_operations TEXT NOT NULL,
  memory_depth_allowed INTEGER NOT NULL DEFAULT 2, namespaces_allowed TEXT NOT NULL,
  tools_allowed TEXT NOT NULL, skills_allowed TEXT NOT NULL, expires_at TEXT,
  signature TEXT, status TEXT NOT NULL, namespace TEXT NOT NULL DEFAULT 'default',
  owner_actor_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS capability_definitions (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, operation TEXT NOT NULL,
  description TEXT NOT NULL, definition TEXT NOT NULL, status TEXT NOT NULL,
  namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memory_records (
  id TEXT PRIMARY KEY, memory_type TEXT NOT NULL, depth INTEGER NOT NULL,
  lifecycle_status TEXT NOT NULL, status TEXT NOT NULL, namespace TEXT NOT NULL,
  scope TEXT NOT NULL, owner_actor_id TEXT, content_ciphertext BLOB NOT NULL,
  content_nonce BLOB NOT NULL, content_aad TEXT NOT NULL, content_hash TEXT NOT NULL,
  evidence_refs TEXT NOT NULL, supersedes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memory_embeddings (
  id TEXT PRIMARY KEY, memory_id TEXT NOT NULL, provider TEXT NOT NULL,
  vector_json TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL,
  owner_actor_id TEXT, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS context_capsules (
  id TEXT PRIMARY KEY, purpose TEXT NOT NULL, task_id TEXT, actor_id TEXT, agent_id TEXT,
  scope TEXT NOT NULL, token_budget INTEGER NOT NULL, payload_ciphertext BLOB NOT NULL,
  payload_nonce BLOB NOT NULL, payload_aad TEXT NOT NULL, checksum TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS rules (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, rule_kind TEXT NOT NULL, content TEXT NOT NULL,
  applies_to TEXT NOT NULL, enforcement_mode TEXT NOT NULL, blocking INTEGER NOT NULL,
  priority INTEGER NOT NULL, evidence_refs TEXT NOT NULL, status TEXT NOT NULL,
  namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skills (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT NOT NULL, manifest TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tools (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL, manifest TEXT NOT NULL,
  risk_level TEXT NOT NULL, status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL,
  owner_actor_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mcp_bindings (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, server_name TEXT NOT NULL, transport TEXT NOT NULL,
  manifest TEXT NOT NULL, risk_level TEXT NOT NULL, status TEXT NOT NULL,
  namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence_refs (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, uri TEXT NOT NULL, public_payload TEXT,
  sensitive_ciphertext BLOB, sensitive_nonce BLOB, content_hash TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
  id TEXT PRIMARY KEY, operation TEXT NOT NULL, actor_id TEXT, target_id TEXT,
  metadata TEXT NOT NULL, previous_hash TEXT, content_hash TEXT NOT NULL,
  created_at TEXT NOT NULL, status TEXT NOT NULL, namespace TEXT NOT NULL,
  scope TEXT NOT NULL, owner_actor_id TEXT
);
CREATE TABLE IF NOT EXISTS task_traces (
  id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL,
  owner_actor_id TEXT, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS experience_traces (
  id TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  status TEXT NOT NULL, namespace TEXT NOT NULL, scope TEXT NOT NULL,
  owner_actor_id TEXT, content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS benchmark_tasks (
  id TEXT PRIMARY KEY, task_type TEXT NOT NULL, payload TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, status TEXT NOT NULL,
  namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  content_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS benchmark_runs (
  id TEXT PRIMARY KEY, mode TEXT NOT NULL, payload TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL, status TEXT NOT NULL,
  namespace TEXT NOT NULL, scope TEXT NOT NULL, owner_actor_id TEXT,
  content_hash TEXT NOT NULL
);
"""
