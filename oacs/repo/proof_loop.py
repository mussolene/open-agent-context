from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from oacs.app import OacsServices
from oacs.core.json import hash_json
from oacs.memory.models import EvidenceItem

ProofLoopPhase = Literal["spec", "build", "evidence", "verify", "fix", "status"]


class RepoProofCaptureRequest(BaseModel):
    task_id: str
    phase: ProofLoopPhase
    summary: str
    actor_id: str | None = None
    cwd: Path = Path(".")
    scope: list[str] = Field(default_factory=list)
    artifacts: list[Path] = Field(default_factory=list)


class RepoProofContextRequest(BaseModel):
    task_id: str
    intent: str = "continue repo proof-loop task"
    actor_id: str | None = None
    agent_id: str | None = None
    cwd: Path = Path(".")
    scope: list[str] = Field(default_factory=list)
    token_budget: int = 4000


class RepoProofStatusRequest(BaseModel):
    task_id: str
    actor_id: str | None = None
    cwd: Path = Path(".")
    scope: list[str] = Field(default_factory=list)


class RepoProofLoopAdapter:
    def __init__(self, services: OacsServices):
        self.services = services

    def capture(self, request: RepoProofCaptureRequest) -> dict[str, object]:
        scope = self._task_scope(request.cwd, request.task_id, request.scope)
        state = repo_state(request.cwd)
        artifacts = [self._artifact_ref(request.cwd, artifact) for artifact in request.artifacts]
        text = "\n".join(
            [
                f"Repo proof-loop task: {request.task_id}",
                f"Phase: {request.phase}",
                f"Summary: {request.summary}",
                f"Git branch: {state['branch']}",
                f"Git commit: {state['commit']}",
                f"Dirty worktree: {state['dirty']}",
            ]
        )
        evidence: list[EvidenceItem | dict[str, object]] = [
            EvidenceItem(
                evidence_kind="repo_proof_loop_phase",
                claim=f"Proof-loop {request.phase} phase summary",
                value=request.summary,
                source_ref=f"git:{state['commit']}",
                confidence=1.0,
                scope=scope,
                slot=request.phase,
            )
        ]
        for artifact in artifacts:
            evidence.append(
                EvidenceItem(
                    evidence_kind="repo_proof_loop_artifact",
                    claim=f"Proof-loop artifact for {request.task_id}",
                    value=str(artifact["path"]),
                    source_ref=str(artifact["path"]),
                    confidence=1.0 if artifact["exists"] else 0.0,
                    scope=scope,
                    slot="artifact",
                )
            )
        proposed = self.services.memory.propose(
            "episode",
            1,
            text,
            request.actor_id,
            scope,
            evidence=evidence,
        )
        committed = self.services.memory.commit(proposed.id, request.actor_id)
        self.services.audit.record(
            "repo.proof_capture",
            request.actor_id,
            committed.id,
            {
                "task_id": request.task_id,
                "phase": request.phase,
                "task_hash": hash_json(request.task_id),
            },
        )
        return {
            "task_id": request.task_id,
            "phase": request.phase,
            "memory_id": committed.id,
            "scope": scope,
            "git": state,
            "artifacts": artifacts,
            "status": committed.lifecycle_status,
        }

    def context(self, request: RepoProofContextRequest) -> dict[str, object]:
        scope = self._task_scope(request.cwd, request.task_id, request.scope)
        capsule = self.services.context.build(
            request.intent,
            request.actor_id,
            request.agent_id,
            scope,
            request.token_budget,
            task_id=request.task_id,
        )
        self.services.audit.record(
            "repo.proof_context",
            request.actor_id,
            capsule.id,
            {"task_id": request.task_id, "memory_count": len(capsule.included_memories)},
        )
        return {
            "task_id": request.task_id,
            "scope": scope,
            "capsule": capsule.model_dump(),
            "explain": self.services.context.explain(capsule.id, request.actor_id),
        }

    def status(self, request: RepoProofStatusRequest) -> dict[str, object]:
        scope = self._task_scope(request.cwd, request.task_id, request.scope)
        task_dir = repo_root(request.cwd) / ".agent" / "tasks" / request.task_id
        artifacts = {
            "spec": self._artifact_summary(task_dir / "spec.md"),
            "evidence": self._json_artifact_summary(task_dir / "evidence.json"),
            "verdict": self._json_artifact_summary(task_dir / "verdict.json"),
            "problems": self._artifact_summary(task_dir / "problems.md"),
        }
        memories = self.services.memory.query(
            f"Repo proof-loop task: {request.task_id}",
            request.actor_id,
            scope,
        )
        capsules = self.services.store.list(
            "context_capsules",
            "WHERE task_id=? AND status='active' ORDER BY created_at DESC",
            (request.task_id,),
        )
        return {
            "task_id": request.task_id,
            "scope": scope,
            "task_dir_exists": task_dir.exists(),
            "artifacts": artifacts,
            "memory_ids": [memory.id for memory in memories],
            "capsule_ids": [str(capsule["id"]) for capsule in capsules],
        }

    def _task_scope(self, cwd: Path, task_id: str, extra_scope: list[str]) -> list[str]:
        return [*repo_scope(cwd), f"task:{task_id}", *extra_scope]

    def _artifact_ref(self, cwd: Path, artifact: Path) -> dict[str, object]:
        path = artifact if artifact.is_absolute() else cwd / artifact
        return {
            "path": str(artifact),
            "exists": path.exists(),
            "sha256": hash_json(path.read_bytes().hex()) if path.is_file() else None,
        }

    def _artifact_summary(self, path: Path) -> dict[str, object]:
        return {
            "path": str(path),
            "exists": path.exists(),
            "sha256": hash_json(path.read_bytes().hex()) if path.is_file() else None,
            "bytes": path.stat().st_size if path.is_file() else 0,
        }

    def _json_artifact_summary(self, path: Path) -> dict[str, object]:
        summary = self._artifact_summary(path)
        if path.is_file():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = None
            summary["json"] = payload
        return summary


def repo_scope(cwd: Path) -> list[str]:
    root = git_value(["rev-parse", "--show-toplevel"], cwd)
    repo_name = Path(root).name if root else cwd.resolve().name
    return [f"repo:{repo_name}"]


def repo_root(cwd: Path) -> Path:
    root = git_value(["rev-parse", "--show-toplevel"], cwd)
    return Path(root) if root else cwd.resolve()


def repo_state(cwd: Path) -> dict[str, object]:
    changed = (git_value(["status", "--short"], cwd) or "").splitlines()
    return {
        "branch": git_value(["branch", "--show-current"], cwd) or "unknown",
        "commit": git_value(["rev-parse", "--short", "HEAD"], cwd) or "unknown",
        "dirty": bool(changed),
        "changed_files": changed[:50],
    }


def git_value(args: list[str], cwd: Path | None = None) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None
