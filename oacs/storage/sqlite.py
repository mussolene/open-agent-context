from __future__ import annotations

import sqlite3
from contextlib import closing, suppress
from pathlib import Path
from typing import Any

from oacs.core.json import dumps, loads
from oacs.storage.backend import OrderBy

_ALLOWED_TABLES = {
    "actors",
    "agents",
    "capability_grants",
    "capability_definitions",
    "memory_records",
    "memory_embeddings",
    "context_capsules",
    "rules",
    "skills",
    "tools",
    "mcp_bindings",
    "evidence_refs",
    "audit_events",
    "task_traces",
    "experience_traces",
    "benchmark_tasks",
    "benchmark_runs",
    "key_metadata",
}


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
        _validate_identifier(table, _ALLOWED_TABLES, "table")
        cols = list(record)
        for col in cols:
            _validate_identifier(col, set(cols), "column")
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
        _validate_identifier(table, _ALLOWED_TABLES, "table")
        with closing(self.connect()) as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE id=?", (record_id,)).fetchone()
        return normalize_row(row) if row else None

    def list(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        _validate_identifier(table, _ALLOWED_TABLES, "table")
        filters = filters or {}
        clauses: list[str] = []
        values: list[Any] = []
        for column, value in filters.items():
            _validate_identifier(column, None, "column")
            clauses.append(f"{column}=?")
            values.append(dumps(value) if isinstance(value, (dict, list)) else value)
        sql = f"SELECT * FROM {table}"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        if order_by:
            order_parts: list[str] = []
            for column, direction in order_by:
                _validate_identifier(column, None, "column")
                sql_direction = "DESC" if direction == "desc" else "ASC"
                order_parts.append(f"{column} {sql_direction}")
            sql += " ORDER BY " + ", ".join(order_parts)
        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            sql += " LIMIT ?"
            values.append(limit)
        with closing(self.connect()) as conn:
            rows = conn.execute(sql, tuple(values)).fetchall()
        return [normalize_row(row) for row in rows]

    def delete(self, table: str, record_id: str) -> None:
        _validate_identifier(table, _ALLOWED_TABLES, "table")
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


def _validate_identifier(
    value: str, allowed: set[str] | None = None, label: str = "identifier"
) -> None:
    if not value.replace("_", "").isalnum() or not value[:1].isalpha():
        raise ValueError(f"invalid {label}: {value}")
    if allowed is not None and value not in allowed:
        raise ValueError(f"unknown {label}: {value}")


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
